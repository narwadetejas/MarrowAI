from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    status: str
    output: str
    exit_code: int | None = None


class SafeExecutor:
    """Minimal safe executor for local CLI actions."""

    def execute_command(self, command: str) -> ExecutionResult:
        try:
            completed = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=20,
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
