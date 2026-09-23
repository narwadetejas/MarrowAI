from __future__ import annotations

import json
from pathlib import Path
import pytest

from marrowai.assistant import MarrowAssistant
from marrowai.gui_automation import GUIAutomationExecutor
from marrowai.interfaces import ExecutionResult, TaskPlan
from marrowai.memory import MemoryStore
from marrowai.planner import RuleBasedPlanner
from marrowai.screen_vision import ScreenElement, ScreenVisionEngine
from marrowai.tools import (
    DailyContextTool,
    GUIActionTool,
    ScreenPerceptionTool,
    ToolRegistry,
    WindowManagementTool,
)


def test_screen_vision_engine_mocked():
    engine = ScreenVisionEngine()
    # Test text search logic on ScreenElements
    sample_elements = [
        ScreenElement("Terminal - bash", 0.98, [[10, 10], [100, 10], [100, 30], [10, 30]], 55, 20, 90, 20),
        ScreenElement("Save Document", 0.95, [[200, 100], [300, 100], [300, 140], [200, 140]], 250, 120, 100, 40),
        ScreenElement("Cancel", 0.92, [[320, 100], [380, 100], [380, 140], [320, 140]], 350, 120, 60, 40),
    ]

    engine.read_screen = lambda monitor_index=0: sample_elements

    matches = engine.find_text_on_screen("Save")
    assert len(matches) == 1
    assert matches[0].text == "Save Document"
    assert matches[0].center_x == 250
    assert matches[0].center_y == 120

    desc = engine.describe_screen()
    assert "Terminal - bash" in desc
    assert "Save Document" in desc


def test_gui_automation_executor_actions():
    executor = GUIAutomationExecutor()
    assert executor.is_available() is True

    # Test coordinate click returns structured result
    res_click = executor.execute_action("click", {"x": 50, "y": 50})
    assert res_click.status in {"success", "failed"}

    # Test keyboard typing returns structured result
    res_type = executor.execute_action("type", {"text": "hello marrowai"})
    assert res_type.status in {"success", "failed"}

    # Test hotkey combo
    res_hotkey = executor.execute_action("hotkey", {"combo": "ctrl+shift+t"})
    assert res_hotkey.status in {"success", "failed"}

    # Test scroll
    res_scroll = executor.execute_action("scroll", {"direction": "down", "amount": 2})
    assert res_scroll.status in {"success", "failed"}

    # Test window listing
    windows = executor.list_open_windows()
    assert isinstance(windows, list)

    # Test active window inspection
    active = executor.get_active_window()
    assert isinstance(active, dict)

    # Test tab listing
    tabs_info = executor.list_tabs()
    assert "active_window" in tabs_info
    assert "detected_tabs" in tabs_info


def test_daily_context_memory_store(tmp_path: Path):
    store = MemoryStore(path=str(tmp_path / "memory.json"))
    today = store.get_today_str()

    # Record multiple turns with metadata
    store.record_daily_turn(
        "user",
        "What applications are currently open?",
        details={"intent": "list_windows"},
    )
    store.record_daily_turn(
        "assistant",
        "You currently have Antigravity IDE and Terminal open.",
        details={"intent": "list_windows", "status": "success"},
    )
    store.record_daily_turn(
        "user",
        "Can you click on the Terminal window?",
        details={"intent": "focus_window"},
    )

    # Verify daily context file was created
    day_file = tmp_path / "daily_context" / f"{today}.json"
    assert day_file.exists()

    # Verify context review
    review = store.review_day_context()
    assert today in review
    assert "What applications are currently open?" in review
    assert "Antigravity IDE and Terminal" in review
    assert "click on the Terminal window" in review

    # Verify built prompt context contains today's review
    prompt_context = store.build_context("switch to it")
    assert "Daily Context Review for" in prompt_context
    assert "What applications are currently open?" in prompt_context
    assert "switch to it" in prompt_context

    # Verify list of available recorded days
    days = store.list_available_days()
    assert today in days


def test_tool_registry_and_new_tools(tmp_path: Path):
    registry = ToolRegistry()

    assert registry.has("screen_perception")
    assert registry.has("screen")
    assert registry.has("window_management")
    assert registry.has("windows")
    assert registry.has("tabs")
    assert registry.has("daily_context")
    assert registry.has("gui_action")

    # Screen tool describe
    screen_tool = registry.get("screen_perception")
    res = screen_tool.execute({"action": "describe_screen"})
    assert res.status == "success"

    # Window management list
    win_tool = registry.get("window_management")
    res_win = win_tool.execute({"action": "list_windows"})
    assert res_win.status == "success"

    # Daily context review
    mem_store = MemoryStore(path=str(tmp_path / "mem.json"))
    mem_store.record_daily_turn("user", "Testing daily review")
    daily_tool = DailyContextTool(memory_store=mem_store)
    res_daily = daily_tool.execute({"action": "review_today"})
    assert res_daily.status == "success"
    assert "Testing daily review" in res_daily.output


def test_planner_screen_gui_daily_rules():
    planner = RuleBasedPlanner()

    # 1. Screen perception query
    plan_screen = planner.plan("what is on my screen right now?")
    assert plan_screen.intent == "screen_perception"
    assert plan_screen.steps[0].tool_name == "screen_perception"
    assert plan_screen.steps[0].parameters["action"] == "describe_screen"

    # 2. Window listing query
    plan_win = planner.plan("what apps are open?")
    assert plan_win.intent == "list_windows"
    assert plan_win.steps[0].tool_name == "window_management"

    # 3. Tab query
    plan_tabs = planner.plan("which tabs are open?")
    assert plan_tabs.intent == "list_tabs"
    assert plan_tabs.steps[0].tool_name == "window_management"

    # 4. Tab switching
    plan_switch = planner.plan("switch tab")
    assert plan_switch.intent == "switch_tab"
    assert plan_switch.steps[0].tool_name == "window_management"

    # 5. Visual click
    plan_click = planner.plan("click on 'Submit'")
    assert plan_click.intent == "visual_click"
    assert plan_click.steps[0].tool_name == "gui_action"
    assert plan_click.steps[0].parameters["parameters"]["text"] == "Submit"

    # 6. Daily context review query
    plan_day = planner.plan("what was my previous question today?")
    assert plan_day.intent == "review_today_context"
    assert plan_day.steps[0].tool_name == "daily_context"
    assert plan_day.steps[0].parameters["action"] == "review_today"


def test_assistant_records_daily_turn(tmp_path: Path):
    from marrowai.model import OllamaProvider
    assistant = MarrowAssistant(
        model_provider=OllamaProvider(base_url="http://127.0.0.1:1"),
        memory_path=str(tmp_path / "mem.json"),
    )

    # Turn 1: ask what is on screen
    res1 = assistant.process("what is on my screen?")
    assert res1["status"] in {"success", "failed"}

    # Check that user and assistant turns are stored in daily context
    today = assistant.memory.get_today_str()
    day_ctx = assistant.memory.get_daily_context()
    turns = day_ctx.get("turns", [])
    assert len(turns) >= 2
    assert turns[0]["role"] == "user"
    assert "what is on my screen?" in turns[0]["message"]
    assert turns[1]["role"] == "assistant"

    # Turn 2: query previous question
    res2 = assistant.process("what was my previous question?")
    assert res2["status"] == "success"
    assert "what is on my screen?" in res2["output"]
