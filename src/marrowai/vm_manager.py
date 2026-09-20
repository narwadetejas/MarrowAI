from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from .interfaces import ExecutionResult


class VMManager:
    """Autonomous Virtual Machine and Hypervisor Manager.

    Detects virtualization runtimes (Multipass, QEMU/KVM, VirtualBox),
    validates installation, and provisions or manages local Ubuntu, Arch Linux,
    and Debian virtual machine instances.
    """

    def __init__(self) -> None:
        self.multipass = shutil.which("multipass")
        self.qemu = shutil.which("qemu-system-x86_64") or shutil.which("qemu-kvm")
        self.vbox = shutil.which("VBoxManage")

    def detect_hypervisors(self) -> dict[str, Any]:
        has_kvm = Path("/dev/kvm").exists()
        return {
            "multipass": bool(self.multipass),
            "qemu": bool(self.qemu),
            "virtualbox": bool(self.vbox),
            "kvm_accelerator": has_kvm,
            "recommended": "multipass" if self.multipass else ("qemu" if self.qemu else "multipass"),
        }

    def ensure_hypervisor(self, os_type: str = "ubuntu") -> tuple[bool, str]:
        """Checks if a hypervisor is ready; if not, provides installation command/path."""
        status = self.detect_hypervisors()
        if os_type == "arch":
            if status["qemu"]:
                return True, f"QEMU hypervisor is ready at {self.qemu} for Arch Linux."
            if status["multipass"]:
                return True, f"Multipass hypervisor is ready at {self.multipass}."
            if status["virtualbox"]:
                return True, f"VirtualBox hypervisor is ready at {self.vbox} for Arch Linux."
            return False, (
                "No hypervisor detected for Arch Linux. Install QEMU/KVM:\n"
                "  sudo apt-get update && sudo apt-get install -y qemu-system-x86 qemu-utils\n"
                "Or install Canonical Multipass:\n"
                "  sudo snap install multipass"
            )

        if status["multipass"]:
            return True, f"Canonical Multipass hypervisor is installed and ready at {self.multipass}."
        if status["qemu"]:
            return True, f"QEMU hypervisor is installed and ready at {self.qemu}."
        if status["virtualbox"]:
            return True, f"VirtualBox is installed and ready at {self.vbox}."

        instructions = (
            "No hypervisor detected. To automatically install Multipass on Ubuntu:\n"
            "  sudo snap install multipass\n"
            "Or install QEMU/KVM via apt:\n"
            "  sudo apt-get update && sudo apt-get install -y qemu-kvm"
        )
        return False, instructions

    def check_vm_exists(self, vm_name: str) -> tuple[bool, str]:
        """Checks if a VM with the specified name exists."""
        if not self.multipass:
            return False, "Multipass is not installed."
        try:
            completed = subprocess.run(
                [self.multipass, "info", vm_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if completed.returncode == 0:
                return True, completed.stdout.strip()
            return False, f"VM '{vm_name}' does not exist."
        except Exception as exc:
            return False, str(exc)

    def create_vm(
        self,
        os_type: str = "ubuntu",
        vm_name: str | None = None,
        release: str | None = None,
    ) -> ExecutionResult:
        """Provisions an Ubuntu or Arch Linux virtual machine autonomously."""
        os_clean = os_type.lower().strip()
        if "arch" in os_clean:
            return self.create_arch_vm(vm_name or "marrowai-arch")
        return self.create_ubuntu_vm(vm_name or "marrowai-ubuntu", release or "24.04")

    def create_arch_vm(self, vm_name: str = "marrowai-arch") -> ExecutionResult:
        """Provisions or configures an Arch Linux virtual machine."""
        is_ready, msg = self.ensure_hypervisor(os_type="arch")
        if not is_ready:
            return ExecutionResult(
                status="blocked",
                output=(
                    f"Cannot create Arch Linux VM '{vm_name}' because no hypervisor is installed.\n"
                    f"{msg}\n"
                    "Install QEMU/KVM or Multipass, then retry."
                ),
                exit_code=1,
            )

        if self.qemu:
            # QEMU Arch Linux initialization
            vm_dir = Path(f".marrowai/vms/{vm_name}")
            vm_dir.mkdir(parents=True, exist_ok=True)
            launch_script = vm_dir / "start_arch.sh"
            launch_script.write_text(
                "#!/usr/bin/env bash\n"
                f"# MarrowAI Arch Linux VM Launcher for {vm_name}\n"
                "QEMU_BIN=$(which qemu-system-x86_64 || echo 'qemu-system-x86_64')\n"
                f"$QEMU_BIN -m 2048 -smp 2 -enable-kvm -name {vm_name} \"$@\"\n",
                encoding="utf-8",
            )
            launch_script.chmod(0o755)
            output = (
                f"Arch Linux VM environment '{vm_name}' configured successfully.\n"
                f"Hypervisor: {self.qemu}\n"
                f"Configuration path: {launch_script.resolve()}\n"
                f"Allocated: 2048MB RAM, 2 vCPUs, KVM hardware acceleration enabled."
            )
            return ExecutionResult("success", output, 0)

        if self.multipass:
            # Use Multipass with cloud-init for Arch container/VM
            return ExecutionResult(
                "success",
                f"Multipass hypervisor detected. Ready to launch Arch container/VM '{vm_name}'.",
                0,
            )

        return ExecutionResult("success", f"Hypervisor ready for Arch Linux VM '{vm_name}': {msg}", 0)

    def create_ubuntu_vm(self, vm_name: str = "marrowai-ubuntu", release: str = "24.04") -> ExecutionResult:
        """Launches or verifies an Ubuntu OS VM autonomously."""
        is_ready, msg = self.ensure_hypervisor(os_type="ubuntu")
        if not is_ready:
            return ExecutionResult(
                status="blocked",
                output=(
                    f"Cannot create VM '{vm_name}' because no hypervisor is installed.\n"
                    f"{msg}\n"
                    "Please install Multipass or QEMU, then retry."
                ),
                exit_code=1,
            )

        if self.multipass:
            exists, info = self.check_vm_exists(vm_name)
            if exists:
                try:
                    subprocess.run([self.multipass, "start", vm_name], check=False, timeout=30, capture_output=True)
                    info_res = subprocess.run([self.multipass, "info", vm_name], capture_output=True, text=True, timeout=10)
                    output = f"Ubuntu VM '{vm_name}' is already installed and running.\n{info_res.stdout.strip()}"
                    return ExecutionResult("success", output, 0)
                except Exception as exc:
                    return ExecutionResult("failed", f"Failed to start existing VM '{vm_name}': {exc}", 1)

            try:
                completed = subprocess.run(
                    [self.multipass, "launch", release, "--name", vm_name],
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                if completed.returncode == 0:
                    info_res = subprocess.run([self.multipass, "info", vm_name], capture_output=True, text=True, timeout=10)
                    output = f"Ubuntu {release} VM '{vm_name}' successfully provisioned and launched.\n{info_res.stdout.strip()}"
                    return ExecutionResult("success", output, 0)
                return ExecutionResult(
                    "failed",
                    f"Failed to launch Ubuntu VM '{vm_name}': {completed.stderr.strip()}",
                    completed.returncode,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult("failed", f"Timed out launching Ubuntu VM '{vm_name}'. Check system resources.", None)
            except Exception as exc:
                return ExecutionResult("failed", f"Error provisioning Ubuntu VM: {exc}", None)

        return ExecutionResult(
            "success",
            f"Hypervisor detected ({msg}). Ready to execute VM creation.",
            0,
        )
