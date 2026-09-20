import json
import os
import shutil
import socket
import struct
import subprocess
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any


def discover_ollama_base_url(preferred_url: str | None = None) -> str:
    """Discover working Ollama endpoint across local, WSL, container, and host setups."""
    candidates: list[str] = []
    if preferred_url:
        candidates.append(preferred_url.rstrip("/"))
    env_url = os.getenv("MARROWAI_OLLAMA_BASE_URL")
    if env_url:
        candidates.append(env_url.rstrip("/"))
    candidates.append("http://127.0.0.1:11434")
    candidates.append("http://localhost:11434")

    # If inside WSL / Linux, extract default route gateway host
    try:
        if os.path.exists("/proc/net/route"):
            with open("/proc/net/route", "r", encoding="utf-8") as fh:
                for line in fh:
                    fields = line.strip().split()
                    if len(fields) >= 3 and fields[1] == "00000000":
                        try:
                            gw_ip = socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
                            if gw_ip and gw_ip != "0.0.0.0":
                                candidates.append(f"http://{gw_ip}:11434")
                                break
                        except Exception:
                            continue
    except Exception:
        pass

    candidates.append("http://host.docker.internal:11434")

    # Deduplicate while preserving order
    seen = set()
    unique_candidates: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)

    for url in unique_candidates:
        try:
            req = urllib.request.Request(f"{url}/api/tags", headers={"Accept": "application/json"}, method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return url
        except Exception:
            continue

    return preferred_url or "http://127.0.0.1:11434"


class OfflineModelManager:
    def __init__(self, base_url: str | None = None, model_dir: str | None = None) -> None:
        self.configured_base_url = (base_url or "http://127.0.0.1:11434").rstrip("/")
        if base_url and base_url.rstrip("/") not in {"http://127.0.0.1:11434", "http://localhost:11434"}:
            self.base_url = self.configured_base_url
        else:
            self.base_url = discover_ollama_base_url(self.configured_base_url)
        self.model_dir = Path(model_dir or ".marrowai/models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.last_error = ""
        self._ollama_process: subprocess.Popen | None = None

    def _announce(self, text: str) -> None:
        try:
            from .voice_engine import OfflineVoiceEngine
            threading.Thread(target=OfflineVoiceEngine().speak, args=(text,), daemon=True).start()
        except Exception:
            pass

    def is_available(self) -> bool:
        # Re-check or re-discover if base_url is currently down
        try:
            request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(request, timeout=1.5) as response:
                return response.status == 200
        except Exception:
            pass

        # Try rediscovery in case gateway or service changed (only for default localhost configs)
        if self.configured_base_url in {"http://127.0.0.1:11434", "http://localhost:11434"}:
            discovered = discover_ollama_base_url(self.configured_base_url)
            if discovered != self.base_url:
                self.base_url = discovered
                try:
                    request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
                    with urllib.request.urlopen(request, timeout=1.5) as response:
                        return response.status == 200
                except Exception:
                    pass
        return False

    def start_service(self) -> tuple[bool, str]:
        """Start Ollama locally when installed but not already serving."""
        if self.is_available():
            return True, "Ollama is ready."
        if self.base_url not in {"http://127.0.0.1:11434", "http://localhost:11434"}:
            return False, f"Ollama is not reachable at {self.base_url}. Ensure Ollama is running on your host system."
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

    def download_model(
        self,
        model_name: str,
        progress_callback: Any = None,
        voice_notify: bool = True,
    ) -> tuple[bool, str]:
        if not model_name.strip():
            return False, "Enter a model name first."
        target_name = model_name.strip()
        ready, message = self.start_service()
        if not ready:
            self.last_error = message
            return False, message

        if voice_notify:
            self._announce(f"Starting download of model {target_name}.")

        payload = json.dumps({"name": target_name, "stream": True}).encode("utf-8")
        milestones = {25: False, 50: False, 75: False}

        try:
            request = urllib.request.Request(
                f"{self.base_url}/api/pull",
                data=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=3600) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if event.get("error"):
                        self.last_error = str(event["error"])
                        if voice_notify:
                            self._announce(f"Model download failed: {self.last_error[:100]}")
                        return False, f"Ollama could not download {target_name}: {self.last_error}"

                    status = str(event.get("status", ""))
                    total = int(event.get("total", 0))
                    completed = int(event.get("completed", 0))

                    if total > 0:
                        pct = min(100.0, max(0.0, (completed / total) * 100.0))
                        comp_mb = completed / (1024 * 1024)
                        tot_mb = total / (1024 * 1024)
                        detail = f"{pct:.1f}% ({comp_mb:.1f} MB / {tot_mb:.1f} MB) - {status}"
                        for m in [25, 50, 75]:
                            if pct >= m and not milestones[m]:
                                milestones[m] = True
                                if voice_notify:
                                    self._announce(f"Model download is {m} percent complete.")
                    else:
                        pct = 0.0
                        detail = status

                    if progress_callback:
                        try:
                            progress_callback(pct, detail, completed, total)
                        except Exception:
                            pass

            if progress_callback:
                try:
                    progress_callback(100.0, f"100% - {target_name} verified and ready", 1, 1)
                except Exception:
                    pass

            if voice_notify:
                self._announce(f"Model {target_name} has been downloaded and verified.")
            return True, f"{target_name} is installed locally."
        except urllib.error.URLError as exc:
            self.last_error = str(exc.reason)
            if voice_notify:
                self._announce("Model download could not reach registry.")
            return False, f"Ollama could not reach the model registry: {exc.reason}"
        except Exception as exc:
            self.last_error = str(exc)
            if voice_notify:
                self._announce("Model download failed.")
            return False, f"Model download failed: {exc}"

    def ensure_model(self, model_name: str) -> bool:
        success, _message = self.download_model(model_name)
        return success

    def list_local_models(self) -> list[str]:
        models = self.list_local_models_detailed()
        return [m["name"] for m in models]

    def list_local_models_detailed(self) -> list[dict[str, Any]]:
        try:
            self.is_available()  # Ensures base_url is fresh
            request = urllib.request.Request(f"{self.base_url}/api/tags", headers={"Accept": "application/json"}, method="GET")
            with urllib.request.urlopen(request, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = data.get("models", [])
                results: list[dict[str, Any]] = []
                for item in models:
                    if not isinstance(item, dict):
                        continue
                    name = item.get("name", "")
                    size_bytes = int(item.get("size", 0))
                    if size_bytes >= 1024 * 1024 * 1024:
                        size_fmt = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                    elif size_bytes >= 1024 * 1024:
                        size_fmt = f"{size_bytes / (1024 * 1024):.1f} MB"
                    else:
                        size_fmt = f"{size_bytes} B"
                    mod_at = str(item.get("modified_at", ""))
                    details = item.get("details", {})
                    param_size = details.get("parameter_size", "")
                    quant = details.get("quantization_level", "")
                    results.append({
                        "name": name,
                        "size_bytes": size_bytes,
                        "size_formatted": size_fmt,
                        "modified_at": mod_at[:19].replace("T", " ") if mod_at else "",
                        "parameter_size": param_size,
                        "quantization": quant,
                        "family": details.get("family", ""),
                    })
                return results
        except Exception:
            return []

    def delete_model(self, model_name: str) -> tuple[bool, str]:
        if not model_name.strip():
            return False, "Model name cannot be empty."
        target = model_name.strip()
        try:
            payload = json.dumps({"name": target}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/delete",
                data=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="DELETE",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in {200, 204}:
                    return True, f"Model {target} deleted successfully."
                return False, f"Delete returned HTTP {resp.status}."
        except Exception as exc:
            return False, f"Failed to delete model {target}: {exc}"

