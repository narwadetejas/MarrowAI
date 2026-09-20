from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import sys
from typing import Any

from .interfaces import ExecutionResult
from .scaffold import ProjectScaffold


class BaseTool(ABC):
    """Abstract interface for all MarrowAI allowlisted tools."""

    name: str = ""
    description: str = ""
    schema: dict[str, Any] = {}

    @abstractmethod
    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        raise NotImplementedError


class ListFilesTool(BaseTool):
    name = "list_files"
    description = "List files in a directory safely without shell execution."
    schema = {
        "type": "object",
        "properties": {"path": {"type": "string", "default": "."}},
    }

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        target_path = Path(str(parameters.get("path", "."))).resolve()
        if not target_path.is_dir():
            return ExecutionResult("failed", f"Directory does not exist: {target_path}", None)
        try:
            entries = "\n".join(item.name for item in sorted(target_path.iterdir()))
            return ExecutionResult("success", entries, 0)
        except Exception as exc:
            return ExecutionResult("failed", f"Error listing directory: {exc}", None)


class ScaffoldBackendTool(BaseTool):
    name = "scaffold_backend"
    description = "Scaffold a clean, testable FastAPI backend project."
    schema = {
        "type": "object",
        "properties": {"project_name": {"type": "string", "default": "backend_project"}},
    }

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        project_name = str(parameters.get("project_name", "backend_project")).strip()
        if not project_name or Path(project_name).name != project_name:
            return ExecutionResult("blocked", f"Invalid project name: '{project_name}'", None)
        success = ProjectScaffold().create_backend_project(project_name)
        if success:
            return ExecutionResult("success", f"Scaffolded {project_name}", 0)
        return ExecutionResult("failed", f"Failed to scaffold {project_name}", 1)


class RunTestsTool(BaseTool):
    name = "run_tests"
    description = "Run a local pytest test suite in a specified directory."
    schema = {
        "type": "object",
        "properties": {"path": {"type": "string", "default": "."}},
    }

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        target_path = Path(str(parameters.get("path", "."))).resolve()
        if not target_path.is_dir():
            return ExecutionResult("failed", f"Test directory does not exist: {target_path}", None)
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=target_path,
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            status = "success" if completed.returncode == 0 else "failed"
            return ExecutionResult(status, output.strip(), completed.returncode)
        except subprocess.TimeoutExpired:
            return ExecutionResult("failed", "Test execution timed out after 30 seconds.", None)
        except Exception as exc:
            return ExecutionResult("failed", str(exc), None)


class EchoTool(BaseTool):
    name = "echo"
    description = "Echo text back to the assistant output."
    schema = {
        "type": "object",
        "properties": {"text": {"type": "string", "default": ""}},
    }

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        text = str(parameters.get("text", ""))
        return ExecutionResult("success", text, 0)


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read file contents safely with bounded size limits."
    schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "max_bytes": {"type": "integer", "default": 65536},
        },
        "required": ["path"],
    }

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        raw_path = parameters.get("path")
        if not raw_path:
            return ExecutionResult("failed", "No path provided", None)
        path = Path(str(raw_path)).resolve()
        if not path.is_file():
            return ExecutionResult("failed", f"File does not exist: {path}", None)
        try:
            max_bytes = int(parameters.get("max_bytes", 65536))
            content = path.read_text(encoding="utf-8", errors="replace")[:max_bytes]
            return ExecutionResult("success", content, 0)
        except Exception as exc:
            return ExecutionResult("failed", f"Error reading file: {exc}", None)


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write text content to a file inside the local workspace safely."
    schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["path", "content"],
    }

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        raw_path = parameters.get("path")
        content = parameters.get("content", "")
        if not raw_path:
            return ExecutionResult("failed", "No path provided", None)
        path = Path(str(raw_path)).resolve()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(content), encoding="utf-8")
            return ExecutionResult("success", f"Wrote {len(str(content))} bytes to {path.name}", 0)
        except Exception as exc:
            return ExecutionResult("failed", f"Error writing file: {exc}", None)


class ToolRegistry:
    """Registry maintaining active allowlisted tools and schemas."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        list_tool = ListFilesTool()
        self.register(list_tool)
        # Register alias 'ls' for backwards compatibility
        self._tools["ls"] = list_tool
        self.register(ScaffoldBackendTool())
        self.register(RunTestsTool())
        self.register(EchoTool())
        self.register(ReadFileTool())
        self.register(WriteFileTool())

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def execute(self, tool_name: str, parameters: dict[str, Any] | None = None) -> ExecutionResult:
        tool = self.get(tool_name)
        if not tool:
            return ExecutionResult("blocked", f"Tool is not allowlisted: {tool_name}", None)
        return tool.execute(parameters or {})
