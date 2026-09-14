from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import urllib.request
import urllib.error

from .planner import RuleBasedPlanner, TaskPlan


class ModelProvider(ABC):
    @abstractmethod
    def generate_plan(self, user_input: str) -> TaskPlan:
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError


class OllamaProvider(ModelProvider):
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "llama3.2") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._fallback_planner = RuleBasedPlanner()

    def is_available(self) -> bool:
        try:
            request = urllib.request.Request(
                f"{self.base_url}/api/tags",
                headers={"Accept": "application/json"},
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate_plan(self, user_input: str) -> TaskPlan:
        if not self.is_available():
            return self._fallback_planner.plan(user_input)

        payload = {
            "model": self.model,
            "prompt": (
                "You are MarrowAI. Return valid JSON only with keys: intent, risk_level, steps. "
                "For safe tasks, use action_type cli and tool_name ls. "
                "Example: {\"intent\":\"list_files\",\"risk_level\":\"low\",\"steps\":[{\"id\":\"step-1\",\"action_type\":\"cli\",\"tool_name\":\"ls\",\"description\":\"List files\",\"parameters\":{\"path\":\".\"},\"approval_required\":false}]}\n"
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
            with urllib.request.urlopen(request, timeout=10) as resp:
                response_text = resp.read().decode("utf-8")
        except Exception:
            return self._fallback_planner.plan(user_input)

        try:
            response = json.loads(response_text)
            text = response.get("response", "")
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError("invalid payload")
            steps = data.get("steps", [])
            return TaskPlan(
                intent=str(data.get("intent", "unknown")),
                risk_level=str(data.get("risk_level", "medium")),
                steps=[
                    __import__("marrowai.planner", fromlist=["PlanStep"]).PlanStep(
                        id=str(step.get("id", f"step-{index + 1}")),
                        action_type=str(step.get("action_type", "question")),
                        description=str(step.get("description", "")),
                        tool_name=step.get("tool_name"),
                        parameters=step.get("parameters", {}),
                        approval_required=bool(step.get("approval_required", False)),
                    )
                    for index, step in enumerate(steps)
                ] or [
                    __import__("marrowai.planner", fromlist=["PlanStep"]).PlanStep(
                        id="step-1",
                        action_type="question",
                        description="Could not parse a valid plan from model output",
                        tool_name=None,
                        parameters={},
                        approval_required=False,
                    )
                ],
            )
        except Exception:
            return self._fallback_planner.plan(user_input)
