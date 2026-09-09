"""Offline planning boundary.

The deterministic planner is a safe bootstrap adapter, not the final AI model.
A real offline model, including any model called Astra, must implement this
contract only after its exact runtime and license are approved.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Plan:
    request: str
    operation: str
    risk_tier: str
    executable: bool
    explanation: str


class OfflinePlanner:
    """Plan a small safe command set without network access or shell execution."""

    SAFE_OPERATIONS = {
        "show memory pressure": "cat /proc/pressure/memory",
        "show system uptime": "uptime",
        "show disk usage": "df -h",
    }

    def plan(self, request: str) -> Plan:
        normalized = " ".join(request.lower().split())
        operation = self.SAFE_OPERATIONS.get(normalized)
        if operation:
            return Plan(
                request=request,
                operation=operation,
                risk_tier="safe",
                executable=True,
                explanation="Matched a built-in read-only Ubuntu diagnostic.",
            )
        return Plan(
            request=request,
            operation="",
            risk_tier="destructive" if any(
                word in normalized for word in ("delete", "remove", "format", "kill")
            ) else "moderate",
            executable=False,
            explanation=(
                "No executable offline adapter is configured for this request. "
                "The action was not run."
            ),
        )

    @staticmethod
    def to_json(plan: Plan) -> str:
        return json.dumps(asdict(plan), sort_keys=True)
