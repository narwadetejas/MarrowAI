from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field
from typing import Any

from .interfaces import PlanStep, TaskPlan

KNOWN_MODELS = [
    "llama3.2:1b",
    "llama3.2",
    "mistral",
    "phi3",
    "qwen2.5",
    "gemma2",
    "deepseek-r1:7b",
    "deepseek-r1",
]


class RuleBasedPlanner:
    """Intelligent rule-based planner mapping requests to safe structured plans."""

    def plan(self, user_input: str) -> TaskPlan:
        raw_text = user_input.strip()
        if "current request:" in raw_text.lower():
            idx = raw_text.lower().rfind("current request:")
            raw_text = raw_text[idx + len("current request:"):].strip()
        text = raw_text.lower()

        # 0a. Informative question: What is Arch Linux
        if ("what is" in text or "tell me about" in text or "explain" in text or "describe" in text) and "arch" in text:
            return TaskPlan(
                intent="explain_arch_linux",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Explain Arch Linux and MarrowAI VM provisioning support",
                        tool_name="echo",
                        parameters={
                            "text": (
                                "Arch Linux is a lightweight, rolling-release Linux distribution adhering to simplicity and customization. "
                                "In MarrowAI, I can autonomously detect your hypervisor (QEMU/KVM or Multipass) and provision an Arch Linux VM "
                                "with custom memory, disk, and networking parameters."
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0b. Informative question: What is Ubuntu
        if ("what is" in text or "tell me about" in text or "explain" in text or "describe" in text) and "ubuntu" in text:
            return TaskPlan(
                intent="explain_ubuntu",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Explain Ubuntu and MarrowAI VM provisioning support",
                        tool_name="echo",
                        parameters={
                            "text": (
                                "Ubuntu is a popular, stable Debian-based Linux distribution. "
                                "In MarrowAI, I can autonomously detect hypervisors and launch Ubuntu 24.04 LTS cloud or desktop instances "
                                "using Canonical Multipass or QEMU."
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0c. Informative question: Voice profiles
        if "voice" in text and ("option" in text or "profile" in text or "what" in text or "which" in text or "available" in text or "list" in text or "show" in text or "tell" in text):
            return TaskPlan(
                intent="voice_info",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Detail Indian English voice profiles",
                        tool_name="echo",
                        parameters={
                            "text": (
                                "MarrowAI offers two clear Indian English voice profiles: "
                                "1. Indian English Female (voice: en-in+f2, Microsoft Heera) - natural conversational tone. "
                                "2. Indian English Male (voice: en-in+m3, Microsoft Ravi) - warm and authoritative tone. "
                                "You can switch at any time in chat by saying 'switch to male voice' or 'switch to female voice'."
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0d. Informative question: Virtual Machines & Hypervisors
        if any(q in text for q in ["what is", "tell me about", "explain", "how does", "how do", "why", "what are"]) and any(v in text for v in ["vm", "virtual machine", "virtualization", "hypervisor", "qemu", "kvm", "multipass"]):
            return TaskPlan(
                intent="explain_vm",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Explain Virtual Machines and hypervisor support",
                        tool_name="echo",
                        parameters={
                            "text": (
                                "A virtual machine (VM) is an isolated software computer that runs its own operating system on top of your physical machine. "
                                "In MarrowAI, I autonomously manage hypervisors including QEMU/KVM and Canonical Multipass to launch and run Linux environments "
                                "such as Arch Linux and Ubuntu 24.04 safely without modifying or risking your host operating system."
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0e. Informative question: Models & Recommendations
        if any(q in text for q in ["what is", "tell me about", "which", "recommend", "how does", "explain", "why", "what are"]) and any(m in text for m in ["model", "ollama", "llama", "deepseek", "phi", "mistral", "qwen"]):
            return TaskPlan(
                intent="explain_models",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Explain local AI models and recommendations",
                        tool_name="echo",
                        parameters={
                            "text": (
                                "MarrowAI runs AI models locally and offline using Ollama. "
                                "I recommend 'llama3.2' (3B) for balanced general assistance, 'llama3.2:1b' for ultra-fast performance on lightweight systems, "
                                "and 'deepseek-r1:7b' for advanced mathematical and technical reasoning. All models run completely offline on your device."
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0f. Friendly Greetings & Conversational Openers
        words = text.split()
        if any(g in words for g in ["hello", "hi", "namaste", "hey", "greetings"]) or any(g in text for g in ["good morning", "good evening", "how are you", "how's it going"]):
            return TaskPlan(
                intent="greeting",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Respond to friendly greeting",
                        tool_name="echo",
                        parameters={
                            "text": (
                                "Namaste! I am MarrowAI, your offline Linux operating partner. "
                                "I am interactive, listening, and ready to assist. You can ask me questions about your system, "
                                "request Arch or Ubuntu VM creation, download local AI models, or monitor real-time resources. How may I help you?"
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0g. Memory Storage & Explicit Memorization
        if text.startswith(("remember that ", "remember ", "note that ", "keep in mind that ", "save memory ")):
            fact_to_save = raw_text
            for prefix in ["remember that ", "keep in mind that ", "save memory ", "note that ", "remember "]:
                if text.startswith(prefix):
                    fact_to_save = raw_text[len(prefix):].strip()
                    break

            return TaskPlan(
                intent="remember_fact",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description=f"Store fact in embedded vector memory: {fact_to_save}",
                        tool_name="manage_memory",
                        parameters={"action": "store", "text": fact_to_save, "category": "user_fact"},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0h. Recall Memories & Profile
        if any(p in text for p in [
            "what do you remember about me",
            "what do you remember",
            "show what you remember",
            "what is in your memory",
            "show my memory",
            "show memories",
            "list memories",
            "list memory",
            "recall memories",
            "what do you know about me",
            "what are my preferences",
        ]):
            return TaskPlan(
                intent="recall_memories",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Recall stored user profile facts and vector memories",
                        tool_name="manage_memory",
                        parameters={"action": "list"},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0i. Search Memory
        if text.startswith(("search memory for ", "search memory ", "find in memory ", "search memories for ")):
            q = raw_text
            for prefix in ["search memories for ", "search memory for ", "find in memory ", "search memory "]:
                if text.startswith(prefix):
                    q = raw_text[len(prefix):].strip()
                    break

            return TaskPlan(
                intent="search_memory",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description=f"Semantic search in vector memory for: {q}",
                        tool_name="manage_memory",
                        parameters={"action": "search", "query": q},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 0j. Forget Memory
        if text.startswith(("forget that ", "forget memory ", "delete memory ", "forget ")):
            target_kw = raw_text
            for prefix in ["forget that ", "forget memory ", "delete memory ", "forget "]:
                if text.startswith(prefix):
                    target_kw = raw_text[len(prefix):].strip()
                    break

            return TaskPlan(
                intent="forget_memory",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description=f"Forget memories matching: {target_kw}",
                        tool_name="manage_memory",
                        parameters={"action": "forget", "query": target_kw},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 1a. Arch Linux Virtual Machine creation
        if "arch" in text and ("vm" in text or "virtual machine" in text or "create" in text or "setup" in text or "launch" in text or "provision" in text or "install" in text or "download" in text):
            return TaskPlan(
                intent="create_arch_vm",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Check and verify hypervisor installation for Arch Linux",
                        tool_name="manage_vm",
                        parameters={"action": "ensure", "os_type": "arch"},
                        approval_required=False,
                    ),
                    PlanStep(
                        id="step-2",
                        action_type="tool",
                        description="Provision and configure local Arch Linux VM",
                        tool_name="manage_vm",
                        parameters={"action": "create", "os_type": "arch", "vm_name": "marrowai-arch"},
                        approval_required=False,
                    ),
                ],
                risk_level="low",
            )


        # 1b. Ubuntu / Generic Virtual Machine & OS creation
        if ("vm" in text or "virtual machine" in text) or ("ubuntu" in text and ("create" in text or "download" in text or "setup" in text or "install" in text)):
            return TaskPlan(
                intent="create_ubuntu_vm",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Check and verify hypervisor installation",
                        tool_name="manage_vm",
                        parameters={"action": "ensure"},
                        approval_required=False,
                    ),
                    PlanStep(
                        id="step-2",
                        action_type="tool",
                        description="Provision and launch local Ubuntu OS VM",
                        tool_name="manage_vm",
                        parameters={"action": "create", "vm_name": "marrowai-ubuntu", "release": "24.04"},
                        approval_required=False,
                    ),
                ],
                risk_level="low",
            )

        # 2. Model listing query
        if "model" in text and ("list" in text or "what" in text or "show" in text or "installed" in text or "have" in text or "available" in text) and not ("download" in text or "pull" in text):
            return TaskPlan(
                intent="list_models",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="List all locally installed models in Ollama",
                        tool_name="manage_models",
                        parameters={"action": "list"},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 3. Model download and pull
        words = text.split()
        if ({"download", "pull", "install"} & set(words) or "download" in text or "pull" in text) and ("model" in text or any(m in text for m in ["llama", "mistral", "phi", "qwen", "gemma", "deepseek"])):
            target_model = "llama3.2"
            for m in KNOWN_MODELS:
                if m in text:
                    target_model = m
                    break
            else:
                for i, w in enumerate(words):
                    if w in {"model", "download", "pull", "install"} and i + 1 < len(words):
                        next_word = words[i + 1].strip(".,;:!?")
                        if next_word not in {"a", "an", "the", "offline", "local", "model"}:
                            target_model = next_word
                            break

            return TaskPlan(
                intent="download_model",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description=f"Check if {target_model} is downloaded, then pull if needed with zero-error validation",
                        tool_name="manage_models",
                        parameters={"action": "pull", "model_name": target_model},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 4. System status, telemetry, and live awareness
        if ("status" in text or "what is happening" in text or "resources" in text or "telemetry" in text or "health" in text or "diagnostics" in text):
            return TaskPlan(
                intent="system_status",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Collect comprehensive system telemetry, hypervisor, and model status",
                        tool_name="system_status",
                        parameters={},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 5. List workspace files
        if "list" in text and ("file" in text or "workspace" in text or "directory" in text):
            return TaskPlan(
                intent="list_files",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="cli",
                        description="List the files in the current workspace",
                        tool_name="ls",
                        parameters={"path": "."},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 6. Destructive delete
        if "delete" in text and ("etc" in text or "directory" in text or "all" in text):
            return TaskPlan(
                intent="dangerous_delete",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="cli",
                        description="Delete an entire system directory",
                        tool_name="rm",
                        parameters={"path": "/etc"},
                        approval_required=True,
                    )
                ],
                risk_level="high",
            )

        # 7. Create/build backend
        if ("create" in text or "build" in text) and ("backend" in text or "fastapi" in text):
            return TaskPlan(
                intent="create_backend_project",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Create a local backend project scaffold",
                        tool_name="scaffold_backend",
                        parameters={"project_name": "backend_project"},
                        approval_required=False,
                    ),
                    PlanStep(
                        id="step-2",
                        action_type="tool",
                        description="Run the project test suite",
                        tool_name="run_tests",
                        parameters={"path": "backend_project"},
                        approval_required=False,
                    ),
                ],
                risk_level="low",
            )

        # 8. Test project
        if "test" in text and ("project" in text or "code" in text or "suite" in text):
            return TaskPlan(
                intent="run_tests",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Run the local test suite",
                        tool_name="run_tests",
                        parameters={},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 9. Conversational assistance & self-explanation
        if any(w in text for w in ["who are you", "what can you do", "help", "who created you", "who made you", "your name", "what is your name"]):
            return TaskPlan(
                intent="assistant_info",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Explain assistant capabilities and safety gate",
                        tool_name="echo",
                        parameters={
                            "text": (
                                "I am MarrowAI, your offline-first Linux operating assistant. "
                                "I can autonomously execute computer commands, create Arch Linux and Ubuntu virtual machines, download and manage local AI models, "
                                "scaffold FastAPI backends, run test suites, monitor system resources, and converse via natural expressive Indian English voice."
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 9.5 Universal Computer & Shell Command Execution
        KNOWN_CLI_COMMANDS = {
            "uname", "whoami", "uptime", "hostname", "date", "df", "free", "ps", "top", "htop",
            "neofetch", "fastfetch", "ip", "ifconfig", "netstat", "ping", "curl", "wget",
            "cat", "head", "tail", "grep", "find", "mkdir", "touch", "cp", "mv", "tar", "gzip",
            "unzip", "systemctl", "journalctl", "service", "apt", "apt-get", "pacman", "dnf",
            "yum", "brew", "pip", "pip3", "npm", "cargo", "git", "docker", "podman", "sudo",
            "kill", "killall", "chmod", "chown", "which", "echo", "pwd", "ls", "env", "printenv",
            "lscpu", "lsblk", "lspci", "lsusb", "dmesg", "id", "ss", "traceroute", "awk", "sed",
        }

        extracted_cmd: str | None = None
        raw_trimmed = raw_text

        if raw_trimmed.startswith(("$ ", "# ", "> ")):
            extracted_cmd = raw_trimmed[2:].strip()
        elif text.startswith("run command "):
            extracted_cmd = raw_trimmed[12:].strip()
        elif text.startswith("execute command "):
            extracted_cmd = raw_trimmed[16:].strip()
        elif text.startswith("run terminal "):
            extracted_cmd = raw_trimmed[13:].strip()
        elif text.startswith("execute "):
            extracted_cmd = raw_trimmed[8:].strip()
        elif text.startswith("exec "):
            extracted_cmd = raw_trimmed[5:].strip()
        elif text.startswith("bash "):
            extracted_cmd = raw_trimmed[5:].strip()
        elif text.startswith("shell "):
            extracted_cmd = raw_trimmed[6:].strip()
        elif text.startswith("terminal "):
            extracted_cmd = raw_trimmed[9:].strip()
        elif text.startswith("run ") and not any(w in text for w in ["test", "model", "vm", "arch", "ubuntu", "fastapi", "backend"]):
            extracted_cmd = raw_trimmed[4:].strip()
        elif words and (words[0].strip("$#>") in KNOWN_CLI_COMMANDS or words[0] == "sudo"):
            extracted_cmd = raw_trimmed
        elif ("check" in text or "show" in text) and ("disk" in text or "storage" in text):
            extracted_cmd = "df -h"
        elif ("check" in text or "show" in text) and ("memory" in text or "ram" in text):
            extracted_cmd = "free -h"
        elif ("check" in text or "show" in text) and ("cpu" in text or "processor" in text):
            extracted_cmd = "lscpu"
        elif ("check" in text or "show" in text) and ("ip" in text or "network" in text):
            extracted_cmd = "ip a"
        elif ("check" in text or "show" in text) and "uptime" in text:
            extracted_cmd = "uptime"
        elif ("list" in text or "show" in text) and "process" in text:
            extracted_cmd = "ps aux"
        elif ("create" in text or "make" in text) and ("folder" in text or "directory" in text):
            # Extract folder name if available
            target_name = words[-1].strip(".,;\"'") if len(words) >= 3 else "new_folder"
            extracted_cmd = f"mkdir -p {target_name}"
        elif text.startswith("install package "):
            pkg_name = words[-1].strip(".,;\"'")
            extracted_cmd = f"sudo apt-get install -y {pkg_name}"
        elif text.startswith("install ") and not any(w in text for w in ["model", "vm", "arch", "ubuntu", "backend", "fastapi", "project"]):
            pkg_name = words[-1].strip(".,;\"'")
            extracted_cmd = f"sudo apt-get install -y {pkg_name}"
        elif text.startswith(("uninstall ", "delete app ", "delete application ", "remove app ", "remove application ")) and not any(w in text for w in ["model", "vm", "memory"]):
            pkg_name = words[-1].strip(".,;\"'")
            extracted_cmd = f"sudo apt-get remove -y {pkg_name}"

        if extracted_cmd:
            cmd_lower = extracted_cmd.lower().strip()
            dangerous_tokens = [
                "sudo",
                "rm ",
                "rm -",
                "rmdir",
                "mkfs",
                "dd if=",
                "fdisk",
                "parted",
                "wipefs",
                "shutdown",
                "reboot",
                "poweroff",
                "init 0",
                "init 6",
                "systemctl stop",
                "systemctl disable",
                "systemctl restart",
                "systemctl mask",
                "kill -9",
                "pkill -9",
                "killall -9",
                "chmod -r 777",
                "chmod 777",
                ":(){ :|:& };:",
                "> /dev/sd",
            ]
            is_high_risk = any(tok in cmd_lower for tok in dangerous_tokens)
            return TaskPlan(
                intent="run_command",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="cli",
                        description=f"Execute command on computer: {extracted_cmd}",
                        tool_name="run_command",
                        parameters={"command": extracted_cmd},
                        approval_required=is_high_risk,
                    )
                ],
                risk_level="high" if is_high_risk else "low",
            )

        # 9a. Autonomous Media, Movie, Music & Web Browser Search / Streaming Planning
        is_movie = any(w in text for w in ["movie", "film", "cinema", "documentary", "series", "episode", "trailer"])
        is_music = any(w in text for w in ["song", "music", "track", "audio", "album", "singer"])
        is_video = any(w in text for w in ["youtube", "youtu.be", "youtuuube", "video", "clip"])
        is_watch = any(w in text for w in ["watch", "play", "stream", "listen to", "see the movie", "hear", "where can i find", "where can i watch", "where to watch"])
        is_search = any(w in text for w in ["search for", "search on web", "search google", "look up", "find online", "google "])
        has_install = any(w in text for w in ["install", "download", "downlaod"])
        is_plain_browser = not has_install and (
            any(w in text for w in ["open browser", "launch browser", "start browser", "web browser", "open web"])
            or any(
                (b in text and ("open" in text or "launch" in text or "start" in text))
                for b in ["chrome", "chromium", "firefox", "edge"]
            )
        )

        if not has_install and (is_movie or is_music or is_video or is_watch or is_search or is_plain_browser):
            # Extract target subject by stripping filler intent keywords
            cleaned_query = raw_text
            for prefix in [
                "i want to watch", "i want to play", "i want to stream", "i want to see",
                "i want to listen to", "can you watch", "can you play", "can you stream",
                "please watch", "please play", "please stream", "where can i find",
                "where can i watch", "where to watch", "how can i watch", "search for",
                "search google for", "search web for", "search", "look up", "find me",
                "find", "play me", "play", "watch", "stream", "listen to", "google",
                "open youtube and watch", "open youtube and play", "open youtube",
            ]:
                if cleaned_query.lower().startswith(prefix + " "):
                    cleaned_query = cleaned_query[len(prefix) + 1:].strip()
                elif f" {prefix} " in cleaned_query.lower():
                    idx = cleaned_query.lower().find(f" {prefix} ")
                    cleaned_query = cleaned_query[idx + len(prefix) + 2:].strip()

            # Clean trailing instructions
            for suffix in [" in browser", " on browser", " on web", " on youtube", " in youtube", " on google", " online", " please"]:
                if cleaned_query.lower().endswith(suffix):
                    cleaned_query = cleaned_query[:-len(suffix)].strip()

            cleaned_query = cleaned_query.strip(".,?!:;\"'")
            if not cleaned_query:
                cleaned_query = raw_text

            if is_plain_browser and not is_movie and not is_music and not is_video and not is_search:
                url = "https://www.google.com"
                intent_name = "open_browser"
                desc = "Open web browser"
            elif is_search and not is_movie and not is_video and not is_music:
                url = f"https://www.google.com/search?q={urllib.parse.quote_plus(cleaned_query)}"
                intent_name = "search_web"
                desc = f"Search Google and open web browser for '{cleaned_query}'"
            else:
                # Direct media / movie streaming search
                enc_query = urllib.parse.quote_plus(cleaned_query)
                url = f"https://www.youtube.com/results?search_query={enc_query}"
                intent_name = "watch_movie" if is_movie else ("watch_youtube" if (is_video or is_music) else "watch_media")
                desc = f"Formulate search query and launch web browser to find and stream '{cleaned_query}'"

            return TaskPlan(
                intent=intent_name,
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="desktop",
                        description=desc,
                        tool_name="desktop_action",
                        parameters={"action": "open_url", "target": url, "query": cleaned_query},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 9b. GUI File Manager & Directory Explorer
        is_file_manager = (
            "file manager" in text
            or "file explorer" in text
            or "open files" in text
            or "browse files" in text
            or "open folder" in text
            or "open directory" in text
            or (("open" in text or "launch" in text) and ("nautilus" in text or "nemo" in text or "thunar" in text or "explorer" in text))
        )
        if is_file_manager:
            return TaskPlan(
                intent="open_file_manager",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="desktop",
                        description="Open GUI file manager at current workspace",
                        tool_name="desktop_action",
                        parameters={"action": "open_file_manager", "target": "."},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 9c. App Center / Software Store & Application Installation
        is_appcenter = (
            "appcenter" in text
            or "app center" in text
            or "software center" in text
            or "app store" in text
            or "snap store" in text
            or "gnome software" in text
        )
        if is_appcenter and ("download" in text or "downlaod" in text or "install" in text or "chromium" in text):
            pkg = "chromium-browser" if "chromium" in text else "software"
            return TaskPlan(
                intent="install_package",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="desktop",
                        description="Launch desktop App Center",
                        tool_name="desktop_action",
                        parameters={"action": "launch_app", "app_name": "appcenter"},
                        approval_required=False,
                    ),
                    PlanStep(
                        id="step-2",
                        action_type="desktop",
                        description=f"Install package {pkg}",
                        tool_name="desktop_action",
                        parameters={"action": "install_package", "package_name": pkg},
                        approval_required=False,
                    ),
                ],
                risk_level="low",
            )
        if is_appcenter:
            return TaskPlan(
                intent="open_appcenter",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="desktop",
                        description="Launch desktop App Center",
                        tool_name="desktop_action",
                        parameters={"action": "launch_app", "app_name": "appcenter"},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 9d. General Desktop Package / Software Installation
        if ("install" in text or "downlaod" in text or "download" in text) and any(
            pkg_kw in text for pkg_kw in ["chromium", "chrome", "firefox", "vlc", "git", "curl", "gedit", "vscode", "code"]
        ):
            target_pkg = "chromium-browser" if "chromium" in text else ("firefox" if "firefox" in text else words[-1].strip(".,;\"'"))
            return TaskPlan(
                intent="install_package",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="desktop",
                        description=f"Install software package: {target_pkg}",
                        tool_name="desktop_action",
                        parameters={"action": "install_package", "package_name": target_pkg},
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # 9e. Application Launching (terminal, settings, editor, calculator)
        app_keywords = {
            "terminal": "terminal",
            "editor": "editor",
            "text editor": "editor",
            "calculator": "calc",
            "calc": "calc",
        }
        for kw, app_id in app_keywords.items():
            if ("open " in text or "launch " in text or "start " in text) and kw in text:
                return TaskPlan(
                    intent="launch_app",
                    steps=[
                        PlanStep(
                            id="step-1",
                            action_type="desktop",
                            description=f"Launch application: {kw}",
                            tool_name="desktop_action",
                            parameters={"action": "launch_app", "app_name": app_id},
                            approval_required=False,
                        )
                    ],
                    risk_level="low",
                )

        # 10. General Question Answering Catcher
        # If user asks a question, answer it intelligently rather than marking unsupported
        is_question = (
            text.endswith("?")
            or text.startswith(("what", "why", "how", "when", "where", "who", "which", "can", "could", "is", "are", "do", "does", "will", "tell", "explain"))
            or any(w in words for w in ["what", "why", "how", "who", "can", "could", "explain"])
        )
        if is_question:
            return TaskPlan(
                intent="general_question",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description="Provide intelligent answer to user inquiry",
                        tool_name="echo",
                        parameters={
                            "text": (
                                f"Regarding your question '{user_input.strip()}': "
                                "I am MarrowAI, your offline Linux companion. I can run commands, provision Arch Linux and Ubuntu virtual machines, "
                                "pull local AI models (like llama3.2 and deepseek-r1), monitor live hardware resources, and execute developer workflows. "
                                "Feel free to ask me for technical details, or command me to create a VM or pull a model."
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        # Check if the fallback looks like an actual shell command
        cli_indicators = [
            "sudo", "apt", "apt-get", "systemctl", "docker", "git", "ls", "cat", "cd",
            "mkdir", "rm", "cp", "mv", "chmod", "chown", "curl", "wget", "tar", "grep",
            "find", "ps", "kill", "pip", "python", "python3", "bash", "sh", "./", "/", "\\",
            "ip", "ifconfig", "ping", "ssh", "uname", "df", "free", "top", "htop",
        ]
        has_cli_indicator = (
            any(raw_text.startswith(ci + " ") or raw_text == ci for ci in cli_indicators)
            or any(c in raw_text for c in [";", "&&", "||", "|", ">", "<", "$", "`"])
        )

        if not has_cli_indicator and len(raw_text.split()) > 2 and any(w in raw_text.lower() for w in ["i ", "can ", "please ", "want ", "help ", "show ", "give "]):
            # Natural language conversational statement
            return TaskPlan(
                intent="general_question",
                steps=[
                    PlanStep(
                        id="step-1",
                        action_type="tool",
                        description=f"Provide intelligent guidance for: {raw_text}",
                        tool_name="echo",
                        parameters={
                            "text": (
                                f"I understand your request regarding '{raw_text}'. "
                                "As your offline Linux partner, I can run commands, provision VMs, manage local Ollama models, "
                                "find and play movies/videos in your browser, or assist with system administration and code. "
                                "Please specify what you would like to execute!"
                            )
                        },
                        approval_required=False,
                    )
                ],
                risk_level="low",
            )

        return TaskPlan(
            intent="unknown",
            steps=[
                PlanStep(
                    id="step-1",
                    action_type="cli",
                    description=f"Execute user command on host: {raw_text}",
                    tool_name="run_command",
                    parameters={"command": raw_text},
                    approval_required=True,
                )
            ],
            risk_level="medium",
        )
