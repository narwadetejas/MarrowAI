from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any
import urllib.parse
import urllib.request
import urllib.error

from .interfaces import PlanStep, TaskPlan
from .model_manager import discover_ollama_base_url
from .planner import RuleBasedPlanner


class ModelProvider(ABC):
    @abstractmethod
    def generate_plan(self, user_input: str) -> TaskPlan:
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError


class OllamaProvider(ModelProvider):
    def __init__(self, base_url: str | None = None, model: str = "llama3.2") -> None:
        self._explicit_base_url = base_url is not None
        if self._explicit_base_url:
            self.configured_base_url = base_url.rstrip("/")
            self.base_url = self.configured_base_url
        else:
            self.configured_base_url = "http://127.0.0.1:11434"
            self.base_url = discover_ollama_base_url(self.configured_base_url)
        self.configured_model = model
        self.model = model
        self._fallback_planner = RuleBasedPlanner()

    def is_available(self) -> bool:
        try:
            request = urllib.request.Request(
                f"{self.base_url}/api/tags",
                headers={"Accept": "application/json"},
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=1.5) as resp:
                return resp.status == 200
        except Exception:
            pass

        # Try rediscovery in case environment/gateway changed (only when base_url was not explicitly pinned)
        if not self._explicit_base_url:
            discovered = discover_ollama_base_url(self.configured_base_url)
            if discovered != self.base_url:
                self.base_url = discovered
                try:
                    request = urllib.request.Request(
                        f"{self.base_url}/api/tags",
                        headers={"Accept": "application/json"},
                        method="GET",
                    )
                    with urllib.request.urlopen(request, timeout=1.5) as resp:
                        return resp.status == 200
                except Exception:
                    pass
        return False

    def _resolve_model(self) -> str:
        """Ensure the chosen model exists in Ollama, or pick the first available installed model."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                headers={"Accept": "application/json"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", []) if isinstance(m, dict)]
                if not models:
                    return self.configured_model
                # If configured model or its tag variant is present, use it
                for m in models:
                    if m == self.configured_model or m.startswith(f"{self.configured_model}:"):
                        self.model = m
                        return m
                # Otherwise, default to first available model installed locally
                self.model = models[0]
                return self.model
        except Exception:
            return self.configured_model

    def generate_plan(self, user_input: str) -> TaskPlan:
        # Fast-path check: Check rule-based planner first for deterministic high-confidence requests
        rule_plan = self._fallback_planner.plan(user_input)
        if rule_plan.intent not in {"unknown", "general_question"} and rule_plan.steps:
            return rule_plan

        if not self.is_available():
            return rule_plan

        active_model = self._resolve_model()

        payload = {
            "model": active_model,
            "format": "json",
            "prompt": (
                "You are MarrowAI, an autonomous agent. Return valid JSON only with keys: intent, risk_level, steps.\n"
                "Allowed tools and parameters:\n"
                "- screen_perception: parameters {\"action\": \"describe_screen\"|\"read_screen\"|\"find_text\"|\"capture_screen\", \"query\": \"...\"}\n"
                "- window_management: parameters {\"action\": \"list_windows\"|\"active_window\"|\"focus_window\"|\"close_window\"|\"switch_tab\"|\"new_tab\"|\"close_tab\"|\"list_tabs\", \"target\": \"...\", \"direction\": \"next\"|\"prev\", \"index\": 1}\n"
                "- gui_action: parameters {\"action\": \"click\"|\"click_text\"|\"hover\"|\"hover_text\"|\"double_click\"|\"right_click\"|\"type\"|\"key\"|\"hotkey\"|\"scroll\"|\"browser_search_and_play\", \"parameters\": {\"x\": 0, \"y\": 0, \"text\": \"...\", \"key\": \"Return\", \"combo\": \"ctrl+t\", \"direction\": \"down\", \"target_window\": \"...\", \"query\": \"...\"}}\n"
                "- daily_context: parameters {\"action\": \"review_today\"|\"get_history\"|\"list_days\", \"date\": \"...\"}\n"
                "- desktop_action: parameters {\"action\": \"open_url\"|\"open_file_manager\"|\"launch_app\"|\"install_package\", \"target\": \"...\", \"app_name\": \"...\", \"package_name\": \"...\"}\n"
                "- run_command: parameters {\"command\": \"...\"}\n"
                "- system_status: parameters {}\n"
                "- manage_vm: parameters {\"action\": \"detect\"|\"create\"|\"status\", \"os_type\": \"ubuntu\"|\"arch\"}\n"
                "- manage_models: parameters {\"action\": \"list\"|\"pull\", \"model_name\": \"...\"}\n"
                "- manage_memory: parameters {\"action\": \"store\"|\"search\"|\"list\", \"text\": \"...\"}\n"
                "- list_files: parameters {\"path\": \".\"}\n"
                "- write_file: parameters {\"path\": \"...\", \"content\": \"...\"}\n"
                "- echo: parameters {\"text\": \"...\"} -> Use this tool to answer general questions, explanations, greetings, or chat conversation.\n"
                "IMPORTANT: You are a fully autonomous JARVIS-like assistant with complete control over this desktop. You have full autonomous vision of the screen, window/tab awareness, terminal, file system, and mouse/keyboard control (clicking, hovering, typing, shortcuts).\n"
                "- When the user asks to watch or play a song, video, or movie, use 'desktop_action' with open_url (https://www.youtube.com/results?search_query=...) or 'gui_action' with 'browser_search_and_play' to autonomously find and stream the video.\n"
                "- When the user asks a question, definition, or explanation, ALWAYS use the 'echo' tool with your answer in parameters {\"text\": \"...\"}.\n"
                "- Use 'window_management' and 'gui_action' when user wants to control windows, tabs, click, hover, scroll, or type.\n"
                "Use risk_level \"low\" for safe read queries and GUI interactions, \"medium\" for system modifications, and \"high\" for destructive commands.\n"
                "Example for questions: {\"intent\":\"answer_question\",\"risk_level\":\"low\",\"steps\":[{\"id\":\"step-1\",\"action_type\":\"tool\",\"tool_name\":\"echo\",\"description\":\"Answer user question\",\"parameters\":{\"text\":\"Arch Linux is a lightweight Linux distribution...\"},\"approval_required\":false}]}\n"
                f"User Context & Request: {user_input}"

            ),
            "stream": False,
            "options": {
                "num_predict": 256,
                "temperature": 0.2,
            },
        }

        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as resp:
                response_text = resp.read().decode("utf-8")
        except Exception:
            return rule_plan

        try:
            response = json.loads(response_text)
            text = response.get("response", "")
            
            import re
            json_str = text
            # Extract JSON block if surrounded by markdown or conversational filler
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                json_str = m.group(0)

            try:
                data = json.loads(json_str)
                if isinstance(data, dict):
                    steps = data.get("steps", [])
                    parsed_steps: list[PlanStep] = []
                    for index, step in enumerate(steps):
                        action_type = str(step.get("action_type", "desktop"))
                        tool_name = step.get("tool_name")
                        params = step.get("parameters", {})
                        desc = str(step.get("description", ""))

                        # Normalize media/movie actions produced by LLMs
                        action_field = step.get("action") or params.get("action", "")
                        if action_field in {"search_movie_source", "open_browser", "play_media", "search_web", "watch_movie", "watch_youtube", "browser_search_and_play"}:
                            clean_q = params.get("query") or params.get("text") or user_input.strip()
                            enc_query = urllib.parse.quote_plus(clean_q)
                            tool_name = "desktop_action"
                            action_type = "desktop"
                            params = {"action": "open_url", "target": f"https://www.youtube.com/results?search_query={enc_query}", "query": clean_q}
                        elif tool_name in {"launch_app", "open_app"}:
                            tool_name = "desktop_action"
                            params.setdefault("action", "launch_app")
                            if "app_name" not in params and "target" in params:
                                params["app_name"] = params["target"]
                        elif tool_name == "desktop_action":
                            if "action" not in params:
                                if action_field:
                                    params["action"] = action_field
                                elif "app_name" in params:
                                    params["action"] = "launch_app"
                                elif "url" in params:
                                    params["action"] = "open_url"
                                else:
                                    params["action"] = "launch_app"
                        elif tool_name in {"close_tab", "switch_tab", "new_tab", "list_tabs", "list_windows", "active_window", "focus_window"}:
                            action_name = tool_name
                            tool_name = "window_management"
                            params.setdefault("action", action_name)
                        elif tool_name in {"type", "click", "hover", "double_click", "right_click", "middle_click", "scroll", "drag", "key", "hotkey", "click_text", "hover_text"}:
                            action_name = tool_name
                            tool_name = "gui_action"
                            action_type = "gui"
                            params.setdefault("action", action_name)
                        elif tool_name == "run_command" and any(k in str(params.get("command", "")) for k in ["xdg-open", "youtube.com", "google-chrome"]):
                            # Normalize browser run_commands into safe desktop open_url
                            cmd_str = str(params.get("command", ""))
                            m = re.search(r"https?://[^\s'\"]+", cmd_str)
                            url = m.group(0) if m else "https://www.youtube.com"
                            tool_name = "desktop_action"
                            action_type = "desktop"
                            params = {"action": "open_url", "target": url}


                        parsed_steps.append(
                            PlanStep(
                                id=str(step.get("id", f"step-{index + 1}")),
                                action_type=action_type,
                                description=desc or f"Execute step {index + 1}",
                                tool_name=tool_name,
                                parameters=params,
                                approval_required=bool(step.get("approval_required", False)),
                            )
                        )

                    if parsed_steps:
                        return TaskPlan(
                            intent=str(data.get("intent", "general_task")),
                            risk_level=str(data.get("risk_level", "low")),
                            steps=parsed_steps,
                        )
            except Exception:
                pass

            # If the model returned direct conversational answer prose
            if text and text.strip():
                clean_reply = text.strip()
                return TaskPlan(
                    intent="answer_question",
                    risk_level="low",
                    steps=[
                        PlanStep(
                            id="step-1",
                            action_type="tool",
                            description="Answer user question with local model",
                            tool_name="echo",
                            parameters={"text": clean_reply},
                            approval_required=False,
                        )
                    ],
                )
        except Exception:
            return self._fallback_planner.plan(user_input)
        return self._fallback_planner.plan(user_input)

