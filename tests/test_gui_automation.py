from __future__ import annotations

from marrowai.gui_automation import GUIAutomationExecutor
from marrowai.tools import GUIActionTool


def test_gui_automation_executor_creation():
    executor = GUIAutomationExecutor()
    assert executor is not None
    # On headless/WSL without xdotool, is_available is properly False
    available = executor.is_available()
    assert isinstance(available, bool)


def test_gui_automation_handles_unavailable_backend():
    executor = GUIAutomationExecutor()
    # If no display or tool, returns a structured failure without crashing
    res = executor.execute_action("click", {"x": 10, "y": 20})
    assert res is not None
    assert res.status in {"success", "failed"}


def test_gui_action_tool_in_registry():
    tool = GUIActionTool()
    assert tool.name == "gui_action"
    res = tool.execute({"action": "unknown_action"})
    assert res.status in {"failed", "blocked"}
