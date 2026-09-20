from __future__ import annotations

import time
from marrowai.assistant import MarrowAssistant
from marrowai.planner import RuleBasedPlanner
from marrowai.safety import SafetyGate
from marrowai.tools import RunCommandTool, ToolRegistry
from marrowai.voice_engine import OfflineVoiceEngine


def test_run_command_tool_executes_successfully():
    tool = RunCommandTool()
    result = tool.execute({"command": "echo marrow_execution_test"})

    assert result.status == "success"
    assert "marrow_execution_test" in result.output
    assert result.exit_code == 0


def test_tool_registry_contains_run_command_and_aliases():
    registry = ToolRegistry()
    assert registry.has("run_command")
    assert registry.has("system_exec")
    assert registry.has("bash")
    assert registry.has("rm")
    assert registry.has("delete_file")


def test_planner_maps_universal_commands():
    planner = RuleBasedPlanner()

    p1 = planner.plan("run command uname -a")
    assert p1.intent == "run_command"
    assert p1.risk_level == "low"
    assert p1.steps[0].tool_name == "run_command"
    assert p1.steps[0].parameters["command"] == "uname -a"

    p2 = planner.plan("check disk space")
    assert p2.intent == "run_command"
    assert p2.steps[0].parameters["command"] == "df -h"

    p3 = planner.plan("check memory")
    assert p3.intent == "run_command"
    assert p3.steps[0].parameters["command"] == "free -h"

    p4 = planner.plan("sudo apt update")
    assert p4.intent == "run_command"
    assert p4.risk_level == "high"
    assert p4.steps[0].approval_required is True


def test_safety_gate_confirmation_escalation():
    gate = SafetyGate()
    planner = RuleBasedPlanner()

    high_risk_plan = planner.plan("sudo systemctl restart nginx")
    assert high_risk_plan.risk_level == "high"

    # Unconfirmed -> requires confirmation
    decision_unconfirmed = gate.evaluate(high_risk_plan, user_confirmed=False)
    assert decision_unconfirmed.requires_confirmation is True

    # Confirmed -> Allowed without restriction
    decision_confirmed = gate.evaluate(high_risk_plan, user_confirmed=True)
    assert decision_confirmed.decision == "ALLOW"
    assert decision_confirmed.confidence == 1.0

    # Password supplied -> Allowed without restriction
    decision_pw = gate.evaluate(high_risk_plan, password="admin_sudo_pass")
    assert decision_pw.decision == "ALLOW"
    assert decision_pw.confidence == 1.0


def test_assistant_escalates_and_completes_work(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assistant = MarrowAssistant(
        model_provider=__import__("marrowai.model", fromlist=["OllamaProvider"]).OllamaProvider(
            base_url="http://127.0.0.1:1"
        ),
        memory_path=str(tmp_path / "memory.json"),
    )

    target_file = tmp_path / "test_exec.txt"
    create_cmd = f"echo test_content > {target_file.name}"

    # Safe command executes immediately
    res_safe = assistant.process(f"run command {create_cmd}")
    assert res_safe["status"] == "success"
    assert target_file.is_file()
    assert "test_content" in target_file.read_text()

    # Destructive / high-risk command requires confirmation
    res_delete = assistant.process(f"run command rm -f {target_file.name}")
    assert res_delete["status"] == "requires_confirmation"
    assert target_file.is_file()  # Not yet deleted

    # User confirms with 'yes' -> proceeds and completes the work!
    res_confirm = assistant.process("yes")
    assert res_confirm["status"] == "success"
    assert not target_file.is_file()  # Successfully deleted after confirmation


def test_audio_cache_low_latency_replay():
    engine = OfflineVoiceEngine(profile="indian_female")
    text = "Low latency caching test for MarrowAI speech synthesis."

    # First call - cache miss
    t0 = time.perf_counter()
    audio1 = engine.synthesize_neural_audio(text, "indian_female")
    elapsed1 = time.perf_counter() - t0

    if audio1 is not None:
        # Second call - LRU cache hit (should be near instantaneous, <10ms)
        t1 = time.perf_counter()
        audio2 = engine.synthesize_neural_audio(text, "indian_female")
        elapsed2 = time.perf_counter() - t1

        assert audio1 == audio2
        assert elapsed2 < 0.05  # Ultra-fast sub-50ms (usually <1ms)
