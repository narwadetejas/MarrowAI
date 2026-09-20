from __future__ import annotations

from marrowai.interfaces import (
    ExecutionResult,
    PlanStep,
    SafetyDecision,
    SystemTelemetry,
    TaskPlan,
    ToolCall,
    UserInput,
)


def test_user_input_defaults():
    inp = UserInput(text="hello")
    assert inp.text == "hello"
    assert inp.source == "text"
    assert inp.audio is None
    assert inp.metadata == {}


def test_plan_step_and_task_plan():
    step = PlanStep(
        id="step-1",
        action_type="cli",
        description="List files",
        tool_name="ls",
        parameters={"path": "."},
    )
    plan = TaskPlan(
        intent="list_files",
        steps=[step],
        risk_level="low",
    )
    assert plan.intent == "list_files"
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "ls"
    assert plan.risk_level == "low"
    assert plan.id is not None


def test_safety_decision():
    dec = SafetyDecision(
        decision="ALLOW",
        reason="safe",
        confidence=0.95,
        requires_confirmation=False,
    )
    assert dec.decision == "ALLOW"
    assert dec.confidence == 0.95


def test_tool_call_and_execution_result():
    call = ToolCall(tool_name="echo", arguments={"text": "hi"})
    assert call.tool_name == "echo"
    assert call.timeout_seconds == 20

    res = ExecutionResult(status="success", output="hi", exit_code=0)
    assert res.status == "success"
    assert res.output == "hi"
    assert res.exit_code == 0


def test_system_telemetry():
    telemetry = SystemTelemetry(
        cpu_percent=12.5,
        memory_available_mb=4096.0,
        memory_percent=35.0,
        load_average=[0.5, 0.4, 0.3],
        is_healthy=True,
    )
    assert telemetry.is_healthy is True
    assert telemetry.cpu_percent == 12.5
    assert telemetry.memory_available_mb == 4096.0
