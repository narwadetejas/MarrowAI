from __future__ import annotations

from marrowai.executor import SafeExecutor
from marrowai.assistant import MarrowAssistant
from marrowai.safety import SafetyGate
from marrowai.planner import RuleBasedPlanner
from marrowai.planner import PlanStep, TaskPlan


def test_plan_generation_for_safe_task():
    planner = RuleBasedPlanner()
    plan = planner.plan("List the files in the current workspace")

    assert plan.intent == "list_files"
    assert len(plan.steps) >= 1
    assert plan.steps[0].tool_name == "ls"


def test_safety_gate_allows_safe_action():
    gate = SafetyGate()
    plan = RuleBasedPlanner().plan("List the files in the current workspace")
    decision = gate.evaluate(plan)

    assert decision.decision == "ALLOW"


def test_safety_gate_denies_dangerous_action():
    gate = SafetyGate()
    plan = RuleBasedPlanner().plan("Delete the entire /etc directory")
    decision = gate.evaluate(plan)

    assert decision.decision == "DENY"


def test_safe_executor_runs_echo_successfully():
    executor = SafeExecutor()
    result = executor.execute_command("echo marrowai")

    assert result.status == "success"
    assert "marrowai" in result.output


def test_planner_builds_ordered_autonomous_backend_workflow():
    plan = RuleBasedPlanner().plan("Create a FastAPI backend and run its tests")

    assert plan.intent == "create_backend_project"
    assert [step.tool_name for step in plan.steps] == ["scaffold_backend", "run_tests"]


def test_safety_gate_blocks_unknown_tools():
    plan = TaskPlan(
        intent="unknown_tool",
        steps=[PlanStep("step-1", "tool", "Do something", "delete_everything")],
    )

    decision = SafetyGate().evaluate(plan)

    assert decision.decision == "DENY"


def test_safe_executor_lists_files_without_shell_interpolation(tmp_path):
    (tmp_path / "example.txt").write_text("hello", encoding="utf-8")

    result = SafeExecutor().execute_tool("list_files", {"path": str(tmp_path)})

    assert result.status == "success"
    assert result.output == "example.txt"


def test_assistant_completes_backend_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assistant = MarrowAssistant(
        model_provider=__import__("marrowai.model", fromlist=["OllamaProvider"]).OllamaProvider(
            base_url="http://127.0.0.1:1"
        ),
        memory_path=str(tmp_path / "memory.json"),
    )

    result = assistant.process("Create a FastAPI backend and run its tests")

    assert result["status"] == "success"
    assert (tmp_path / "backend_project" / "app.py").is_file()
