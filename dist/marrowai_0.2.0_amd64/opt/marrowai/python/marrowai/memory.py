from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or ".marrowai/memory.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _load(self) -> dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {}

    def _save(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

    def remember(self, key: str, value: Any) -> None:
        data = self._load()
        data[key] = value
        self._save(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._load().get(key, default)

    def add_event(self, role: str, message: str) -> None:
        data = self._load()
        history = data.setdefault("history", [])
        history.append({"role": role, "message": message})
        if len(history) > 50:
            history = history[-50:]
        data["history"] = history
        self._save(data)

    def build_context(self, user_input: str) -> str:
        data = self._load()
        history = data.get("history", [])
        recent = history[-6:]
        profile = data.get("profile", {})
        parts = []
        if profile:
            parts.append(f"User profile: {json.dumps(profile, sort_keys=True)}")
        if recent:
            parts.append("Recent interaction:")
            for item in recent:
                parts.append(f"- {item['role']}: {item['message']}")
        if user_input:
            parts.append(f"Current request: {user_input}")
        return "\n".join(parts)

    def set_profile(self, profile: dict[str, Any]) -> None:
        data = self._load()
        data["profile"] = profile
        self._save(data)
