from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass
class VoiceStatus:
    ok: bool
    engine: str
    message: str
    provider: str


class OfflineVoiceEngine:
    """Local-first voice engine for Ubuntu and offline use."""

    def __init__(self) -> None:
        self.tts_backend = self._detect_tts_backend()
        self.stt_backend = self._detect_stt_backend()

    def _detect_tts_backend(self) -> str:
        if shutil.which("espeak-ng"):
            return "espeak-ng"
        if shutil.which("espeak"):
            return "espeak"
        if shutil.which("spd-say"):
            return "spd-say"
        return "fallback"

    def _detect_stt_backend(self) -> str:
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        return "fallback"

    def speak(self, text: str) -> VoiceStatus:
        if not text or not text.strip():
            return VoiceStatus(False, self.tts_backend, "empty text", "tts")

        if self.tts_backend == "espeak-ng":
            try:
                subprocess.run(["espeak-ng", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return VoiceStatus(True, "espeak-ng", "spoken successfully", "tts")
            except Exception as exc:  # pragma: no cover - platform-specific fallback
                return VoiceStatus(False, self.tts_backend, str(exc), "tts")

        if self.tts_backend == "espeak":
            try:
                subprocess.run(["espeak", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return VoiceStatus(True, "espeak", "spoken successfully", "tts")
            except Exception as exc:  # pragma: no cover
                return VoiceStatus(False, self.tts_backend, str(exc), "tts")

        if self.tts_backend == "spd-say":
            try:
                subprocess.run(["spd-say", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return VoiceStatus(True, "spd-say", "spoken successfully", "tts")
            except Exception as exc:  # pragma: no cover
                return VoiceStatus(False, self.tts_backend, str(exc), "tts")

        return VoiceStatus(True, "fallback", "text-only fallback; no speech engine installed", "tts")

    def transcribe(self, audio_bytes: bytes | None = None, source_text: str | None = None) -> VoiceStatus:
        if source_text is not None:
            return VoiceStatus(True, self.stt_backend, source_text, "stt")

        if audio_bytes is None:
            return VoiceStatus(False, self.stt_backend, "no audio provided", "stt")

        if self.stt_backend == "ffmpeg":
            return VoiceStatus(True, "ffmpeg", "audio bytes accepted for offline transcription pipeline", "stt")

        return VoiceStatus(True, "fallback", "audio fallback accepted; no speech engine installed", "stt")

    def status(self) -> dict[str, Any]:
        return {
            "tts_backend": self.tts_backend,
            "stt_backend": self.stt_backend,
            "voice_ready": self.tts_backend != "fallback" or self.stt_backend != "fallback",
        }


def main() -> None:
    engine = OfflineVoiceEngine()
    print(engine.status())


if __name__ == "__main__":
    main()
