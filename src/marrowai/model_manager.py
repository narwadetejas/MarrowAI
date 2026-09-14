from __future__ import annotations

import json
import shutil
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path


class OfflineModelManager:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model_dir: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_dir = Path(model_dir or ".marrowai/models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.last_error = ""
        self._ollama_process: subprocess.Popen | None = None

    def is_available(self) -> bool:
        try:
            request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(request, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def start_service(self) -> tuple[bool, str]:
        """Start Ollama locally when installed but not already serving."""
        if self.is_available():
            return True, "Ollama is ready."
        if self.base_url != "http://127.0.0.1:11434":
            return False, f"Ollama is not reachable at {self.base_url}. Check the configured address."
        executable = shutil.which("ollama")
        if not executable:
            return False, "Ollama is not installed. Install Ollama first, then try again."
        try:
            self._ollama_process = subprocess.Popen(
                [executable, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exc:
            return False, f"Ollama could not be started: {exc}"
        for _ in range(20):
            if self.is_available():
                return True, "Ollama started and is ready."
            time.sleep(0.25)
        return False, "Ollama is installed but did not become ready. Run 'ollama serve' in a terminal."

    def download_model(self, model_name: str) -> tuple[bool, str]:
        if not model_name.strip():
            return False, "Enter a model name first."
        ready, message = self.start_service()
        if not ready:
            self.last_error = message
            return False, message
        payload = json.dumps({"name": model_name.strip()}).encode("utf-8")
        try:
            request = urllib.request.Request(
                f"{self.base_url}/api/pull",
                data=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=3600) as response:
                body = response.read().decode("utf-8", errors="replace")
            messages = []
            for line in body.splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("error"):
                    self.last_error = str(event["error"])
                    return False, f"Ollama could not download {model_name}: {self.last_error}"
                if event.get("status"):
                    messages.append(str(event["status"]))
            return True, f"{model_name} is installed locally."
        except urllib.error.URLError as exc:
            self.last_error = str(exc.reason)
            return False, f"Ollama could not reach the model registry: {exc.reason}"
        except Exception as exc:
            self.last_error = str(exc)
            return False, f"Model download failed: {exc}"

    def ensure_model(self, model_name: str) -> bool:
        success, _message = self.download_model(model_name)
        return success

    def list_local_models(self) -> list[str]:
        try:
            request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(request, timeout=2) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = data.get("models", [])
                return [item.get("name", "") for item in models if isinstance(item, dict)]
        except Exception:
            return []
