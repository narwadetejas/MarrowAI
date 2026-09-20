from __future__ import annotations

from unittest.mock import patch, MagicMock
from marrowai.assistant import MarrowAssistant
from marrowai.planner import RuleBasedPlanner
from marrowai.safety import SafetyGate
from marrowai.tools import DesktopActionTool, ToolRegistry
from marrowai.voice_engine import OfflineVoiceEngine


def test_planner_youtube_intent():
    planner = RuleBasedPlanner()
    plan = planner.plan("i want to watchh youtuuube , oprm it")
    assert plan.intent == "watch_youtube"
    assert plan.risk_level == "low"
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "desktop_action"
    assert plan.steps[0].parameters["action"] == "open_url"
    assert "youtube.com" in plan.steps[0].parameters["target"]


def test_planner_file_manager_intent():
    planner = RuleBasedPlanner()
    plan = planner.plan("open file manager")
    assert plan.intent == "open_file_manager"
    assert plan.risk_level == "low"
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "desktop_action"
    assert plan.steps[0].parameters["action"] == "open_file_manager"


def test_planner_appcenter_download_chromium_intent():
    planner = RuleBasedPlanner()
    plan = planner.plan("open appcenter and downlaod chromium browser")
    assert plan.intent == "install_package"
    assert plan.risk_level == "low"
    assert len(plan.steps) >= 1
    tool_names = [s.tool_name for s in plan.steps]
    assert "desktop_action" in tool_names


def test_planner_uninstall_application_requires_confirmation():
    planner = RuleBasedPlanner()
    plan = planner.plan("delete application firefox")
    assert plan.intent == "run_command"
    assert plan.risk_level == "high"
    assert plan.steps[0].approval_required is True
    assert "sudo apt-get remove -y firefox" in plan.steps[0].parameters["command"]

    gate = SafetyGate()
    decision = gate.evaluate(plan)
    assert decision.decision == "REVIEW"
    assert decision.requires_confirmation is True


def test_safety_gate_allows_desktop_action():
    planner = RuleBasedPlanner()
    plan = planner.plan("open file manager")
    gate = SafetyGate()
    decision = gate.evaluate(plan)
    assert decision.decision == "ALLOW"
    assert decision.requires_confirmation is False


def test_desktop_action_tool_open_url():
    tool = DesktopActionTool()
    with patch("webbrowser.open") as mock_open:
        res = tool.execute({"action": "open_url", "target": "https://www.youtube.com"})
        assert res.status == "success"
        assert "youtube.com" in res.output


def test_desktop_action_tool_open_file_manager():
    tool = DesktopActionTool()
    res = tool.execute({"action": "open_file_manager", "target": "."})
    assert res.status == "success"


def test_desktop_action_tool_invalid_package():
    tool = DesktopActionTool()
    res = tool.execute({"action": "install_package", "package_name": "rm -rf /; evil"})
    assert res.status == "blocked"


def test_assistant_processes_file_manager():
    assistant = MarrowAssistant()
    with patch.object(assistant.executor, "execute_tool") as mock_exec:
        from marrowai.interfaces import ExecutionResult
        mock_exec.return_value = ExecutionResult("success", "Opened file manager", 0)
        res = assistant.process("open file manager")
        assert res["decision"] == "ALLOW"
        assert res["status"] == "success"


def test_voice_engine_offline_wav_synthesis():
    engine = OfflineVoiceEngine()
    with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run, patch("builtins.open") as mock_open, patch("os.path.exists", return_value=True):
        mock_which.side_effect = lambda b: "/usr/bin/espeak-ng" if b == "espeak-ng" else None
        mock_run.return_value = MagicMock(returncode=0)
        mock_open.return_value.__enter__.return_value.read.return_value = b"RIFFfake-wav-bytes"

        wav = engine.synthesize_offline_wav("Test voice output", "indian_female")
        assert wav == b"RIFFfake-wav-bytes"


def test_assistant_confirmation_flow_proceeds_with_password():
    assistant = MarrowAssistant()
    # Step 1: Initial high-risk request halts for confirmation
    step1_res = assistant.process("delete application firefox")
    assert step1_res["status"] == "requires_confirmation"
    assert assistant._pending_plan is not None

    # Step 2: Confirming with password executes and forwards password
    with patch.object(assistant.executor, "execute_tool") as mock_exec:
        from marrowai.interfaces import ExecutionResult
        mock_exec.return_value = ExecutionResult("success", "Package firefox uninstalled", 0)
        step2_res = assistant.process("yes", confirmed=True, password="mypassword123")
        assert step2_res["status"] == "success"
        assert "uninstalled" in step2_res["output"]
        assert mock_exec.called
        call_params = mock_exec.call_args[0][1]
        assert call_params.get("password") == "mypassword123"

