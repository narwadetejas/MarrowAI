from __future__ import annotations

import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .scaffold import ProjectScaffold


@dataclass
class ExecutionResult:
    status: str
    output: str
    exit_code: int | None = None


class SafeExecutor:
    """Allowlisted local tools for bounded autonomous workflows."""

    allowed_tools = {"ls", "list_files", "echo", "run_tests", "scaffold_backend"}

    def execute_tool(self, tool_name: str, parameters: dict | None = None) -> ExecutionResult:
        parameters = parameters or {}
        if tool_name not in self.allowed_tools:
            return ExecutionResult("blocked", f"Tool is not allowlisted: {tool_name}", None)

        if tool_name in {"ls", "list_files"}:
            path = Path(str(parameters.get("path", "."))).resolve()
            if not path.is_dir():
                return ExecutionResult("failed", f"Directory does not exist: {path}", None)
            entries = "\n".join(item.name for item in sorted(path.iterdir()))
            return ExecutionResult("success", entries, 0)

        if tool_name == "scaffold_backend":
            project_name = str(parameters.get("project_name", "marrowai_backend")).strip()
            if not project_name or Path(project_name).name != project_name:
                return ExecutionResult("blocked", "Invalid project name", None)
            success = ProjectScaffold().create_backend_project(project_name)
            return ExecutionResult("success" if success else "failed", f"Scaffolded {project_name}", 0 if success else 1)

        if tool_name == "run_tests":
            path = Path(str(parameters.get("path", "."))).resolve()
            if not path.is_dir():
                return ExecutionResult("failed", f"Test directory does not exist: {path}", None)
            return self._run_process([sys.executable, "-m", "pytest", "-q"], cwd=path)

        return self.execute_command(f"echo {parameters.get('text', '')}")

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
