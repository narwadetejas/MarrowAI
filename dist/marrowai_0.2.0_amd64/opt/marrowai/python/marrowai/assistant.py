from __future__ import annotations

from pathlib import Path
from .audit import AuditLogger
from .executor import SafeExecutor
from .governor import ResourceGovernor
from .memory import MemoryStore
from .model import OllamaProvider
from .planner import RuleBasedPlanner
from .safety import SafetyGate


class MarrowAssistant:
    def __init__(
        self,
        model_provider: OllamaProvider | None = None,
        memory_path: str | None = None,
        audit_logger: AuditLogger | None = None,
        governor: ResourceGovernor | None = None,
    ) -> None:
        self.model_provider = model_provider or OllamaProvider()
        self.governor = governor or ResourceGovernor()
        self.executor = SafeExecutor(governor=self.governor)
        self.safety = SafetyGate()
        self.fallback_planner = RuleBasedPlanner()
        self.memory = MemoryStore(memory_path)

        if audit_logger is not None:
            self.audit = audit_logger
        elif memory_path is not None:
            audit_path = str(Path(memory_path).parent / "audit.jsonl")
            self.audit = AuditLogger(log_path=audit_path)
        else:
            self.audit = AuditLogger()

    def process(self, user_input: str) -> dict:
        self.audit.log_request(user_input)
        self.memory.add_event("user", user_input)
        context = self.memory.build_context(user_input)

        plan = self.model_provider.generate_plan(context)
        self.audit.log_plan(plan)

        decision = self.safety.evaluate(plan)
        self.audit.log_decision(decision)

        result = {
            "intent": plan.intent,
            "risk_level": plan.risk_level,
            "decision": decision.decision,
            "plan_id": plan.id,
        }

        if decision.decision == "DENY":
            self.memory.add_event("assistant", "Action blocked by safety policy.")
            result["status"] = "blocked"
            return result

        # Resource Governor pre-check for the overall workflow
        healthy, gov_details = self.governor.is_safe_to_execute()
        self.audit.log_governor_check(healthy, gov_details)
        if not healthy:
            self.memory.add_event("assistant", f"Governor paused execution: {gov_details}")
            result["status"] = "blocked"
            result["output"] = gov_details
            return result

        outputs = []
        for step in plan.steps:
            if not step.tool_name:
                continue
            exec_result = self.executor.execute_tool(step.tool_name, step.parameters)
            self.audit.log_tool_execution(step.tool_name, step.parameters, exec_result)
            outputs.append(exec_result.output)
            if exec_result.status != "success":
                result["status"] = exec_result.status
                result["output"] = "\n".join(output for output in outputs if output)
                self.memory.add_event("assistant", f"Stopped at {step.id} with status {exec_result.status}")
                return result

        if outputs:
            result["status"] = "success"
            result["output"] = "\n".join(output for output in outputs if output)
            self.memory.add_event("assistant", f"Completed {len(outputs)} autonomous step(s)")
            return result

        self.memory.add_event("assistant", "Request is outside the supported MVP tool set.")
        result["status"] = "unsupported"
        return result
