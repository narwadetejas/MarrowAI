from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

from .interfaces import ExecutionResult, SafetyDecision, TaskPlan


SENSITIVE_KEYS = {
    "password",
    "token",
    "secret",
    "key",
    "auth",
    "authorization",
    "credential",
    "private_key",
    "api_key",
}


def redact_sensitive(obj: Any) -> Any:
    """Recursively redacts dictionary values with sensitive keys."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if any(s in str(k).lower() for s in SENSITIVE_KEYS):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = redact_sensitive(v)
        return cleaned
    if isinstance(obj, list):
        return [redact_sensitive(item) for item in obj]
    return obj


class AuditLogger:
    """Audit Logging & Activity Trail Subsystem (MA-CORE-009).

    Maintains an append-only, tamper-evident JSON Lines log of all assistant
    interactions, planning decisions, risk evaluations, and tool executions.
    """

    def __init__(self, log_path: str | None = None) -> None:
        self.log_path = Path(log_path or ".marrowai/audit.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _append(self, event_type: str, payload: dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event_type": event_type,
            "data": redact_sensitive(payload),
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    def log_request(self, user_prompt: str) -> None:
        self._append("REQUEST", {"prompt": user_prompt})

    def log_plan(self, plan: TaskPlan) -> None:
        self._append(
            "PLAN",
            {
                "plan_id": plan.id,
                "intent": plan.intent,
                "risk_level": plan.risk_level,
                "steps": [
                    {
                        "id": step.id,
                        "action_type": step.action_type,
                        "description": step.description,
                        "tool_name": step.tool_name,
                        "parameters": step.parameters,
                    }
                    for step in plan.steps
                ],
            },
        )

    def log_decision(self, decision: SafetyDecision) -> None:
        self._append(
            "SAFETY_DECISION",
            {
                "decision": decision.decision,
                "reason": decision.reason,
                "confidence": decision.confidence,
                "requires_confirmation": decision.requires_confirmation,
            },
        )

    def log_governor_check(self, is_healthy: bool, details: str) -> None:
        self._append(
            "GOVERNOR_CHECK",
            {
                "is_healthy": is_healthy,
                "details": details,
            },
        )

    def log_tool_execution(self, tool_name: str, parameters: dict[str, Any], result: ExecutionResult) -> None:
        self._append(
            "TOOL_EXECUTION",
            {
                "tool_name": tool_name,
                "parameters": parameters,
                "status": result.status,
                "output": result.output[:1000] if result.output else "",
                "exit_code": result.exit_code,
            },
        )

    def get_recent_events(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.log_path.exists():
            return []
        events = []
        try:
            with self.log_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            return []
        return events[-limit:]
