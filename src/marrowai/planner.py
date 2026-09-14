from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanStep:
    id: str
    action_type: str
    description: str
    tool_name: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    approval_required: bool = False


@dataclass
class TaskPlan:
    intent: str
    steps: list[PlanStep]
    risk_level: str = "low"


class RuleBasedPlanner:
    """Simple planner that maps a narrow set of tasks into a safe structured plan."""

    def plan(self, user_input: str) -> TaskPlan:
        text = user_input.strip().lower()

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

        return TaskPlan(
            intent="unknown",
            steps=[
                PlanStep(
                    id="step-1",
                    action_type="question",
                    description="Ask for clarification because the request is not in the supported MVP command set",
                    tool_name=None,
                    parameters={},
                    approval_required=False,
                )
            ],
            risk_level="medium",
        )
