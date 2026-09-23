from __future__ import annotations

from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from marrowai.assistant import MarrowAssistant
from marrowai.memory import MemoryStore
from marrowai.planner import RuleBasedPlanner
from marrowai.tools import DesktopActionTool, GUIActionTool, ToolRegistry, ToolRouter, WindowManagementTool


def test_prompt_1_open_libre_writer_essay():
    planner = RuleBasedPlanner()
    plan = planner.plan("open libre writer and write a small essay on any topic")
    assert plan.intent == "write_essay_libreoffice"
    assert len(plan.steps) == 3
    # Step 1: launch LibreOffice Writer
    assert plan.steps[0].tool_name == "desktop_action"
    assert plan.steps[0].parameters["action"] == "launch_app"
    assert "writer" in plan.steps[0].parameters["app_name"]
    # Step 2: short delay for focus
    assert plan.steps[1].tool_name == "run_command"
    assert "sleep" in plan.steps[1].parameters["command"]
    # Step 3: type essay
    assert plan.steps[2].tool_name == "gui_action"
    assert plan.steps[2].parameters["action"] == "type"
    assert "parameters" in plan.steps[2].parameters
    assert "Artificial Intelligence" in plan.steps[2].parameters["parameters"]["text"]


def test_prompt_2_write_selection_sort_in_editor():
    planner = RuleBasedPlanner()
    # Note typo in user input: "sellection sort"
    plan = planner.plan("write a code for sellection sort in suitable editor or app")
    assert plan.intent == "write_code_in_editor"
    assert len(plan.steps) == 2
    # Step 1: write python file
    assert plan.steps[0].tool_name == "write_file"
    assert plan.steps[0].parameters["path"] == "selection_sort.py"
    assert "def selection_sort" in plan.steps[0].parameters["content"]
    # Step 2: launch editor
    assert plan.steps[1].tool_name == "desktop_action"
    assert plan.steps[1].parameters["action"] == "launch_app"
    assert "gedit" in plan.steps[1].parameters["app_name"]


def test_prompt_3_close_antigravity_ide_tab_with_typo():
    planner = RuleBasedPlanner()
    # User typo: "close thw antigravity ide tab"
    plan = planner.plan("close thw antigravity ide tab")
    assert plan.intent == "close_tab"
    assert len(plan.steps) == 2
    # Step 1: focus window
    assert plan.steps[0].tool_name == "window_management"
    assert plan.steps[0].parameters["action"] == "focus_window"
    assert "antigravity ide" in plan.steps[0].parameters["target"]
    # Step 2: close tab in that window
    assert plan.steps[1].tool_name == "window_management"
    assert plan.steps[1].parameters["action"] == "close_tab"
    assert "antigravity ide" in plan.steps[1].parameters["target"]


def test_claude_style_thought_process_generation():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        assistant = MarrowAssistant(memory_path=str(Path(tmp_dir) / "mem.json"))
        planner = RuleBasedPlanner()
        plan = planner.plan("write a code for sellection sort in suitable editor or app")

        thoughts = assistant.generate_thought_process(
            "write a code for sellection sort in suitable editor or app",
            plan,
        )
        assert "🧠 MarrowAI Thought Process:" in thoughts
        assert "• Intent Analysis:" in thoughts
        assert "• Context & Environment:" in thoughts
        assert "• Strategy & Steps:" in thoughts
        assert "• Safety Policy Check:" in thoughts
        assert "selection_sort.py" in thoughts


def test_on_thinking_callback_invocation():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        assistant = MarrowAssistant(memory_path=str(Path(tmp_dir) / "mem.json"))

        captured_thoughts = []
        captured_narrations = []

        def on_thinking(t: str) -> None:
            captured_thoughts.append(t)

        def on_narration(n: str) -> None:
            captured_narrations.append(n)

        with patch("subprocess.Popen") as mock_popen, patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_run.return_value = mock_proc

            res = assistant.process(
                "write a code for sellection sort in suitable editor or app",
                on_narration=on_narration,
                on_thinking=on_thinking,
            )

        assert res["status"] == "success"
        assert len(captured_thoughts) >= 1
        assert "🧠 MarrowAI Thought Process:" in captured_thoughts[0]
        assert Path("selection_sort.py").exists()
        if Path("selection_sort.py").exists():
            Path("selection_sort.py").unlink()


def test_daily_context_session_sidebar_features():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        mem = MemoryStore(path=str(Path(tmp_dir) / "mem.json"))
        today = mem.get_today_str()

        mem.record_daily_turn("user", "open libre writer and write a small essay on any topic")
        mem.record_daily_turn("assistant", "Launched LibreOffice Writer and typed essay.", details={"intent": "write_essay_libreoffice", "status": "success"})

        # Verify today's review
        review = mem.review_day_context()
        assert today in review
        assert "open libre writer" in review
        assert "Launched LibreOffice Writer" in review

        # Verify available days listing
        days = mem.list_available_days()
        assert today in days


def test_prompt_4_watch_sanam_re_song_video_on_youtube():
    planner = RuleBasedPlanner()
    plan = planner.plan("i want to watch sanam re song video on youtube")
    assert plan.intent == "watch_youtube"
    assert len(plan.steps) == 3
    # Step 1: Direct YouTube search URL in browser
    assert plan.steps[0].tool_name == "desktop_action"
    assert plan.steps[0].parameters["action"] == "open_url"
    assert "youtube.com/results?search_query=" in plan.steps[0].parameters["target"]
    assert "sanam+re" in plan.steps[0].parameters["target"]
    # Step 2: Window focus onto browser
    assert plan.steps[1].tool_name == "window_management"
    assert plan.steps[1].parameters["action"] == "focus_window"
    # Step 3: Autonomous search and playback
    assert plan.steps[2].tool_name == "gui_action"
    assert plan.steps[2].parameters["action"] == "browser_search_and_play"
    assert "sanam re" in plan.steps[2].parameters["parameters"]["query"]
