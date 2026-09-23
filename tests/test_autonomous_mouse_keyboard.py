from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from marrowai.gui_automation import GUIAutomationExecutor
from marrowai.tools import GUIActionTool, ToolRegistry, ToolRouter
from marrowai.executor import SafeExecutor
from marrowai.planner import RuleBasedPlanner
from marrowai.interfaces import PlanStep


def test_mouse_hover_and_coordinates():
    executor = GUIAutomationExecutor()
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        res = executor.hover(350, 450, duration=0.1)
        assert res.status == "success"
        assert "(350, 450)" in res.output


def test_mouse_hover_text():
    executor = GUIAutomationExecutor()
    mock_el = MagicMock()
    mock_el.text = "Search"
    mock_el.center_x = 400
    mock_el.center_y = 200
    mock_el.confidence = 0.95

    with patch.object(executor.vision, "find_text_on_screen", return_value=[mock_el]), \
         patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        res = executor.hover_text("Search", duration=0.1)
        assert res.status == "success"
        assert "Search" in res.output
        assert "(400, 200)" in res.output


def test_window_aware_type_and_hotkeys():
    executor = GUIAutomationExecutor()
    with patch.object(executor, "focus_window") as mock_focus, \
         patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        # Type with target_window focuses target window first
        res = executor.execute_action("type", {"text": "hello autonomous linux", "target_window": "Chrome"})
        assert res.status == "success"
        mock_focus.assert_called_with("Chrome")

        # Hotkey execution
        res2 = executor.execute_action("hotkey", {"combo": "ctrl+t"})
        assert res2.status == "success"
        assert "ctrl+t" in res2.output


def test_tool_registry_gui_aliases():
    registry = ToolRegistry()
    for alias in ["click", "hover", "hover_text", "type", "key", "hotkey", "scroll"]:
        assert registry.has(alias)
        tool = registry.get(alias)
        assert isinstance(tool, GUIActionTool)


def test_safe_executor_allows_mouse_and_keyboard():
    executor = SafeExecutor()
    for tool in ["click", "hover", "hover_text", "type", "key", "hotkey", "scroll", "browser_search_and_play"]:
        assert tool in executor.allowed_tools


def test_planner_hover_and_coordinate_clicks():
    planner = RuleBasedPlanner()

    # Coordinate click
    p1 = planner.plan("click at (500, 300)")
    assert p1.intent == "coordinate_click"
    assert p1.steps[0].tool_name == "gui_action"
    assert p1.steps[0].parameters["action"] == "click"
    assert p1.steps[0].parameters["parameters"]["x"] == 500
    assert p1.steps[0].parameters["parameters"]["y"] == 300

    # Hover at coordinate
    p2 = planner.plan("hover at 450, 600")
    assert p2.intent == "hover_mouse"
    assert p2.steps[0].parameters["action"] == "hover"
    assert p2.steps[0].parameters["parameters"]["x"] == 450

    # Hover over visual text
    p3 = planner.plan("hover over Search")
    assert p3.intent == "hover_mouse"
    assert p3.steps[0].parameters["action"] == "hover_text"
    assert p3.steps[0].parameters["parameters"]["text"] == "Search"

    # Hotkey trigger
    p4 = planner.plan("trigger hotkey ctrl+w")
    assert p4.intent == "trigger_hotkey"
    assert p4.steps[0].parameters["parameters"]["combo"] == "ctrl+w"

    # Key press
    p5 = planner.plan("press key Return")
    assert p5.intent == "press_key"
    assert p5.steps[0].parameters["parameters"]["key"] == "Return"
