from __future__ import annotations

import json
import urllib.request
from pathlib import Path


class OfflineModelManager:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model_dir: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_dir = Path(model_dir or ".marrowai/models")
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        try:
            request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(request, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def ensure_model(self, model_name: str) -> bool:
        if not self.is_available():
            return False
        payload = json.dumps({"name": model_name}).encode("utf-8")
        try:
            request = urllib.request.Request(
                f"{self.base_url}/api/pull",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status == 200
        except Exception:
            return False

    def list_local_models(self) -> list[str]:
        try:
            request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(request, timeout=2) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = data.get("models", [])
                return [item.get("name", "") for item in models if isinstance(item, dict)]
        except Exception:
            return []
