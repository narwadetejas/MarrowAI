from __future__ import annotations

from dataclasses import dataclass

from .planner import TaskPlan


@dataclass
class SafetyDecision:
    decision: str
    reason: str
    confidence: float
    requires_confirmation: bool = False


class SafetyGate:
    """Risk gate for plan validation before execution."""

    allowed_tools = {"ls", "list_files", "echo", "run_tests", "scaffold_backend"}

    def evaluate(self, plan: TaskPlan) -> SafetyDecision:
        if plan.intent == "dangerous_delete":
            return SafetyDecision(
                decision="DENY",
                reason="High-risk destructive action is blocked by policy.",
                confidence=0.99,
                requires_confirmation=False,
            )

        unknown_tools = {
            step.tool_name for step in plan.steps if step.tool_name and step.tool_name not in self.allowed_tools
        }
        if unknown_tools:
            return SafetyDecision(
                decision="DENY",
                reason=f"Unknown tools are blocked: {', '.join(sorted(unknown_tools))}.",
                confidence=0.99,
                requires_confirmation=False,
            )

        if plan.risk_level == "high":
            return SafetyDecision(
                decision="REVIEW",
                reason="High-risk action requires explicit confirmation.",
                confidence=0.8,
                requires_confirmation=True,
            )

        if plan.risk_level == "medium":
            return SafetyDecision(
                decision="REVIEW",
                reason="Action requires a human confirmation before execution.",
                confidence=0.7,
                requires_confirmation=True,
            )

        return SafetyDecision(
            decision="ALLOW",
            reason="Safe action within the current MVP policy.",
            confidence=0.95,
            requires_confirmation=False,
        )
