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
        self.configured_base_url = (base_url or "http://127.0.0.1:11434").rstrip("/")
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

        # Try rediscovery in case environment/gateway changed
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
        if not self.is_available():
            return self._fallback_planner.plan(user_input)

        active_model = self._resolve_model()

        payload = {
            "model": active_model,
            "prompt": (
                "You are MarrowAI, an autonomous Linux operating assistant. Return valid JSON only with keys: intent, risk_level, steps.\n"
                "Allowed tools and parameters:\n"
                "- desktop_action: parameters {\"action\": \"open_url\"|\"open_file_manager\"|\"launch_app\"|\"install_package\", \"target\": \"...\", \"app_name\": \"...\", \"package_name\": \"...\"}\n"
                "- run_command: parameters {\"command\": \"...\"}\n"
                "- system_status: parameters {}\n"
                "- manage_vm: parameters {\"action\": \"detect\"|\"create\"|\"status\", \"os_type\": \"ubuntu\"|\"arch\"}\n"
                "- manage_models: parameters {\"action\": \"list\"|\"pull\", \"model_name\": \"...\"}\n"
                "- manage_memory: parameters {\"action\": \"store\"|\"search\"|\"list\", \"text\": \"...\"}\n"
                "- list_files: parameters {\"path\": \".\"}\n"
                "- run_tests: parameters {\"path\": \".\"}\n"
                "- scaffold_backend: parameters {\"project_name\": \"...\"}\n"
                "- echo: parameters {\"text\": \"...\"}\n"
                "To watch a movie, video, music, or search the web, use desktop_action with action 'open_url' and target URL (e.g. YouTube search https://www.youtube.com/results?search_query=... or Google search https://www.google.com/search?q=...).\n"
                "Use risk_level \"low\" for safe read/desktop/browser queries, \"medium\" for installation/modification, and \"high\" for destructive commands.\n"
                "Example: {\"intent\":\"watch_movie\",\"risk_level\":\"low\",\"steps\":[{\"id\":\"step-1\",\"action_type\":\"desktop\",\"tool_name\":\"desktop_action\",\"description\":\"Open browser to search and stream movie\",\"parameters\":{\"action\":\"open_url\",\"target\":\"https://www.youtube.com/results?search_query=watch+aashiqui+2+movie\"},\"approval_required\":false}]}\n"
                f"User request: {user_input}"
            ),
            "stream": False,
        }

        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=12) as resp:
                response_text = resp.read().decode("utf-8")
        except Exception:
            return self._fallback_planner.plan(user_input)

        try:
            response = json.loads(response_text)
            text = response.get("response", "")
            try:
                data = json.loads(text)
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
                        if action_field in {"search_movie_source", "open_browser", "play_media", "search_web", "watch_movie"}:
                            tool_name = "desktop_action"
                            action_type = "desktop"
                            if not params.get("target"):
                                enc_query = urllib.parse.quote_plus(user_input.strip())
                                params = {"action": "open_url", "target": f"https://www.youtube.com/results?search_query={enc_query}"}

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

