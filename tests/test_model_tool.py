from __future__ import annotations

from marrowai.tools import ManageModelsTool


def test_manage_models_tool_status():
    tool = ManageModelsTool()
    assert tool.name == "manage_models"

    status_res = tool.execute({"action": "status"})
    assert status_res.status == "success"
    assert "Ollama daemon:" in status_res.output


def test_manage_models_tool_list():
    tool = ManageModelsTool()
    list_res = tool.execute({"action": "list"})
    assert list_res.status == "success"
    assert "models" in list_res.output.lower() or "ollama" in list_res.output.lower()


def test_manage_models_tool_missing_name():
    tool = ManageModelsTool()
    pull_res = tool.execute({"action": "pull", "model_name": ""})
    assert pull_res.status == "blocked"
    assert "No model name specified" in pull_res.output


def test_manage_models_tool_pull_offline_handling():
    tool = ManageModelsTool()
    # Offline or missing endpoint should return a graceful failure with actionable advice, never unhandled crash
    pull_res = tool.execute({"action": "pull", "model_name": "test-model-abc"})
    assert pull_res.status in {"success", "failed"}
    assert "test-model-abc" in pull_res.output
