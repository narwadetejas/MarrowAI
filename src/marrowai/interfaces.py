from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class UserInput:
    text: str | None = None
    audio: bytes | None = None
    source: str = "text"
    metadata: dict[str, str] = field(default_factory=dict)


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
    steps: list[PlanStep] = field(default_factory=list)
    risk_level: str = "low"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    constraints: list[str] = field(default_factory=list)


@dataclass
class SafetyDecision:
    decision: str
    reason: str
    confidence: float
    requires_confirmation: bool = False


@dataclass
class ToolCall:
    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 20
    resource_profile: str = "standard"


@dataclass
class ExecutionResult:
    status: str
    output: str
    exit_code: int | None = None
    logs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class SystemTelemetry:
    cpu_percent: float = 0.0
    memory_available_mb: float = 0.0
    memory_percent: float = 0.0
    load_average: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    is_healthy: bool = True
    details: str = "System healthy"
