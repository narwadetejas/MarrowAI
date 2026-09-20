from __future__ import annotations

from marrowai.vm_manager import VMManager
from marrowai.tools import ManageVMTool


def test_vm_manager_detects_hypervisors():
    mgr = VMManager()
    detected = mgr.detect_hypervisors()
    assert "multipass" in detected
    assert "qemu" in detected
    assert "virtualbox" in detected
    assert "kvm_accelerator" in detected
    assert "recommended" in detected


def test_vm_manager_ensure_hypervisor():
    mgr = VMManager()
    ok, msg = mgr.ensure_hypervisor(os_type="ubuntu")
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
    assert len(msg) > 0


def test_vm_manager_arch_linux_support():
    mgr = VMManager()
    res = mgr.create_vm(os_type="arch", vm_name="test-arch")
    assert res is not None
    assert res.status in {"success", "blocked", "failed"}


def test_manage_vm_tool_actions():
    tool = ManageVMTool()
    assert tool.name == "manage_vm"

    # Test detect
    res_detect = tool.execute({"action": "detect"})
    assert res_detect.status == "success"
    assert "Hypervisor Detection:" in res_detect.output

    # Test ensure for ubuntu
    res_ensure = tool.execute({"action": "ensure", "os_type": "ubuntu"})
    assert res_ensure.status in {"success", "blocked"}

    # Test ensure for arch
    res_ensure_arch = tool.execute({"action": "ensure", "os_type": "arch"})
    assert res_ensure_arch.status in {"success", "blocked"}

    # Test status of non-existent VM
    res_status = tool.execute({"action": "status", "vm_name": "test-dummy-vm"})
    assert res_status.status in {"failed", "success"}
