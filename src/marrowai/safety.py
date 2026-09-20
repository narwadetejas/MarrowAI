from __future__ import annotations

from typing import Any
from .interfaces import PlanStep, SafetyDecision, TaskPlan


class RiskClassifier:
    """Zero-trust risk evaluation engine per HLD & LLD specification.
    
    Evaluates actions against operating policies and ensures all actions—including
    risky, destructive, sudo, and custom tools—can be executed once confirmed by the user.
    """

    allowed_tools = {
        "ls",
        "list_files",
        "echo",
        "run_tests",
        "scaffold_backend",
        "read_file",
        "write_file",
        "gui_action",
        "manage_vm",
        "manage_models",
        "system_status",
        "run_command",
        "system_exec",
        "bash",
        "rm",
        "delete_file",
        "manage_memory",
        "remember",
        "desktop_action",
        "open_app",
        "launch_app",
        "open_url",
        "install_package",
    }

    destructive_tokens = [
        "rm -rf",
        "rm -f",
        "rmdir",
        "mkfs",
        "dd if=",
        "fdisk",
        "parted",
        "wipefs",
        "shutdown",
        "reboot",
        "poweroff",
        "init 0",
        "init 6",
        ":(){ :|:& };:",
        "> /dev/sd",
        "chmod -r 777",
        "chmod 777 /",
    ]

    def is_destructive(self, command_str: str) -> bool:
        """Determines if a command string contains destructive or system-altering tokens."""
        cmd_lower = command_str.lower().strip()
        return any(tok in cmd_lower for tok in self.destructive_tokens)

    def requires_sudo(self, step: PlanStep) -> bool:
        """Checks if a step requires elevated sudo privileges."""
        cmd = str(step.parameters.get("command", "")).lower().strip()
        return "sudo" in cmd or step.parameters.get("requires_sudo", False)

    def classify_risk(self, action_type_or_plan: Any) -> str:
        """Classifies risk level: 'low', 'medium', or 'high'."""
        if isinstance(action_type_or_plan, TaskPlan):
            return action_type_or_plan.risk_level
        if isinstance(action_type_or_plan, PlanStep):
            step = action_type_or_plan
            cmd = str(step.parameters.get("command", ""))
            if self.is_destructive(cmd) or self.requires_sudo(step):
                return "high"
            if step.action_type in {"cli", "file", "gui"} or step.approval_required:
                return "medium"
            return "low"
        if isinstance(action_type_or_plan, str):
            act = action_type_or_plan.lower()
            if act in {"dangerous_delete", "sudo", "system_destroy", "format_disk"}:
                return "high"
            if act in {"cli", "file", "gui", "install_package", "manage_vm"}:
                return "medium"
            return "low"
        return "medium"

    def evaluate(
        self,
        plan_or_step: TaskPlan | PlanStep,
        user_confirmed: bool = False,
        password: str | None = None,
    ) -> SafetyDecision:
        """Evaluates whether a plan or step is safe to execute or requires user review.
        
        CRITICAL INVARIANT: Any action—even high-risk, destructive, or custom operations—
        is ALLOWED when user_confirmed is True or when a password is provided.
        """
        # If user explicitly confirmed or provided authorization credentials, allow execution
        if user_confirmed or (password and len(password.strip()) > 0):
            return SafetyDecision(
                decision="ALLOW",
                reason="Action authorized by explicit user confirmation.",
                confidence=1.0,
                requires_confirmation=False,
            )

        # Handle PlanStep evaluation directly
        if isinstance(plan_or_step, PlanStep):
            step = plan_or_step
            cmd = str(step.parameters.get("command", ""))
            if self.is_destructive(cmd):
                return SafetyDecision(
                    decision="REVIEW",
                    reason=f"Destructive operation detected in step '{step.id}': requires confirmation.",
                    confidence=0.99,
                    requires_confirmation=True,
                )
            if self.requires_sudo(step):
                return SafetyDecision(
                    decision="REVIEW",
                    reason=f"Privileged sudo operation in step '{step.id}': requires password or confirmation.",
                    confidence=0.95,
                    requires_confirmation=True,
                )
            if step.approval_required:
                return SafetyDecision(
                    decision="REVIEW",
                    reason=f"Step '{step.id}' is flagged as requiring user approval.",
                    confidence=0.90,
                    requires_confirmation=True,
                )
            return SafetyDecision(
                decision="ALLOW",
                reason="Safe step within operating policy.",
                confidence=0.95,
                requires_confirmation=False,
            )

        # Handle TaskPlan evaluation
        plan = plan_or_step
        if plan.intent == "dangerous_delete":
            return SafetyDecision(
                decision="DENY",
                reason="High-risk destructive action requires explicit user confirmation to proceed.",
                confidence=0.99,
                requires_confirmation=True,
            )

        # Check for any destructive command in any step
        for step in plan.steps:
            cmd = str(step.parameters.get("command", ""))
            if self.is_destructive(cmd):
                return SafetyDecision(
                    decision="DENY",
                    reason=f"High-risk command '{cmd}' requires explicit user confirmation.",
                    confidence=0.99,
                    requires_confirmation=True,
                )

        # Unknown or custom tools require user confirmation instead of being permanently blocked
        unknown_tools = {
            step.tool_name for step in plan.steps if step.tool_name and step.tool_name not in self.allowed_tools
        }
        if unknown_tools:
            return SafetyDecision(
                decision="DENY",
                reason=f"Custom / unlisted tool(s) require explicit user authorization: {', '.join(sorted(unknown_tools))}.",
                confidence=0.95,
                requires_confirmation=True,
            )

        if plan.risk_level == "high":
            return SafetyDecision(
                decision="REVIEW",
                reason="High-risk action requires explicit confirmation or password.",
                confidence=0.8,
                requires_confirmation=True,
            )

        if plan.risk_level == "medium":
            return SafetyDecision(
                decision="REVIEW",
                reason="Action requires human confirmation before execution.",
                confidence=0.7,
                requires_confirmation=True,
            )

        return SafetyDecision(
            decision="ALLOW",
            reason="Safe action within current operating policy.",
            confidence=0.95,
            requires_confirmation=False,
        )


class SafetyGate(RiskClassifier):
    """Backwards-compatible alias for RiskClassifier."""
    pass

