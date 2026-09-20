from __future__ import annotations

from marrowai.planner import RuleBasedPlanner
from marrowai.tools import SystemStatusTool


def test_system_status_tool():
    tool = SystemStatusTool()
    assert tool.name == "system_status"
    res = tool.execute({})
    assert res.status == "success"
    assert "System Status Overview:" in res.output
    assert "Platform:" in res.output
    assert "CPU Usage:" in res.output
    assert "RAM Headroom:" in res.output


def test_planner_maps_vm_creation():
    planner = RuleBasedPlanner()
    plan = planner.plan("download a virtual machine and create an ubuntu os in vm")
    assert plan.intent == "create_ubuntu_vm"
    assert len(plan.steps) == 2
    assert plan.steps[0].tool_name == "manage_vm"
    assert plan.steps[0].parameters["action"] == "ensure"
    assert plan.steps[1].tool_name == "manage_vm"
    assert plan.steps[1].parameters["action"] == "create"


def test_planner_maps_model_download():
    planner = RuleBasedPlanner()
    plan = planner.plan("download model llama3.2")
    assert plan.intent == "download_model"
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "manage_models"
    assert plan.steps[0].parameters["action"] == "pull"
    assert plan.steps[0].parameters["model_name"] == "llama3.2"


def test_planner_maps_model_list():
    planner = RuleBasedPlanner()
    plan = planner.plan("what models do I have installed?")
    assert plan.intent == "list_models"
    assert plan.steps[0].tool_name == "manage_models"
    assert plan.steps[0].parameters["action"] == "list"


def test_planner_maps_system_status():
    planner = RuleBasedPlanner()
    plan = planner.plan("what is the system status and health?")
    assert plan.intent == "system_status"
    assert plan.steps[0].tool_name == "system_status"


def test_planner_maps_arch_vm_creation():
    planner = RuleBasedPlanner()
    plan = planner.plan("create an arch linux vm")
    assert plan.intent == "create_arch_vm"
    assert len(plan.steps) == 2
    assert plan.steps[0].tool_name == "manage_vm"
    assert plan.steps[0].parameters["action"] == "ensure"
    assert plan.steps[0].parameters["os_type"] == "arch"
    assert plan.steps[1].tool_name == "manage_vm"
    assert plan.steps[1].parameters["action"] == "create"
    assert plan.steps[1].parameters["os_type"] == "arch"

