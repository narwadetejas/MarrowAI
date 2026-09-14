from __future__ import annotations

from marrowai.model import ModelProvider, OllamaProvider


def test_model_provider_interface_is_defined():
    assert issubclass(ModelProvider, object)


def test_ollama_provider_falls_back_to_rule_based_planner_when_server_unavailable():
    provider = OllamaProvider(base_url="http://127.0.0.1:1")
    plan = provider.generate_plan("List the files in the current workspace")

    assert plan.intent == "list_files"
    assert plan.steps[0].tool_name == "ls"


def test_ollama_provider_reports_server_availability():
    provider = OllamaProvider(base_url="http://127.0.0.1:1")
    assert provider.is_available() is False
