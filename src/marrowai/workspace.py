from __future__ import annotations

import os
from pathlib import Path


class WorkspaceAgent:
    def __init__(self, workspace_root: str | None = None) -> None:
        self.workspace_root = Path(workspace_root or os.getcwd())

    def list_workspace(self) -> list[str]:
        return [str(path.name) for path in sorted(self.workspace_root.iterdir())]

    def ensure_project_dir(self, project_name: str) -> Path:
        target = self.workspace_root / project_name
        target.mkdir(parents=True, exist_ok=True)
        return target
