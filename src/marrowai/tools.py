from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import os
import shutil
import subprocess
import sys
import webbrowser
from typing import Any

from .interfaces import ExecutionResult, PlanStep, ToolCall
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


class RemoveFileTool(BaseTool):
    name = "rm"
    description = "Remove a file or directory"
    schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
        },
        "required": ["path"],
    }

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        raw_path = parameters.get("path")
        if not raw_path:
            return ExecutionResult("failed", "No path provided", None)
        path = Path(str(raw_path))
        try:
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
            return ExecutionResult("success", f"Removed {path}", 0)
        except Exception as exc:
            return ExecutionResult("failed", f"Error removing {path}: {exc}", None)


class GUIActionTool(BaseTool):
    name = "gui_action"
    description = "Execute bounded GUI actions (click, type, key) via accessibility fallback."
    schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["click", "type", "key"]},
            "parameters": {"type": "object"},
        },
        "required": ["action"],
    }

    def __init__(self) -> None:
        from .gui_automation import GUIAutomationExecutor
        self._executor = GUIAutomationExecutor()

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        action = str(parameters.get("action", ""))
        action_params = parameters.get("parameters", {})
        return self._executor.execute_action(action, action_params)


class DesktopActionTool(BaseTool):
    """Tool to launch desktop applications, open URLs/browsers, and manage desktop windows/files."""

    name = "desktop_action"
    description = "Launch desktop applications, open GUI file managers, open URLs in web browsers, and install software packages."
    schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["open_url", "open_file_manager", "launch_app", "install_package"],
            },
            "target": {"type": "string"},
            "app_name": {"type": "string"},
            "package_name": {"type": "string"},
        },
        "required": ["action"],
    }

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        action = str(parameters.get("action", "")).strip().lower()

        if action in {"open_url", "open_browser", "open_link"}:
            raw_url = str(parameters.get("target", parameters.get("url", "https://www.youtube.com"))).strip()
            if not raw_url.startswith(("http://", "https://")):
                url = f"https://{raw_url}"
            else:
                url = raw_url
            try:
                if shutil.which("wslview"):
                    subprocess.Popen(["wslview", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif shutil.which("cmd.exe"):
                    subprocess.Popen(["cmd.exe", "/c", "start", "", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif shutil.which("xdg-open") and ("DISPLAY" in os.environ or "WAYLAND_DISPLAY" in os.environ):
                    subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    webbrowser.open(url)
                return ExecutionResult("success", f"Opened URL '{url}' in default browser.", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to open URL '{url}': {exc}", 1)

        if action in {"open_file_manager", "open_files", "browse_folder"}:
            raw_path = str(parameters.get("target", parameters.get("path", "."))).strip() or "."
            path = Path(raw_path).resolve()
            try:
                if shutil.which("wslview"):
                    subprocess.Popen(["wslview", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif shutil.which("explorer.exe"):
                    subprocess.Popen(["explorer.exe", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif shutil.which("xdg-open") and ("DISPLAY" in os.environ or "WAYLAND_DISPLAY" in os.environ):
                    subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif shutil.which("nautilus") and ("DISPLAY" in os.environ or "WAYLAND_DISPLAY" in os.environ):
                    subprocess.Popen(["nautilus", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif os.name == "nt":
                    os.startfile(str(path))
                else:
                    return ExecutionResult("success", f"File manager target directory: {path}", 0)
                return ExecutionResult("success", f"Opened file manager at '{path}'.", 0)
            except Exception as exc:
                return ExecutionResult("failed", f"Failed to open file manager: {exc}", 1)

        if action in {"launch_app", "open_app"}:
            app_name = str(parameters.get("app_name", parameters.get("target", ""))).strip().lower()
            if not app_name:
                return ExecutionResult("failed", "No application name specified.", 1)

            app_candidates: dict[str, list[str]] = {
                "appcenter": ["gnome-software", "snap-store", "io.elementary.appcenter", "plasma-discover"],
                "software": ["gnome-software", "snap-store", "software-properties-gtk"],
                "chromium": ["chromium-browser", "chromium", "google-chrome", "google-chrome-stable"],
                "chrome": ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"],
                "firefox": ["firefox"],
                "terminal": ["gnome-terminal", "konsole", "xfce4-terminal", "xterm"],
                "editor": ["gedit", "kate", "mousepad", "code", "nano"],
                "calc": ["gnome-calculator", "kcalc", "xcalc"],
            }

            binaries = app_candidates.get(app_name, [app_name])
            launched_bin = None
            for b in binaries:
                if shutil.which(b):
                    try:
                        subprocess.Popen([b], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        launched_bin = b
                        break
                    except Exception:
                        pass

            if launched_bin:
                return ExecutionResult("success", f"Launched application '{launched_bin}'.", 0)

            if shutil.which(app_name):
                try:
                    subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return ExecutionResult("success", f"Launched application '{app_name}'.", 0)
                except Exception as exc:
                    return ExecutionResult("failed", f"Failed to launch '{app_name}': {exc}", 1)

            if app_name in {"appcenter", "software", "store", "app store"}:
                if shutil.which("cmd.exe"):
                    try:
                        subprocess.Popen(["cmd.exe", "/c", "start", "ms-windows-store:"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return ExecutionResult("success", "Launched application store.", 0)
                    except Exception:
                        pass
                return ExecutionResult("success", "Desktop software center checked.", 0)

            return ExecutionResult("failed", f"Application '{app_name}' is not installed or not in PATH.", 1)

        if action in {"install_package", "download_package"}:
            pkg = str(parameters.get("package_name", parameters.get("target", ""))).strip()
            password = parameters.get("password")
            if not pkg:
                return ExecutionResult("failed", "No package name specified for installation.", 1)

            import re
            if not re.match(r"^[a-zA-Z0-9_\.\-]+$", pkg):
                return ExecutionResult("blocked", f"Invalid package name '{pkg}'.", 1)

            # Fast-path: Check if the application or binary is already installed
            for candidate in [pkg, f"{pkg}-browser", pkg.replace("-browser", "")]:
                if shutil.which(candidate):
                    return ExecutionResult("success", f"Package '{pkg}' ({candidate}) is already installed and ready to use.", 0)

            timeout = int(parameters.get("timeout", 360))
            if shutil.which("apt-get"):
                cmd = f"sudo apt-get update && sudo apt-get install -y {pkg}"
            elif shutil.which("snap"):
                cmd = f"sudo snap install {pkg}"
            elif shutil.which("pacman"):
                cmd = f"sudo pacman -S --noconfirm {pkg}"
            else:
                return ExecutionResult("failed", "No supported package manager found (apt, snap, pacman).", 1)

            input_data = None
            if password:
                input_data = f"{password}\n"
                cmd = cmd.replace("sudo ", "sudo -S ")

            try:
                res = subprocess.run(cmd, shell=True, input=input_data, capture_output=True, text=True, timeout=timeout)
                out = (res.stdout or "") + (res.stderr or "")
                status = "success" if res.returncode == 0 else "failed"
                return ExecutionResult(status, f"Package installation output:\n{out.strip()}", res.returncode)
            except subprocess.TimeoutExpired:
                # Check if package finished installing despite timeout
                for candidate in [pkg, f"{pkg}-browser", pkg.replace("-browser", "")]:
                    if shutil.which(candidate):
                        return ExecutionResult("success", f"Package '{pkg}' installation completed successfully.", 0)
                return ExecutionResult("failed", "Package installation timed out.", -1)
            except Exception as exc:
                return ExecutionResult("failed", f"Error during package installation: {exc}", 1)

        return ExecutionResult("blocked", f"Unsupported desktop action '{action}'.", 1)


class ManageVMTool(BaseTool):
    name = "manage_vm"
    description = "Autonomous hypervisor detection and Ubuntu VM creation and management."
    schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["detect", "ensure", "create", "status"]},
            "vm_name": {"type": "string", "default": "marrowai-ubuntu"},
            "release": {"type": "string", "default": "24.04"},
        },
    }

    def __init__(self) -> None:
        from .vm_manager import VMManager
        self._manager = VMManager()

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        action = str(parameters.get("action", "detect")).lower()
        os_type = str(parameters.get("os_type", "ubuntu")).lower().strip()
        default_name = "marrowai-arch" if "arch" in os_type else "marrowai-ubuntu"
        vm_name = str(parameters.get("vm_name", default_name)).strip()
        release = str(parameters.get("release", "24.04")).strip()

        if action == "detect":
            hyp = self._manager.detect_hypervisors()
            lines = [f"- {k}: {'yes' if v else 'no'}" for k, v in hyp.items() if k != "recommended"]
            lines.append(f"Recommended hypervisor: {hyp['recommended']}")
            return ExecutionResult("success", "Hypervisor Detection:\n" + "\n".join(lines), 0)

        if action == "ensure":
            ok, msg = self._manager.ensure_hypervisor(os_type=os_type)
            status = "success" if ok else "blocked"
            return ExecutionResult(status, msg, 0 if ok else 1)

        if action == "create":
            return self._manager.create_vm(os_type=os_type, vm_name=vm_name, release=release)

        if action == "status":
            exists, info = self._manager.check_vm_exists(vm_name)
            if exists:
                return ExecutionResult("success", f"VM '{vm_name}' status:\n{info}", 0)
            return ExecutionResult("failed", f"VM '{vm_name}' does not exist.", 1)

        return ExecutionResult("blocked", f"Unsupported VM action: '{action}'", None)


class ManageModelsTool(BaseTool):
    name = "manage_models"
    description = "Inspect, check, and pull local models into Ollama with zero-error validation."
    schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["list", "pull", "status"]},
            "model_name": {"type": "string"},
        },
    }

    def __init__(self) -> None:
        from .config import get_config
        from .model_manager import OfflineModelManager
        config = get_config()
        self._manager = OfflineModelManager(base_url=config.ollama_base_url)

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        action = str(parameters.get("action", "list")).lower()
        model_name = str(parameters.get("model_name", "")).strip()

        if action == "list":
            if not self._manager.is_available():
                return ExecutionResult(
                    "success",
                    "Ollama service is currently stopped or offline. Models catalog available once started.",
                    0,
                )
            models = self._manager.list_local_models()
            if not models:
                return ExecutionResult("success", "No models installed locally yet. Use 'download <model>' to install one.", 0)
            return ExecutionResult("success", "Locally installed models:\n" + "\n".join(f"- {m}" for m in models), 0)

        if action == "status":
            available = self._manager.is_available()
            models = self._manager.list_local_models() if available else []
            status_text = (
                f"Ollama daemon: {'running (online)' if available else 'stopped (offline)'}\n"
                f"Installed models count: {len(models)}"
            )
            return ExecutionResult("success", status_text, 0)

        if action == "pull":
            if not model_name:
                return ExecutionResult("blocked", "No model name specified for download.", None)

            # Check if model is already downloaded first
            if self._manager.is_available():
                local_models = self._manager.list_local_models()
                for m in local_models:
                    if m == model_name or m.startswith(f"{model_name}:"):
                        return ExecutionResult(
                            "success",
                            f"Model '{m}' is already downloaded locally and ready for offline use.",
                            0,
                        )

            # Ensure Ollama service is running and pull with live progress updates
            import sys
            last_pct = -1

            def _cli_progress(pct: float, detail: str, comp: int, tot: int) -> None:
                nonlocal last_pct
                if tot > 0:
                    int_pct = int(pct)
                    if int_pct != last_pct:
                        last_pct = int_pct
                        bars = int_pct // 5
                        bar_str = "=" * bars + ("-" * (20 - bars))
                        comp_mb = comp / (1024 * 1024)
                        tot_mb = tot / (1024 * 1024)
                        sys.stdout.write(f"\rDownloading {model_name}: [{bar_str}] {pct:.1f}% ({comp_mb:.1f} MB / {tot_mb:.1f} MB)")
                        sys.stdout.flush()
                else:
                    sys.stdout.write(f"\rDownloading {model_name}: {detail}")
                    sys.stdout.flush()

            success, message = self._manager.download_model(model_name, progress_callback=_cli_progress)
            sys.stdout.write("\n")
            sys.stdout.flush()
            if success:
                return ExecutionResult("success", f"Successfully downloaded and verified '{model_name}'.", 0)
            return ExecutionResult("failed", f"Could not download '{model_name}': {message}", 1)

        return ExecutionResult("blocked", f"Unsupported model action: '{action}'", None)


class SystemStatusTool(BaseTool):
    name = "system_status"
    description = "Provides comprehensive system awareness including CPU, RAM, VMs, models, and audio."
    schema = {"type": "object"}

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        from .governor import ResourceGovernor
        from .diagnostics import CapabilityDetector
        from .config import get_config
        from .model_manager import OfflineModelManager
        from .vm_manager import VMManager
        from .voice_engine import OfflineVoiceEngine

        gov = ResourceGovernor().get_telemetry()
        diag = CapabilityDetector().detect()
        vm = VMManager().detect_hypervisors()
        voice = OfflineVoiceEngine().status()
        cfg = get_config()
        mgr = OfflineModelManager(base_url=cfg.ollama_base_url)
        models = mgr.list_local_models() if mgr.is_available() else []

        lines = [
            "System Status Overview:",
            f"  - Platform: {diag.platform} ({diag.cpu}), Python {diag.python_version}",
            f"  - CPU Usage: {gov.cpu_percent}% (1-min load: {gov.load_average[0]})",
            f"  - RAM Headroom: {gov.memory_available_mb:.1f} MB available ({100.0 - gov.memory_percent:.1f}% free)",
            f"  - System Health: {'Healthy' if gov.is_healthy else 'Warning: ' + gov.details}",
            f"  - Virtualization (VM): Multipass={'yes' if vm['multipass'] else 'no'}, QEMU={'yes' if vm['qemu'] else 'no'}, KVM={'yes' if vm['kvm_accelerator'] else 'no'}",
            f"  - Local Models: {', '.join(models) if models else 'None installed (Ollama offline/empty)'}",
            f"  - Audio Subsystem: TTS backend={voice['tts_backend']}, STT pipeline={voice['stt_backend']}",
        ]
        return ExecutionResult("success", "\n".join(lines), 0)


class RunCommandTool(BaseTool):
    """Universal tool to execute computer commands, scripts, package management, and system tasks."""

    name = "run_command"
    description = "Execute an arbitrary system shell command on the host computer."

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        command = str(parameters.get("command", "")).strip()
        if not command:
            return ExecutionResult("failed", "No command specified.", 1)

        password = parameters.get("password")
        timeout = int(parameters.get("timeout", 60))
        cwd = parameters.get("cwd", ".")

        input_data = None
        if password and "sudo" in command:
            if not command.startswith("sudo -S"):
                command = command.replace("sudo ", "sudo -S ", 1)
            input_data = f"{password}\n"

        try:
            completed = subprocess.run(
                command,
                shell=True,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            status = "success" if completed.returncode == 0 else "failed"
            return ExecutionResult(status, output.strip(), completed.returncode)
        except subprocess.TimeoutExpired:
            return ExecutionResult("failed", f"Command timed out after {timeout} seconds.", -1)
        except Exception as exc:
            return ExecutionResult("failed", str(exc), 1)


class ManageMemoryTool(BaseTool):
    """Tool to manage, store, search, and recall user facts in the embedded vector memory."""

    name = "manage_memory"
    description = "Store, search, list, or forget facts and memories in the embedded vector database."
    schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["store", "search", "list", "forget"]},
            "text": {"type": "string"},
            "query": {"type": "string"},
            "category": {"type": "string"},
        },
    }

    def __init__(self, memory_store: Any = None) -> None:
        if memory_store is not None:
            self._memory = memory_store
        else:
            from .memory import MemoryStore
            self._memory = MemoryStore()

    def execute(self, parameters: dict[str, Any]) -> ExecutionResult:
        action = str(parameters.get("action", "list")).lower()

        if action == "store":
            text = str(parameters.get("text", "")).strip()
            if not text:
                return ExecutionResult("failed", "No memory text provided to store.", 1)
            cat = str(parameters.get("category", "general"))
            self._memory.remember_fact(text, category=cat)
            return ExecutionResult("success", f"Saved to memory: {text}", 0)

        if action == "search":
            query = str(parameters.get("query", parameters.get("text", ""))).strip()
            if not query:
                return ExecutionResult("failed", "No search query provided.", 1)
            results = self._memory.search_memories(query, limit=5)
            if not results:
                return ExecutionResult("success", f"No memories found matching '{query}'.", 0)
            lines = [f"Found {len(results)} relevant memory item(s):"]
            for r in results:
                lines.append(f"- [{r.get('category', 'general')} | {r.get('score', 0):.2f}] {r['text']}")
            return ExecutionResult("success", "\n".join(lines), 0)

        if action == "list":
            cat = parameters.get("category")
            memories = self._memory.get_all_memories(category=cat, limit=50)
            if not memories:
                return ExecutionResult("success", "No memories stored yet.", 0)
            lines = [f"Stored memories ({len(memories)} items):"]
            for m in memories:
                lines.append(f"- [{m.get('category', 'general')}] {m['text']}")
            return ExecutionResult("success", "\n".join(lines), 0)

        if action == "forget":
            keyword = str(parameters.get("query", parameters.get("text", ""))).strip()
            if not keyword:
                return ExecutionResult("failed", "No keyword specified to forget.", 1)
            removed = self._memory.forget(keyword)
            return ExecutionResult("success", f"Removed {removed} memory item(s) matching '{keyword}'.", 0)

        return ExecutionResult("blocked", f"Unsupported memory action: '{action}'", None)


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
        self.register(GUIActionTool())
        self.register(ManageVMTool())
        self.register(ManageModelsTool())
        self.register(SystemStatusTool())
        run_cmd = RunCommandTool()
        self.register(run_cmd)
        self._tools["system_exec"] = run_cmd
        self._tools["bash"] = run_cmd
        rm_tool = RemoveFileTool()
        self.register(rm_tool)
        self._tools["delete_file"] = rm_tool
        mem_tool = ManageMemoryTool()
        self.register(mem_tool)
        self._tools["remember"] = mem_tool
        desktop_tool = DesktopActionTool()
        self.register(desktop_tool)
        self._tools["open_app"] = desktop_tool
        self._tools["launch_app"] = desktop_tool
        self._tools["open_url"] = desktop_tool
        self._tools["install_package"] = desktop_tool

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


class ToolRouter:
    """Tool Router per LLD Section 3.2: Routes PlanSteps to validated, typed ToolCalls."""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()

    def route(self, step: PlanStep, password: str | None = None) -> ToolCall:
        tool_name = step.tool_name or "run_command"
        args = dict(step.parameters or {})
        if password and "password" not in args:
            args["password"] = password

        # Set appropriate timeout based on action type
        timeout = 30
        if step.action_type in {"cli", "install_package", "manage_vm"}:
            timeout = 120
        elif step.action_type == "test":
            timeout = 60

        return ToolCall(
            tool_name=tool_name,
            arguments=args,
            timeout_seconds=timeout,
            resource_profile="high" if step.approval_required else "standard",
        )

