from __future__ import annotations

from .executor import SafeExecutor
from .memory import MemoryStore
from .model import OllamaProvider
from .planner import RuleBasedPlanner
from .safety import SafetyGate


class MarrowAssistant:
    def __init__(self, model_provider: OllamaProvider | None = None, memory_path: str | None = None) -> None:
        self.model_provider = model_provider or OllamaProvider()
        self.executor = SafeExecutor()
        self.safety = SafetyGate()
        self.fallback_planner = RuleBasedPlanner()
        self.memory = MemoryStore(memory_path)

    def process(self, user_input: str) -> dict:
        self.memory.add_event("user", user_input)
        context = self.memory.build_context(user_input)

        plan = self.model_provider.generate_plan(context)
        decision = self.safety.evaluate(plan)

        result = {"intent": plan.intent, "risk_level": plan.risk_level, "decision": decision.decision}

        if decision.decision == "DENY":
            self.memory.add_event("assistant", "Action blocked by safety policy.")
            result["status"] = "blocked"
            return result

        if plan.steps and plan.steps[0].tool_name == "ls":
            exec_result = self.executor.execute_command("ls")
            result["status"] = exec_result.status
            result["output"] = exec_result.output
            self.memory.add_event("assistant", f"Executed ls with status {exec_result.status}")
            return result

        self.memory.add_event("assistant", "Request is outside the supported MVP tool set.")
        result["status"] = "unsupported"
        return result
