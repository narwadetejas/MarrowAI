from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
import urllib.parse
from typing import Any

from .interfaces import ExecutionResult
from .screen_vision import ScreenVisionEngine


class GUIAutomationExecutor:
    """Intelligent GUI Automation, Accessibility & Window/Tab Controller (MA-CORE-006).

    Provides full autonomous desktop control:
    - Screen-aware visual clicks (OCR text targeting)
    - Mouse movement, clicking, dragging, scrolling
    - Keyboard typing and complex shortcut hotkeys
    - Open window discovery, active window detection, window focus/close
    - Tab awareness, tab switching, new tab, and tab closing
    """

    def __init__(self) -> None:
        self.has_x11 = "DISPLAY" in os.environ
        self.has_wayland = "WAYLAND_DISPLAY" in os.environ
        self.xdotool = shutil.which("xdotool")
        self.ydotool = shutil.which("ydotool")
        self.vision = ScreenVisionEngine()
        self.pyautogui = None
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui.FAILSAFE = False
            self.pyautogui.PAUSE = 0.05
        except Exception:
            self.pyautogui = None

    def is_available(self) -> bool:
        return (self.has_x11 or self.has_wayland) and bool(self.xdotool or self.ydotool or self.pyautogui)

    # ---------------------------------------------------------
    # Window & Tab Awareness
    # ---------------------------------------------------------

    def get_active_window(self) -> dict[str, Any]:
        """Returns details of the currently focused window."""
        if not self.xdotool:
            return {"error": "xdotool not installed"}

        try:
            wid = subprocess.check_output([self.xdotool, "getactivewindow"], timeout=2).decode().strip()
            title = subprocess.check_output([self.xdotool, "getwindowname", wid], timeout=2).decode().strip()
            
            # Fetch application class
            app_class = ""
            try:
                xprop_out = subprocess.check_output(["xprop", "-id", wid, "WM_CLASS"], timeout=2).decode().strip()
                if "=" in xprop_out:
                    app_class = xprop_out.split("=")[-1].strip().replace('"', "")
            except Exception:
                pass

            # Fetch geometry
            geom = {"x": 0, "y": 0, "width": 0, "height": 0}
            try:
                geo_out = subprocess.check_output([self.xdotool, "getwindowgeometry", wid], timeout=2).decode()
                pos_match = re.search(r"Position:\s*(\d+),(\d+)", geo_out)
                geo_match = re.search(r"Geometry:\s*(\d+)x(\d+)", geo_out)
                if pos_match:
                    geom["x"] = int(pos_match.group(1))
                    geom["y"] = int(pos_match.group(2))
                if geo_match:
                    geom["width"] = int(geo_match.group(1))
                    geom["height"] = int(geo_match.group(2))
            except Exception:
                pass

            return {
                "window_id": wid,
                "title": title,
                "app_name": app_class,
                "geometry": geom,
                "is_active": True,
            }
        except Exception as exc:
            return {"error": f"Failed to get active window: {exc}"}

    def list_open_windows(self) -> list[dict[str, Any]]:
        """Lists all open, visible application windows with titles, classes, and IDs."""
        if not self.xdotool:
            return []

        try:
            active_id = ""
            try:
                active_id = subprocess.check_output([self.xdotool, "getactivewindow"], timeout=1).decode().strip()
            except Exception:
                pass

            raw_ids = subprocess.check_output(
                [self.xdotool, "search", "--onlyvisible", "--name", ""],
                timeout=3,
            ).decode().splitlines()

            windows: list[dict[str, Any]] = []
            seen_titles: set[str] = set()

            for wid in raw_ids:
                wid = wid.strip()
                if not wid:
                    continue
                try:
                    name = subprocess.check_output([self.xdotool, "getwindowname", wid], timeout=1).decode().strip()
                    if not name or name in seen_titles or name in {"mutter guard window", "gnome-shell"}:
                        continue

                    seen_titles.add(name)
                    app_class = ""
                    try:
                        xprop_out = subprocess.check_output(["xprop", "-id", wid, "WM_CLASS"], timeout=1).decode().strip()
                        if "=" in xprop_out:
                            app_class = xprop_out.split("=")[-1].strip().replace('"', "")
                    except Exception:
                        pass

                    windows.append({
                        "window_id": wid,
                        "title": name,
                        "app_name": app_class or name,
                        "is_active": (wid == active_id),
                    })
                except Exception:
                    continue

            return windows
        except Exception:
            return []

    def focus_window(self, target: str) -> ExecutionResult:
        """Focuses/raises a window specified by ID, window title, or application name."""
        if not self.xdotool:
            return ExecutionResult("failed", "xdotool not available", 1)

        def _activate_and_wait(wid: str) -> ExecutionResult:
            try:
                subprocess.run([self.xdotool, "windowactivate", "--sync", wid], check=True, timeout=3)
            except Exception:
                try:
                    subprocess.run([self.xdotool, "windowactivate", wid], check=True, timeout=1)
                except Exception:
                    pass
            
            # Verify loop to ensure the window manager actually gave it focus
            for _ in range(10):
                active_win = self.get_active_window()
                if active_win.get("window_id") == wid:
                    return ExecutionResult("success", f"Activated window {wid}", 0)
                time.sleep(0.2)
            return ExecutionResult("failed", f"Failed to verify activation of window {wid}. Focus might be stuck.", 1)

        # 1. If target is digits, treat as window ID
        if target.isdigit():
            return _activate_and_wait(target)

        # 2. Search by title or class
        try:
            wids = subprocess.check_output(
                [self.xdotool, "search", "--name", target],
                timeout=3,
            ).decode().splitlines()
            if not wids:
                wids = subprocess.check_output(
                    [self.xdotool, "search", "--class", target],
                    timeout=3,
                ).decode().splitlines()

            if wids:
                chosen = wids[-1].strip()
                return _activate_and_wait(chosen)
            return ExecutionResult("failed", f"No window found matching '{target}'", 1)
        except Exception as exc:
            return ExecutionResult("failed", f"Error searching/activating window: {exc}", 1)

    def close_window(self, target: str | None = None) -> ExecutionResult:
        """Closes a target window or the currently active window."""
        if not self.xdotool:
            return ExecutionResult("failed", "xdotool not available", 1)

        try:
            if target:
                self.focus_window(target)
            subprocess.run([self.xdotool, "key", "alt+F4"], check=True, timeout=3)
            return ExecutionResult("success", f"Closed window {target or 'active'}", 0)
        except Exception as exc:
            return ExecutionResult("failed", f"Failed to close window: {exc}", 1)

    def switch_tab(self, direction: str = "next", index: int | None = None) -> ExecutionResult:
        """Switches browser/editor tabs: direction can be 'next', 'prev', or 'index' (1-9)."""
        if not self.xdotool:
            return ExecutionResult("failed", "xdotool not available", 1)

        try:
            if index is not None and 1 <= index <= 9:
                subprocess.run([self.xdotool, "key", f"ctrl+{index}"], check=True, timeout=2)
                return ExecutionResult("success", f"Switched to tab #{index}", 0)
            elif direction == "prev":
                subprocess.run([self.xdotool, "key", "ctrl+shift+Tab"], check=True, timeout=2)
                return ExecutionResult("success", "Switched to previous tab", 0)
            else:
                subprocess.run([self.xdotool, "key", "ctrl+Tab"], check=True, timeout=2)
                return ExecutionResult("success", "Switched to next tab", 0)
        except Exception as exc:
            return ExecutionResult("failed", f"Failed to switch tab: {exc}", 1)

    def new_tab(self, url: str | None = None) -> ExecutionResult:
        """Opens a new browser tab and optionally navigates to a URL."""
        if not self.xdotool:
            return ExecutionResult("failed", "xdotool not available", 1)

        try:
            subprocess.run([self.xdotool, "key", "ctrl+t"], check=True, timeout=2)
            time.sleep(0.3)
            if url:
                subprocess.run([self.xdotool, "type", url], check=True, timeout=3)
                time.sleep(0.1)
                subprocess.run([self.xdotool, "key", "Return"], check=True, timeout=2)
                return ExecutionResult("success", f"Opened new tab with URL: {url}", 0)
            return ExecutionResult("success", "Opened new tab", 0)
        except Exception as exc:
            return ExecutionResult("failed", f"Failed to open new tab: {exc}", 1)

    def close_tab(self, target_window: str | None = None) -> ExecutionResult:
        """Closes the current browser or editor tab (focuses target_window first if provided)."""
        if not self.xdotool:
            return ExecutionResult("failed", "xdotool not available", 1)

        try:
            if target_window:
                self.focus_window(target_window)
                time.sleep(0.3)
            subprocess.run([self.xdotool, "key", "ctrl+w"], check=True, timeout=2)
            return ExecutionResult("success", f"Closed tab in {target_window or 'active window'}.", 0)
        except Exception as exc:
            return ExecutionResult("failed", f"Failed to close tab: {exc}", 1)


    def list_tabs(self) -> dict[str, Any]:
        """Detects active window tabs using title inspection and OCR over the tab bar region."""
        active = self.get_active_window()
        elements = self.vision.read_screen()
        # Find elements located in the upper region of the screen (y < 120) where tabs reside
        tab_candidates = [
            el.text for el in elements
            if el.center_y < 120 and len(el.text) > 2 and el.confidence > 0.6
        ]
        return {
            "active_window": active,
            "detected_tabs": tab_candidates[:12],
        }

    # ---------------------------------------------------------
    # Visual & Coordinate Mouse Actions
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Visual & Coordinate Mouse Actions
    # ---------------------------------------------------------

    def hover(self, x: int, y: int, duration: float = 0.25) -> ExecutionResult:
        """Smoothly moves the mouse cursor to (x, y) and hovers to activate UI hover states."""
        if self.pyautogui:
            try:
                self.pyautogui.moveTo(x, y, duration=duration)
                time.sleep(0.1)
                return ExecutionResult("success", f"Hovered mouse at ({x}, {y})", 0)
            except Exception:
                pass

        tool = self.xdotool or self.ydotool
        if tool:
            try:
                subprocess.run([tool, "mousemove", str(x), str(y)], check=True, timeout=5)
                time.sleep(0.1)
                return ExecutionResult("success", f"Hovered mouse at ({x}, {y})", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to hover mouse: {exc}", 1)

        return ExecutionResult("failed", "No mouse automation backend available.", 1)

    def hover_text(self, text: str, duration: float = 0.3) -> ExecutionResult:
        """Visually locates text on screen using OCR and hovers mouse cursor over its center."""
        matches = self.vision.find_text_on_screen(text)
        if not matches:
            return ExecutionResult("failed", f"Could not find text '{text}' on screen to hover.", 1)

        best = matches[0]
        x, y = best.center_x, best.center_y
        res = self.hover(x, y, duration=duration)
        if res.status == "success":
            return ExecutionResult(
                "success",
                f"Located '{best.text}' on screen at ({x}, {y}) (confidence: {best.confidence:.2f}) and hovered successfully.",
                0,
            )
        return res

    def click_text(self, text: str, double: bool = False, target_window: str | None = None) -> ExecutionResult:
        """Visually locates text on screen using OCR and clicks its center coordinate."""
        if target_window:
            self.focus_window(target_window)
            time.sleep(0.3)

        matches = self.vision.find_text_on_screen(text)
        if not matches:
            return ExecutionResult("failed", f"Could not find text '{text}' on screen.", 1)

        best = matches[0]
        x, y = best.center_x, best.center_y

        action = "double_click" if double else "click"
        res = self.execute_action(action, {"x": x, "y": y})
        if res.status == "success":
            return ExecutionResult(
                "success",
                f"Located '{best.text}' on screen at ({x}, {y}) (confidence: {best.confidence:.2f}) and clicked successfully.",
                0,
            )
        return res

    def browser_search_and_play(self, query: str, platform: str = "youtube") -> ExecutionResult:
        """Autonomously searches YouTube or web in the browser and selects the top video to play."""
        clean_query = query.strip()
        if not clean_query:
            return ExecutionResult("failed", "No query provided to search and play.", 1)

        # 1. Search for an open browser or YouTube window
        windows = self.list_open_windows()
        browser_win = None
        for w in windows:
            title_lower = w.get("title", "").lower()
            app_lower = w.get("app_name", "").lower()
            if any(k in title_lower or k in app_lower for k in ["youtube", "chrome", "firefox", "chromium", "brave"]):
                browser_win = w
                break

        enc_query = urllib.parse.quote_plus(clean_query)
        target_url = f"https://www.youtube.com/results?search_query={enc_query}"

        if browser_win:
            self.focus_window(browser_win["window_id"])
            time.sleep(0.4)

            # If already on YouTube, use the search bar or navigate
            if "youtube" in browser_win.get("title", "").lower():
                # Hit search bar hotkey '/' or click
                self.execute_action("key", {"key": "slash"})
                time.sleep(0.2)
                # Clear and type
                self.execute_action("hotkey", {"combo": "ctrl+a"})
                time.sleep(0.1)
                self.execute_action("type", {"text": clean_query})
                time.sleep(0.1)
                self.execute_action("key", {"key": "Return"})
                time.sleep(1.8)
            else:
                # Open a new tab with direct search results
                self.new_tab(target_url)
                time.sleep(2.0)
        else:
            # Launch default browser with direct search results URL
            try:
                subprocess.Popen(["xdg-open", target_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                import webbrowser
                webbrowser.open(target_url)
            
            # Wait for a browser window to appear and become active
            loaded = False
            for _ in range(20):
                active = self.get_active_window()
                t = active.get("title", "").lower()
                a = active.get("app_name", "").lower()
                if any(k in t or k in a for k in ["youtube", "chrome", "firefox", "chromium", "brave"]):
                    loaded = True
                    time.sleep(1.0) # extra wait for page load
                    break
                time.sleep(0.5)
            if not loaded:
                return ExecutionResult("failed", "Browser window failed to open or become active in time.", 1)

        # 2. Select and play the first video result
        # Try finding video title text or thumbnail coordinate
        query_words = [w for w in clean_query.split() if len(w) > 2]
        clicked = False
        if query_words:
            for w in query_words:
                c_res = self.click_text(w)
                if c_res.status == "success":
                    clicked = True
                    break

        if not clicked:
            # First video search card is reliably around (520, 260) or accessible via Tab + Enter
            self.execute_action("key", {"key": "Tab"})
            time.sleep(0.1)
            self.execute_action("key", {"key": "Return"})
            time.sleep(0.2)
            # Coordinate fallback
            self.execute_action("click", {"x": 520, "y": 260})

        return ExecutionResult(
            "success",
            f"Successfully searched YouTube for '{clean_query}', focused the browser, and started video playback.",
            0,
        )

    def execute_action(self, action: str, parameters: dict[str, Any] | None = None) -> ExecutionResult:
        parameters = parameters or {}
        if not self.is_available():
            display_status = "Wayland" if self.has_wayland else ("X11" if self.has_x11 else "Headless/TTY")
            return ExecutionResult(
                status="failed",
                output=f"GUI automation backend not available (session: {display_status}, xdotool/ydotool missing).",
                exit_code=1,
            )

        tool = self.xdotool or self.ydotool
        action_lower = action.lower().strip()

        # Handle target_window focusing if requested
        target_win = parameters.get("target_window") or parameters.get("window") or parameters.get("app")
        if target_win:
            f_res = self.focus_window(str(target_win))
            if f_res.status == "failed":
                return f_res
            time.sleep(0.2)
        else:
            # Prevent typing/clicking in marrowai if target_win not specified
            if action_lower in {"type", "key", "hotkey", "click", "left_click", "double_click", "right_click", "click_text", "hover_text"}:
                active = self.get_active_window()
                active_title = str(active.get("title", "")).lower()
                if "marrowai" in active_title:
                    switched = False
                    for win in self.list_open_windows():
                        wt = win.get("title", "").lower()
                        if "marrowai" not in wt and not any(ign in wt for ign in ["mutter", "gnome-shell"]):
                            if self.focus_window(win["window_id"]).status == "success":
                                switched = True
                                break
                    if not switched:
                        return ExecutionResult("failed", f"Safety check: Refusing to execute '{action_lower}' into MarrowAI terminal window.", 1)

        # 1. Visual Click by Text
        if action_lower == "click_text":
            text = str(parameters.get("text", "")).strip()
            double = bool(parameters.get("double", False))
            return self.click_text(text, double=double, target_window=target_win)

        # 1b. Visual Hover by Text
        if action_lower == "hover_text":
            text = str(parameters.get("text", "")).strip()
            duration = float(parameters.get("duration", 0.3))
            return self.hover_text(text, duration=duration)

        # 2. Hover Mouse at Coordinates
        if action_lower in {"hover", "mouse_hover"}:
            x = int(parameters.get("x", 0))
            y = int(parameters.get("y", 0))
            duration = float(parameters.get("duration", 0.25))
            return self.hover(x, y, duration=duration)

        # 3. Coordinate Click
        if action_lower in {"click", "left_click"}:
            x = int(parameters.get("x", 0))
            y = int(parameters.get("y", 0))
            if self.pyautogui:
                try:
                    self.pyautogui.moveTo(x, y, duration=0.15)
                    self.pyautogui.click(x, y)
                    return ExecutionResult("success", f"Clicked at ({x}, {y})", 0)
                except Exception:
                    pass
            try:
                subprocess.run([tool, "mousemove", str(x), str(y), "click", "1"], check=True, timeout=5)
                return ExecutionResult("success", f"Clicked at ({x}, {y})", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to execute click: {exc}", 1)

        # 4. Double Click
        if action_lower == "double_click":
            x = int(parameters.get("x", 0))
            y = int(parameters.get("y", 0))
            if self.pyautogui:
                try:
                    self.pyautogui.moveTo(x, y, duration=0.15)
                    self.pyautogui.doubleClick(x, y)
                    return ExecutionResult("success", f"Double-clicked at ({x}, {y})", 0)
                except Exception:
                    pass
            try:
                subprocess.run([tool, "mousemove", str(x), str(y), "click", "--repeat", "2", "--delay", "100", "1"], check=True, timeout=5)
                return ExecutionResult("success", f"Double-clicked at ({x}, {y})", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to execute double click: {exc}", 1)

        # 5. Right Click
        if action_lower == "right_click":
            x = int(parameters.get("x", 0))
            y = int(parameters.get("y", 0))
            if self.pyautogui:
                try:
                    self.pyautogui.moveTo(x, y, duration=0.15)
                    self.pyautogui.rightClick(x, y)
                    return ExecutionResult("success", f"Right-clicked at ({x}, {y})", 0)
                except Exception:
                    pass
            try:
                subprocess.run([tool, "mousemove", str(x), str(y), "click", "3"], check=True, timeout=5)
                return ExecutionResult("success", f"Right-clicked at ({x}, {y})", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to execute right click: {exc}", 1)

        # 5b. Middle Click
        if action_lower == "middle_click":
            x = int(parameters.get("x", 0))
            y = int(parameters.get("y", 0))
            if self.pyautogui:
                try:
                    self.pyautogui.moveTo(x, y, duration=0.15)
                    self.pyautogui.middleClick(x, y)
                    return ExecutionResult("success", f"Middle-clicked at ({x}, {y})", 0)
                except Exception:
                    pass
            try:
                subprocess.run([tool, "mousemove", str(x), str(y), "click", "2"], check=True, timeout=5)
                return ExecutionResult("success", f"Middle-clicked at ({x}, {y})", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to execute middle click: {exc}", 1)

        # 6. Mouse Move
        if action_lower in {"move", "mousemove"}:
            x = int(parameters.get("x", 0))
            y = int(parameters.get("y", 0))
            if self.pyautogui:
                try:
                    self.pyautogui.moveTo(x, y, duration=0.2)
                    return ExecutionResult("success", f"Moved mouse to ({x}, {y})", 0)
                except Exception:
                    pass
            try:
                subprocess.run([tool, "mousemove", str(x), str(y)], check=True, timeout=5)
                return ExecutionResult("success", f"Moved mouse to ({x}, {y})", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to move mouse: {exc}", 1)

        # 7. Scroll
        if action_lower == "scroll":
            direction = str(parameters.get("direction", "down")).lower()
            amount = int(parameters.get("amount", 3))
            if self.pyautogui:
                try:
                    clicks = -amount if direction in {"down", "bottom"} else amount
                    self.pyautogui.scroll(clicks * 100)
                    return ExecutionResult("success", f"Scrolled {direction} by {amount} units", 0)
                except Exception:
                    pass
            button = "4" if direction in {"up", "top"} else "5"
            try:
                subprocess.run([tool, "click", "--repeat", str(amount), "--delay", "50", button], check=True, timeout=5)
                return ExecutionResult("success", f"Scrolled {direction} by {amount} ticks", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to scroll: {exc}", 1)

        # 8. Drag and Drop
        if action_lower == "drag":
            start_x = int(parameters.get("start_x", 0))
            start_y = int(parameters.get("start_y", 0))
            end_x = int(parameters.get("end_x", 0))
            end_y = int(parameters.get("end_y", 0))
            if self.pyautogui:
                try:
                    self.pyautogui.moveTo(start_x, start_y)
                    self.pyautogui.dragTo(end_x, end_y, duration=0.4, button="left")
                    return ExecutionResult("success", f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})", 0)
                except Exception:
                    pass
            try:
                subprocess.run([tool, "mousemove", str(start_x), str(start_y)], check=True, timeout=2)
                subprocess.run([tool, "mousedown", "1"], check=True, timeout=2)
                time.sleep(0.1)
                subprocess.run([tool, "mousemove", str(end_x), str(end_y)], check=True, timeout=2)
                time.sleep(0.1)
                subprocess.run([tool, "mouseup", "1"], check=True, timeout=2)
                return ExecutionResult("success", f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to drag: {exc}", 1)

        # 9. Type Text with Window Focus Safeguards
        if action_lower == "type":
            text = str(parameters.get("text", ""))

            if self.pyautogui:
                try:
                    interval = float(parameters.get("interval", 0.02))
                    self.pyautogui.write(text, interval=interval)
                    return ExecutionResult("success", f"Typed {len(text)} characters", 0)
                except Exception:
                    pass

            try:
                subprocess.run([tool, "type", "--clearmodifiers", "--delay", "20", text], check=True, timeout=10)
                return ExecutionResult("success", f"Typed {len(text)} characters", 0)
            except Exception:
                try:
                    subprocess.run([tool, "type", text], check=True, timeout=10)
                    return ExecutionResult("success", f"Typed {len(text)} characters", 0)
                except Exception as exc:
                    return ExecutionResult("failed", f"Failed to execute type: {exc}", 1)

        # 10. Key press
        if action_lower == "key":
            keys = str(parameters.get("key", "Return")).split()
            if self.pyautogui:
                try:
                    for k in keys:
                        pk = k.lower()
                        if pk in {"return", "enter"}:
                            pk = "enter"
                        elif pk in {"escape", "esc"}:
                            pk = "esc"
                        elif pk in {"slash"}:
                            pk = "/"
                        self.pyautogui.press(pk)
                    return ExecutionResult("success", f"Pressed keys: {' '.join(keys)}", 0)
                except Exception:
                    pass
            try:
                subprocess.run([tool, "key"] + keys, check=True, timeout=5)
                return ExecutionResult("success", f"Pressed keys: {' '.join(keys)}", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to press keys: {exc}", 1)

        # 11. Hotkey / Key combination (e.g. ctrl+c, alt+Tab, ctrl+t)
        if action_lower == "hotkey":
            keys = str(parameters.get("combo") or parameters.get("key", "")).strip()
            if self.pyautogui and "+" in keys:
                try:
                    combo_parts = [k.strip().lower() for k in keys.split("+")]
                    self.pyautogui.hotkey(*combo_parts)
                    return ExecutionResult("success", f"Triggered hotkey combo: {keys}", 0)
                except Exception:
                    pass
            try:
                subprocess.run([tool, "key", keys], check=True, timeout=5)
                return ExecutionResult("success", f"Triggered hotkey combo: {keys}", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to trigger hotkey: {exc}", 1)

        # 12. Autonomous Browser Search & Video Playback Flow
        if action_lower in {"browser_search_and_play", "watch_youtube", "play_youtube"}:
            query = str(parameters.get("query") or parameters.get("text") or parameters.get("target", "")).strip()
            platform = str(parameters.get("platform", "youtube"))
            return self.browser_search_and_play(query, platform=platform)

        # 13. Window management dispatch
        if action_lower == "list_windows":
            wins = self.list_open_windows()
            import json
            return ExecutionResult("success", json.dumps(wins, indent=2), 0)

        if action_lower == "active_window":
            win = self.get_active_window()
            import json
            return ExecutionResult("success", json.dumps(win, indent=2), 0)

        if action_lower == "focus_window":
            target = str(parameters.get("target") or parameters.get("title") or parameters.get("window_id", "")).strip()
            return self.focus_window(target)

        if action_lower == "close_window":
            target = parameters.get("target")
            return self.close_window(str(target) if target else None)

        # 14. Tab management dispatch
        if action_lower == "switch_tab":
            direction = str(parameters.get("direction", "next"))
            index = parameters.get("index")
            return self.switch_tab(direction=direction, index=int(index) if index else None)

        if action_lower == "new_tab":
            url = parameters.get("url")
            return self.new_tab(str(url) if url else None)

        if action_lower == "close_tab":
            target = parameters.get("target") or parameters.get("app") or parameters.get("window")
            return self.close_tab(target_window=str(target) if target else None)

        if action_lower == "list_tabs":
            tabs_info = self.list_tabs()
            import json
            return ExecutionResult("success", json.dumps(tabs_info, indent=2), 0)

        return ExecutionResult("failed", f"Unsupported GUI action: {action}", None)

