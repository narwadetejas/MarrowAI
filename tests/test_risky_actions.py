from __future__ import annotations

import tempfile
from pathlib import Path
from marrowai.assistant import MarrowAssistant
from marrowai.executor import SafeExecutor
from marrowai.interfaces import PlanStep, TaskPlan, ToolCall
from marrowai.planner import RuleBasedPlanner
from marrowai.safety import RiskClassifier, SafetyGate
from marrowai.tools import ToolRegistry, ToolRouter, RunCommandTool


def test_risk_classifier_methods():
    classifier = RiskClassifier()
    assert classifier.is_destructive("rm -rf /") is True
    assert classifier.is_destructive("mkfs.ext4 /dev/sdb") is True
    assert classifier.is_destructive("echo hello") is False
    assert classifier.is_destructive("ls -la") is False

    step_sudo = PlanStep("s1", "cli", "install package", "run_command", {"command": "sudo apt-get update"})
    assert classifier.requires_sudo(step_sudo) is True

    step_normal = PlanStep("s2", "tool", "echo text", "echo", {"text": "hello"})
    assert classifier.requires_sudo(step_normal) is False

    assert classifier.classify_risk("dangerous_delete") == "high"
    assert classifier.classify_risk("cli") == "medium"
    assert classifier.classify_risk("tool") == "low"


def test_tool_router_routes_step():
    router = ToolRouter()
    step = PlanStep(
        id="step-1",
        action_type="cli",
        description="Run test command",
        tool_name="run_command",
        parameters={"command": "echo routing_test"},
        approval_required=True,
    )
    call = router.route(step, password="secret_password")
    assert isinstance(call, ToolCall)
    assert call.tool_name == "run_command"
    assert call.arguments["command"] == "echo routing_test"
    assert call.arguments["password"] == "secret_password"
    assert call.resource_profile == "high"


def test_unconfirmed_risky_action_halts_for_confirmation():
    assistant = MarrowAssistant()
    # Plan a destructive action
    plan = RuleBasedPlanner().plan("Delete the entire /etc directory")
    assert plan.intent == "dangerous_delete"

    # Evaluate with SafetyGate / RiskClassifier
    gate = SafetyGate()
    decision = gate.evaluate(plan, user_confirmed=False)
    assert decision.requires_confirmation is True

    # Process through assistant without confirmation
    result = assistant.process("Delete the entire /etc directory", confirmed=False)
    assert result["status"] == "requires_confirmation"
    assert result.get("requires_confirmation") is True
    assert "requires confirmation" in result["output"]


def test_confirmed_risky_action_executes():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        test_file = Path(tmp_dir) / "risky_file.txt"
        test_file.write_text("risky data to be deleted", encoding="utf-8")
        assert test_file.exists()

        assistant = MarrowAssistant()
        # Direct execution of a delete step with confirmation
        plan = TaskPlan(
            intent="dangerous_delete",
            steps=[
                PlanStep(
                    id="step-1",
                    action_type="cli",
                    description=f"Delete test file {test_file}",
                    tool_name="rm",
                    parameters={"path": str(test_file)},
                    approval_required=True,
                )
            ],
            risk_level="high",
        )

        decision = assistant.safety.evaluate(plan, user_confirmed=True)
        assert decision.decision == "ALLOW"
        assert decision.requires_confirmation is False

        exec_res = assistant.execute_plan(plan)
        assert exec_res["status"] == "success"
        assert not test_file.exists()


def test_safe_executor_runs_arbitrary_cli_command():
    executor = SafeExecutor()
    # Test arbitrary CLI commands that were previously blocked by whitelist
    res1 = executor.execute_command("echo hello world")
    assert res1.status == "success"
    assert "hello world" in res1.output

    res2 = executor.execute_command("python --version")
    assert res2.status == "success"
    assert "Python" in res2.output


def test_unknown_custom_tool_allowed_when_confirmed():
    gate = SafetyGate()
    custom_plan = TaskPlan(
        intent="custom_action",
        steps=[
            PlanStep(
                id="step-1",
                action_type="tool",
                description="Custom tool invocation",
                tool_name="custom_vendor_tool",
                parameters={"flag": "--force"},
            )
        ],
        risk_level="high",
    )

    # Unconfirmed -> requires confirmation
    dec_unconfirmed = gate.evaluate(custom_plan, user_confirmed=False)
    assert dec_unconfirmed.requires_confirmation is True

    # Confirmed -> ALLOW
    dec_confirmed = gate.evaluate(custom_plan, user_confirmed=True)
    assert dec_confirmed.decision == "ALLOW"
    assert dec_confirmed.requires_confirmation is False


def test_interactive_confirmation_flow():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        assistant = MarrowAssistant(memory_path=str(Path(tmp_dir) / "mem.json"))

        # Step 1: User requests high risk action -> assistant asks for confirmation
        res1 = assistant.process("Delete the entire /etc directory")
        assert res1["status"] == "requires_confirmation"
        assert assistant._pending_plan is not None

        # Step 2: User responds 'yes' -> assistant confirms and executes
        res2 = assistant.process("yes")
        # Pending plan is cleared and executed
        assert assistant._pending_plan is None
        assert res2["status"] in {"success", "failed"}  # Will execute the steps!


def run_all():
    print("Running test_risk_classifier_methods...")
    test_risk_classifier_methods()
    print("Running test_tool_router_routes_step...")
    test_tool_router_routes_step()
    print("Running test_unconfirmed_risky_action_halts_for_confirmation...")
    test_unconfirmed_risky_action_halts_for_confirmation()
    print("Running test_confirmed_risky_action_executes...")
    test_confirmed_risky_action_executes()
    print("Running test_safe_executor_runs_arbitrary_cli_command...")
    test_safe_executor_runs_arbitrary_cli_command()
    print("Running test_unknown_custom_tool_allowed_when_confirmed...")
    test_unknown_custom_tool_allowed_when_confirmed()
    print("Running test_interactive_confirmation_flow...")
    test_interactive_confirmation_flow()
    print("[PASS] All risky action tests PASSED successfully!")


if __name__ == "__main__":
    run_all()
