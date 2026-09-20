from __future__ import annotations

from pathlib import Path
from typing import Any
from .audit import AuditLogger
from .executor import SafeExecutor
from .governor import ResourceGovernor
from .interfaces import TaskPlan
from .memory import MemoryStore
from .model import OllamaProvider
from .planner import RuleBasedPlanner
from .safety import RiskClassifier, SafetyGate
from .tools import ManageMemoryTool, ToolRegistry, ToolRouter


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
        self.memory = MemoryStore(memory_path)

        registry = ToolRegistry()
        mem_tool = ManageMemoryTool(memory_store=self.memory)
        registry.register(mem_tool)
        registry._tools["remember"] = mem_tool

        self.tool_router = ToolRouter(registry)
        self.executor = SafeExecutor(governor=self.governor, registry=registry)
        self.safety = RiskClassifier()
        self.fallback_planner = RuleBasedPlanner()
        self._pending_plan: Any = None

        if audit_logger is not None:
            self.audit = audit_logger
        elif memory_path is not None:
            audit_path = str(Path(memory_path).parent / "audit.jsonl")
            self.audit = AuditLogger(log_path=audit_path)
        else:
            self.audit = AuditLogger()

    def execute_plan(self, plan: TaskPlan, password: str | None = None) -> dict[str, Any]:
        """Dispatches verified plan steps to the tool router and executor per LLD specification."""
        healthy, gov_details = self.governor.is_safe_to_execute()
        self.audit.log_governor_check(healthy, gov_details)
        if not healthy:
            self.memory.add_event("assistant", f"Governor paused execution: {gov_details}")
            return {
                "status": "blocked",
                "output": gov_details,
                "intent": plan.intent,
                "risk_level": plan.risk_level,
                "plan_id": plan.id,
            }

        outputs = []
        for step in plan.steps:
            if not step.tool_name:
                continue
            tool_call = self.tool_router.route(step, password=password)
            exec_result = self.executor.execute_tool_call(tool_call)
            self.audit.log_tool_execution(tool_call.tool_name, tool_call.arguments, exec_result)
            outputs.append(exec_result.output)
            if exec_result.status != "success":
                self.memory.add_event("assistant", f"Stopped at {step.id} with status {exec_result.status}")
                return {
                    "status": exec_result.status,
                    "output": "\n".join(output for output in outputs if output),
                    "intent": plan.intent,
                    "risk_level": plan.risk_level,
                    "plan_id": plan.id,
                }

        if outputs:
            self.memory.add_event("assistant", f"Completed {len(outputs)} autonomous step(s)")
            return {
                "status": "success",
                "output": "\n".join(output for output in outputs if output),
                "intent": plan.intent,
                "risk_level": plan.risk_level,
                "plan_id": plan.id,
            }
        else:
            self.memory.add_event("assistant", "Request is outside the supported MVP tool set.")
            return {
                "status": "unsupported",
                "output": "Request is outside the supported MVP tool set.",
                "intent": plan.intent,
                "risk_level": plan.risk_level,
                "plan_id": plan.id,
            }

    def process(
        self,
        user_input: str,
        on_narration: Any = None,
        confirmed: bool = False,
        password: str | None = None,
    ) -> dict:
        self.audit.log_request(user_input)
        self.memory.add_event("user", user_input)

        # Check if this input is a confirmation of a previous pending plan
        lowered = user_input.strip().lower()
        if (confirmed or lowered in {"yes", "y", "confirm", "proceed", "approve"}) and self._pending_plan is not None:
            plan = self._pending_plan
            self._pending_plan = None
            confirmed = True
        else:
            context = self.memory.build_context(user_input)
            plan = self.model_provider.generate_plan(context)

        self.audit.log_plan(plan)

        narration = self.get_narration(plan)
        if on_narration and narration:
            try:
                on_narration(narration)
            except Exception:
                pass

        decision = self.safety.evaluate(plan, user_confirmed=confirmed, password=password)
        self.audit.log_decision(decision)

        result = {
            "intent": plan.intent,
            "risk_level": plan.risk_level,
            "decision": decision.decision,
            "plan_id": plan.id,
            "narration": narration,
            "plan_steps": [{"id": s.id, "description": s.description, "action_type": s.action_type} for s in plan.steps],
        }

        # If confirmation is required and action has not been authorized yet, halt for user approval
        if decision.requires_confirmation and not confirmed:
            self._pending_plan = plan
            msg = f"⚠️ High-risk task '{plan.intent}' requires confirmation. Type 'yes' or confirm to proceed."
            self.memory.add_event("assistant", msg)
            result["status"] = "requires_confirmation"
            result["requires_confirmation"] = True
            result["output"] = msg
            result["confirmation_prompt"] = msg
            return result

        if decision.decision == "DENY" and not confirmed:
            self.memory.add_event("assistant", "Action blocked by safety policy.")
            result["status"] = "blocked"
            return result

        exec_res = self.execute_plan(plan, password=password)
        result["status"] = exec_res.get("status", "failed")
        result["output"] = exec_res.get("output", "")

        # Continuous learning: automatically extract and index facts from user conversation
        try:
            self.memory.extract_and_store_facts(user_input, result.get("output"))
        except Exception:
            pass

        return result


    def get_narration(self, plan: Any) -> str:
        """Generates an immediate spoken statement telling the user what actions will be performed or answering questions."""
        intent = getattr(plan, "intent", "unknown")
        steps = getattr(plan, "steps", [])
        return self._narrate_intent(intent, steps)

    def _narrate_intent(self, intent: str, steps: list[Any]) -> str:
        if intent in {
            "explain_arch_linux",
            "explain_ubuntu",
            "explain_vm",
            "explain_models",
            "voice_info",
            "assistant_info",
            "greeting",
            "general_question",
            "answer_question",
        }:
            if steps and steps[0].tool_name == "echo" and "text" in steps[0].parameters:
                return steps[0].parameters["text"]

        if intent in {"watch_movie", "watch_media"}:
            q = "the movie"
            if steps and "query" in steps[0].parameters:
                q = steps[0].parameters["query"]
            return f"I have planned the steps to help you watch '{q}': first formulating the online source, then opening your web browser directly to find and stream it."
        if intent == "watch_youtube":
            q = ""
            if steps and "query" in steps[0].parameters:
                q = steps[0].parameters["query"]
            if q:
                return f"I have planned prior: opening YouTube directly to find and play '{q}' for you."
            return "Opening YouTube in your default web browser."
        if intent == "search_web":
            q = "your search"
            if steps and "query" in steps[0].parameters:
                q = steps[0].parameters["query"]
            return f"I have formulated a web search for '{q}' and am opening your browser now."
        if intent == "remember_fact":
            return "I have stored this information in my embedded memory for our future conversations."
        if intent == "recall_memories":
            return "Here are the stored facts and preferences I remember about you."
        if intent == "search_memory":
            return "I am searching through my long-term memory records."
        if intent == "forget_memory":
            return "I have updated my memory records."
        if intent == "create_arch_vm":
            return "I will check the hypervisors on your system and configure an Arch Linux virtual machine for you now."
        if intent == "create_ubuntu_vm":
            return "I will check your system and launch an Ubuntu virtual machine for you now."
        if intent == "explain_arch_linux":
            return "Here is information about Arch Linux and how I run it in a virtual machine."
        if intent == "explain_ubuntu":
            return "Here is information about Ubuntu and its virtual machine support."
        if intent == "voice_info":
            return "Here are the available Indian English voice options."
        if intent == "assistant_info":
            return "Here is an overview of my offline capabilities and architecture."
        if intent == "download_model":
            model_name = "the requested model"
            if steps and "model_name" in steps[0].parameters:
                model_name = steps[0].parameters["model_name"]
            return f"I will check your local Ollama models and download {model_name} for offline use."
        if intent == "list_models":
            return "I am checking your installed local AI models in Ollama."
        if intent == "system_status":
            return "I am gathering real-time telemetry, resources, and system health status."
        if intent == "list_files":
            return "I will list the files in your current workspace."
        if intent == "create_backend_project":
            return "I will scaffold a FastAPI backend project and run its test suite."
        if intent in {"run_command", "system_exec"}:
            cmd = ""
            if steps and "command" in steps[0].parameters:
                cmd = steps[0].parameters["command"]
            return f"Executing command on your computer: {cmd}" if cmd else "Executing command on your computer."
        if intent == "run_tests":
            return "I am running the local test suite."
        if intent == "open_browser":
            return "Opening web browser."
        if intent == "open_file_manager":
            return "Opening the file manager at your current directory."
        if intent == "open_appcenter":
            return "Launching the desktop software app center."
        if intent == "install_package":
            pkg = "the requested package"
            if steps and "package_name" in steps[0].parameters:
                pkg = steps[0].parameters["package_name"]
            elif len(steps) > 1 and "package_name" in steps[1].parameters:
                pkg = steps[1].parameters["package_name"]
            return f"Installing software package {pkg} on your system."
        if intent == "launch_app":
            app = "application"
            if steps and "app_name" in steps[0].parameters:
                app = steps[0].parameters["app_name"]
            return f"Launching {app}."
        return "I will analyze your request and execute the required safe steps."
