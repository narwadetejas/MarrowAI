from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

from .interfaces import ExecutionResult


class GUIAutomationExecutor:
    """GUI Automation & Accessibility Fallback Executor (MA-CORE-006).

    Per ADR-004 and PRD Section 7.4, GUI automation is used only as a last resort
    fallback when CLI or API actions are unavailable. It is strictly constrained
    and gated by safety review.
    """

    def __init__(self) -> None:
        self.has_x11 = "DISPLAY" in os.environ
        self.has_wayland = "WAYLAND_DISPLAY" in os.environ
        self.xdotool = shutil.which("xdotool")
        self.ydotool = shutil.which("ydotool")

    def is_available(self) -> bool:
        return (self.has_x11 or self.has_wayland) and bool(self.xdotool or self.ydotool)

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
        if action == "click":
            x = parameters.get("x", 0)
            y = parameters.get("y", 0)
            try:
                subprocess.run([tool, "mousemove", str(x), str(y), "click", "1"], check=True, timeout=5)
                return ExecutionResult("success", f"Clicked at ({x}, {y})", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to execute click: {exc}", 1)

        if action == "type":
            text = str(parameters.get("text", ""))
            try:
                subprocess.run([tool, "type", text], check=True, timeout=5)
                return ExecutionResult("success", f"Typed {len(text)} characters", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to execute type: {exc}", 1)

        if action == "key":
            key = str(parameters.get("key", "Return"))
            try:
                subprocess.run([tool, "key", key], check=True, timeout=5)
                return ExecutionResult("success", f"Pressed key {key}", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to press key: {exc}", 1)

        return ExecutionResult("blocked", f"Unsupported GUI action: {action}", None)
