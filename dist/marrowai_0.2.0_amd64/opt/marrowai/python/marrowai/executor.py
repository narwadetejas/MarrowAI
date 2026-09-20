from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

from .governor import ResourceGovernor
from .interfaces import ExecutionResult
from .tools import ToolRegistry


class SafeExecutor:
    """Allowlisted local tools for bounded autonomous workflows."""

    allowed_tools = {"ls", "list_files", "echo", "run_tests", "scaffold_backend", "read_file", "write_file"}

    def __init__(self, governor: ResourceGovernor | None = None, registry: ToolRegistry | None = None) -> None:
        self.governor = governor or ResourceGovernor()
        self.registry = registry or ToolRegistry()

    def execute_tool(self, tool_name: str, parameters: dict[str, Any] | None = None) -> ExecutionResult:
        parameters = parameters or {}
        if tool_name not in self.allowed_tools or not self.registry.has(tool_name):
            return ExecutionResult("blocked", f"Tool is not allowlisted: {tool_name}", None)

        # Pre-execution check with Resource Governor (MA-CORE-005)
        if tool_name in {"run_tests", "scaffold_backend"}:
            safe, reason = self.governor.is_safe_to_execute()
            if not safe:
                return ExecutionResult("blocked", reason, None)

        return self.registry.execute(tool_name, parameters)

    def execute_command(self, command: str) -> ExecutionResult:
        try:
            arguments = shlex.split(command)
        except ValueError as exc:
            return ExecutionResult("blocked", str(exc), None)
        if not arguments or arguments[0] not in {"echo", "ls"}:
            return ExecutionResult("blocked", "Command is not allowlisted.", None)
        if arguments[0] == "echo":
            return ExecutionResult("success", " ".join(arguments[1:]), 0)
        return self._run_process(arguments)

    def _run_process(self, arguments: list[str], cwd: Path | None = None) -> ExecutionResult:
        try:
            completed = subprocess.run(
                arguments,
                capture_output=True,
                text=True,
                timeout=20,
                cwd=cwd,
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
