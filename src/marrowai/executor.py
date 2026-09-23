from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .governor import ResourceGovernor
from .interfaces import ExecutionResult, ToolCall
from .tools import ToolRegistry


class SafeExecutor:
    """Allowlisted local tools and universal execution engine per HLD & LLD."""

    allowed_tools = {
        "ls",
        "list_files",
        "echo",
        "run_tests",
        "scaffold_backend",
        "read_file",
        "write_file",
        "gui_action",
        "manage_vm",
        "manage_models",
        "system_status",
        "run_command",
        "system_exec",
        "bash",
        "rm",
        "delete_file",
        "manage_memory",
        "remember",
        "desktop_action",
        "open_app",
        "launch_app",
        "open_url",
        "install_package",
        "click",
        "left_click",
        "double_click",
        "right_click",
        "middle_click",
        "hover",
        "hover_text",
        "mouse_hover",
        "move",
        "mousemove",
        "type",
        "type_text",
        "key",
        "press_key",
        "hotkey",
        "scroll",
        "click_text",
        "browser_search_and_play",
        "watch_youtube",
        "play_youtube",
        "window_management",
        "screen_perception",
        "daily_context",
    }

    def __init__(self, governor: ResourceGovernor | None = None, registry: ToolRegistry | None = None) -> None:
        self.governor = governor or ResourceGovernor()
        self.registry = registry or ToolRegistry()

    def execute_tool(self, tool_name: str, parameters: dict[str, Any] | None = None) -> ExecutionResult:
        parameters = parameters or {}
        if not self.registry.has(tool_name) and tool_name not in self.allowed_tools:
            # If tool is not registered directly, attempt to execute as a universal system command if applicable
            if self.registry.has("run_command"):
                return self.registry.execute("run_command", {"command": tool_name, **parameters})
            return ExecutionResult("blocked", f"Tool is not allowlisted: {tool_name}", None)

        # Pre-execution check with Resource Governor (MA-CORE-005)
        if tool_name in {"run_tests", "scaffold_backend"}:
            safe, reason = self.governor.is_safe_to_execute()
            if not safe:
                return ExecutionResult("blocked", reason, None)

        return self.registry.execute(tool_name, parameters)

    def execute_tool_call(self, tool_call: ToolCall) -> ExecutionResult:
        """Executes a typed ToolCall per LLD specification."""
        return self.execute_tool(tool_call.tool_name, tool_call.arguments)

    def execute_command(self, command: str, cwd: Path | None = None) -> ExecutionResult:
        try:
            arguments = shlex.split(command)
        except ValueError as exc:
            return ExecutionResult("blocked", str(exc), None)
        if not arguments:
            return ExecutionResult("blocked", "Empty command.", None)
        if arguments[0] == "echo":
            return ExecutionResult("success", " ".join(arguments[1:]), 0)
        return self._run_process(arguments, cwd=cwd)

    def _run_process(self, arguments: list[str], cwd: Path | None = None) -> ExecutionResult:
        try:
            cmd = list(arguments)
            if cmd and cmd[0] == "python" and not shutil.which("python"):
                cmd[0] = sys.executable or "python3"
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=cwd,
                shell=False,
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            status = "success" if completed.returncode == 0 else "failed"
            return ExecutionResult(
                status=status,
                output=output.strip(),
                exit_code=completed.returncode,
            )
        except Exception as exc:  # pragma: no cover - defensive path
            return ExecutionResult(
                status="failed",
                output=str(exc),
                exit_code=None,
            )

