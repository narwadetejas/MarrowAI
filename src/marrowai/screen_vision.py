from __future__ import annotations

import os
from pathlib import Path
import tempfile
import time
from typing import Any, NamedTuple


class ScreenElement(NamedTuple):
    text: str
    confidence: float
    box: list[list[float]]
    center_x: int
    center_y: int
    width: int
    height: int


class ScreenVisionEngine:
    """High-accuracy screen perception and visual grounding engine for MarrowAI.
    
    Provides:
    - Multi-monitor full-screen capture
    - Fast OCR via RapidOCR (ONNX runtime)
    - Visual target localization (finding text, buttons, links with (x, y) coordinates)
    - Full screen description and text extraction
    """

    def __init__(self, debug_dir: str | None = None) -> None:
        self.debug_dir = Path(debug_dir) if debug_dir else Path("/tmp/marrowai_vision")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        self._ocr_engine: Any = None
        self._has_mss: bool | None = None
        self._has_rapidocr: bool | None = None

    def _get_ocr_engine(self) -> Any:
        if self._ocr_engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._ocr_engine = RapidOCR()
                self._has_rapidocr = True
            except Exception:
                self._has_rapidocr = False
                self._ocr_engine = None
        return self._ocr_engine

    def capture_screen(self, monitor_index: int = 0, output_path: str | None = None) -> dict[str, Any]:
        """Captures the screen and saves it or returns pixel dimensions."""
        file_path = output_path or str(self.debug_dir / f"screen_{int(time.time() * 1000)}.png")

        # 1. Try mss (fastest and multi-monitor capable)
        try:
            import mss
            import mss.tools
            sct_cls = getattr(mss, "MSS", mss.mss)
            with sct_cls() as sct:
                if monitor_index < len(sct.monitors):
                    mon = sct.monitors[monitor_index]
                else:
                    mon = sct.monitors[0]
                shot = sct.grab(mon)
                mss.tools.to_png(shot.rgb, shot.size, output=file_path)
                return {
                    "status": "success",
                    "path": file_path,
                    "width": mon["width"],
                    "height": mon["height"],
                    "left": mon.get("left", 0),
                    "top": mon.get("top", 0),
                    "monitor_index": monitor_index,
                }
        except Exception:
            pass

        # 2. Try PIL ImageGrab
        try:
            from PIL import ImageGrab
            im = ImageGrab.grab()
            im.save(file_path)
            w, h = im.size
            return {
                "status": "success",
                "path": file_path,
                "width": w,
                "height": h,
                "left": 0,
                "top": 0,
                "monitor_index": monitor_index,
            }
        except Exception:
            pass

        # 3. Fallback: CLI tools (xwd / ffmpeg)
        try:
            import subprocess
            display = os.environ.get("DISPLAY", ":1")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "x11grab", "-video_size", "1920x1080", "-i", display, "-vframes", "1", file_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            if os.path.exists(file_path):
                return {
                    "status": "success",
                    "path": file_path,
                    "width": 1920,
                    "height": 1080,
                    "left": 0,
                    "top": 0,
                    "monitor_index": monitor_index,
                }
        except Exception:
            pass

        return {"status": "failed", "error": "No available screen capture backend (mss, PIL, ffmpeg failed)"}

    def read_screen(self, monitor_index: int = 0) -> list[ScreenElement]:
        """Captures the screen and performs OCR to extract all visible text elements with exact coordinates."""
        cap = self.capture_screen(monitor_index=monitor_index)
        if cap.get("status") != "success":
            return []

        file_path = cap["path"]
        elements: list[ScreenElement] = []

        engine = self._get_ocr_engine()
        if engine is None:
            # If RapidOCR is not available, return empty list
            return []

        try:
            result, _ = engine(file_path)
            if not result:
                return []

            offset_x = cap.get("left", 0)
            offset_y = cap.get("top", 0)

            for item in result:
                box, text, score = item
                # box is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                xs = [p[0] for p in box]
                ys = [p[1] for p in box]
                cx = int(sum(xs) / len(xs)) + offset_x
                cy = int(sum(ys) / len(ys)) + offset_y
                w = int(max(xs) - min(xs))
                h = int(max(ys) - min(ys))

                elements.append(
                    ScreenElement(
                        text=str(text).strip(),
                        confidence=float(score),
                        box=box,
                        center_x=cx,
                        center_y=cy,
                        width=w,
                        height=h,
                    )
                )
        except Exception:
            return []

        return elements

    def find_text_on_screen(
        self,
        query: str,
        fuzzy: bool = True,
        min_confidence: float = 0.4,
    ) -> list[ScreenElement]:
        """Locates specific text on screen and returns matching elements sorted by relevance."""
        elements = self.read_screen()
        matches: list[tuple[float, ScreenElement]] = []
        q_lower = query.strip().lower()

        for el in elements:
            if el.confidence < min_confidence:
                continue
            text_lower = el.text.lower()

            # Exact match
            if text_lower == q_lower:
                matches.append((2.0, el))
            # Substring match
            elif q_lower in text_lower:
                ratio = len(q_lower) / max(1, len(text_lower))
                matches.append((1.0 + ratio, el))
            # Fuzzy match (all query words present)
            elif fuzzy and all(word in text_lower for word in q_lower.split() if len(word) > 2):
                matches.append((0.8, el))

        matches.sort(key=lambda m: m[0], reverse=True)
        return [m[1] for m in matches]

    def describe_screen(self) -> str:
        """Returns a concise, structured textual summary of everything visible on screen."""
        elements = self.read_screen()
        if not elements:
            return "Screen observation: Unable to detect text or screen capture returned empty."

        lines = [f"Screen Observation ({len(elements)} elements detected):"]
        # Group elements top-to-bottom
        sorted_elements = sorted(elements, key=lambda el: (el.center_y // 40, el.center_x))
        for el in sorted_elements[:40]:
            lines.append(f"- \"{el.text}\" at ({el.center_x}, {el.center_y}) [confidence: {el.confidence:.2f}]")

        if len(sorted_elements) > 40:
            lines.append(f"... and {len(sorted_elements) - 40} additional elements.")

        return "\n".join(lines)
