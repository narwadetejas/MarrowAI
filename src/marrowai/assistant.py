from __future__ import annotations

from pathlib import Path
from typing import Any
from .agent_loop import AgentLoop
from .audit import AuditLogger
from .executor import SafeExecutor
from .governor import ResourceGovernor
from .interfaces import TaskPlan
from .memory import MemoryStore
from .model import OllamaProvider
from .planner import RuleBasedPlanner
from .safety import RiskClassifier, SafetyGate
from .tools import DailyContextTool, ManageMemoryTool, ToolRegistry, ToolRouter

# Words that indicate a GUI/desktop action the AgentLoop should handle directly
_AGENT_LOOP_TRIGGERS = {
    "watch", "play", "stream", "listen",
    "write code", "code a", "create a", "make a",
    "write a program", "write a script", "calculator",
    "fibonacci", "sort algorithm", "bubble sort", "selection sort",
    "hello world", "program that", "click", "tap", "open", "launch",
}

def _is_agent_loop_request(text: str) -> bool:
    """Returns True if this request should be handled by the autonomous AgentLoop."""
    t = text.lower().strip()
    # Explicit desktop/GUI signals
    if any(kw in t for kw in [
        "youtube", "video", "song", "music", "movie",
        "write code", "code a", "type code", "open editor",
        "calculator", "fibonacci", "sort algorithm", "bubble sort",
        "selection sort", "hello world", "write a program", "write a script",
        "write me a", "make a", "create a python", "create a javascript",
    ]):
        return True
    # "open" + known app
    if "open" in t or "launch" in t:
        import re
        if re.search(r'(?:open|launch|start)\s+(?:firefox|chrome|gedit|code|vscode|terminal|calculator)', t):
            return True
    return False


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

        daily_tool = DailyContextTool(memory_store=self.memory)
        registry.register(daily_tool)
        registry._tools["daily_context"] = daily_tool
        registry._tools["daily_memory"] = daily_tool

        self.tool_router = ToolRouter(registry)
        self.executor = SafeExecutor(governor=self.governor, registry=registry)
        self.safety = RiskClassifier()
        self.fallback_planner = RuleBasedPlanner()
        self._pending_plan: Any = None
        self._agent_loop: AgentLoop | None = None  # lazy-init on first use

        if audit_logger is not None:
            self.audit = audit_logger
        elif memory_path is not None:
            audit_path = str(Path(memory_path).parent / "audit.jsonl")
            self.audit = AuditLogger(log_path=audit_path)
        else:
            self.audit = AuditLogger()

    def _get_agent_loop(self, on_step: Any = None) -> AgentLoop:
        """Lazily initialise the AgentLoop (and re-wire the step callback)."""
        if self._agent_loop is None:
            self._agent_loop = AgentLoop(on_step=on_step)
        else:
            self._agent_loop.on_step = on_step
        return self._agent_loop

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

    def generate_thought_process(self, user_input: str, plan: TaskPlan, context: str = "") -> str:
        """Produces a comprehensive, structured Claude-style thinking process."""
        intent = getattr(plan, "intent", "unknown")
        risk = getattr(plan, "risk_level", "low")
        steps = getattr(plan, "steps", [])

        # 1. Intent Analysis
        clean_input = user_input.strip()
        if "current request:" in clean_input.lower():
            idx = clean_input.lower().rfind("current request:")
            clean_input = clean_input[idx + len("current request:"):].strip()

        intent_summary = f"User request: '{clean_input}'."
        if intent in {"write_essay_libreoffice", "launch_app"}:
            intent_summary += " User requested desktop document authoring and application execution."
        elif intent in {"write_code_in_editor"}:
            intent_summary += " User requested algorithm code synthesis and display in a desktop code editor."
        elif intent in {"close_tab"}:
            intent_summary += " User requested browser/IDE tab closure with keyboard hotkey targeting."
        elif intent in {"screen_perception", "visual_click"}:
            intent_summary += " User requested visual screen inspection and UI element interaction."
        elif intent in {"review_today_context", "list_daily_contexts"}:
            intent_summary += " User requested review of today's conversational session and episodic context."
        elif intent in {"answer_question", "general_question"}:
            intent_summary += " User requested informational explanation and knowledge synthesis."

        # 2. Context & Environment Review
        ctx_summary = "Reviewing daily session context and local desktop environment..."
        today_turns = len(self.memory.get_daily_context().get("turns", []))
        ctx_summary += f" Found {today_turns} previous turn(s) in today's context journal."
        if "antigravity" in clean_input.lower():
            ctx_summary += " Target window identified: Antigravity IDE."
        elif "libre" in clean_input.lower() or "writer" in clean_input.lower():
            ctx_summary += " Target environment: LibreOffice Writer document suite."
        elif "sort" in clean_input.lower() or "editor" in clean_input.lower():
            ctx_summary += " Target workspace: Python script in desktop text editor."

        # 3. Strategy & Decomposition
        strategy_lines = ["Synthesized execution strategy:"]
        if steps:
            for idx, s in enumerate(steps, start=1):
                strategy_lines.append(f"  {idx}. [{s.action_type.upper()}] {s.description}")
        else:
            strategy_lines.append("  1. Formulate direct conversational response.")

        # 4. Safety & Policy Verification
        safety_summary = f"Safety verification: Evaluated policy risk level as {risk.upper()}."
        if risk == "high":
            safety_summary += " High-risk operation detected; will hold for explicit user confirmation."
        else:
            safety_summary += " Parameters validated within safe operating boundaries."

        sections = [
            "🧠 MarrowAI Thought Process:",
            f"• Intent Analysis:\n  {intent_summary}",
            f"• Context & Environment:\n  {ctx_summary}",
            "• Strategy & Steps:\n" + "\n".join(strategy_lines),
            f"• Safety Policy Check:\n  {safety_summary}",
        ]
        return "\n\n".join(sections)

    def process(
        self,
        user_input: str,
        on_narration: Any = None,
        on_thinking: Any = None,
        confirmed: bool = False,
        password: str | None = None,
    ) -> dict:
        self.audit.log_request(user_input)
        self.memory.record_daily_turn("user", user_input)

        # ── Fast path: route desktop/GUI tasks through the autonomous AgentLoop ──
        if _is_agent_loop_request(user_input) and not confirmed:
            def _step_cb(msg: str) -> None:
                """Forward agent step messages as narrations to the UI."""
                if on_narration:
                    try:
                        on_narration(msg)
                    except Exception:
                        pass

            if on_thinking:
                try:
                    on_thinking(f"🧠 MarrowAI is reasoning autonomously about: {user_input}")
                except Exception:
                    pass

            loop = self._get_agent_loop(on_step=_step_cb)
            agent_result = loop.run(user_input)

            out_str = agent_result.get("output", "")
            status = agent_result.get("status", "unknown")
            intent = agent_result.get("intent", "agent_loop")

            # Log and return
            self.memory.add_event("assistant", f"AgentLoop completed [{status}]: {out_str[:80]}")
            try:
                self.memory.record_daily_turn("assistant", out_str,
                                              details={"intent": intent, "status": status})
            except Exception:
                pass

            return {
                "status": status,
                "output": out_str,
                "intent": intent,
                "risk_level": "low",
                "decision": "ALLOW",
                "plan_id": "agent-loop",
                "narration": f"Executing: {user_input}",
                "thought_process": f"🧠 AgentLoop reasoning for: {user_input}",
                "plan_steps": [],
            }

        # ── Normal path: rule-based planner + LLM + tool executor ────────────
        max_retries = 3
        attempts = 0
        last_result = {}

        while attempts < max_retries:
            attempts += 1

            # Check if this input is a confirmation of a previous pending plan
            lowered = current_input.strip().lower()
            if (confirmed or lowered in {"yes", "y", "confirm", "proceed", "approve"}) and self._pending_plan is not None:
                plan = self._pending_plan
                self._pending_plan = None
                confirmed = True
                context = ""
            else:
                context = self.memory.build_context(current_input)
                plan = self.model_provider.generate_plan(context)

            self.audit.log_plan(plan)

            thought = self.generate_thought_process(current_input, plan, context)
            if on_thinking and attempts == 1:
                try:
                    on_thinking(thought)
                except Exception:
                    pass

            narration = self.get_narration(plan)
            if on_narration and narration and attempts == 1:
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
                "thought_process": thought,
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
            last_result = result

            if result["status"] == "success" or result["status"] == "blocked" or result["status"] == "unsupported":
                break

            if result["status"] == "failed":
                error_output = result["output"]
                if attempts < max_retries:
                    self.memory.add_event("assistant", f"Plan execution failed: {error_output[:100]}... Reasoning alternative.")
                    if on_narration:
                        try:
                            on_narration("I encountered an issue and am formulating a new plan to retry.")
                        except Exception:
                            pass
                    current_input = (
                        f"Original request: '{user_input}'. "
                        f"Your previous plan failed with error:\n{error_output}\n\n"
                        f"Reason about why this failed. Do not repeat the exact same steps. "
                        f"If the task involves a web browser, streaming video, or GUI action, do NOT attempt to install media player packages like totem or vlc with apt; instead use desktop_action (open_url) to navigate directly in the browser or use gui_action with browser_search_and_play. Provide a revised plan."
                    )
                else:
                    break

        # Continuous learning: automatically extract and index facts from user conversation
        try:
            self.memory.extract_and_store_facts(user_input, last_result.get("output"))
        except Exception:
            pass

        # Record assistant response and execution details in today's context journal
        try:
            out_str = str(last_result.get("output", ""))
            self.memory.record_daily_turn(
                "assistant",
                out_str,
                details={
                    "intent": last_result.get("intent"),
                    "status": last_result.get("status"),
                },
            )
        except Exception:
            pass

        return last_result


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

        if intent in {"review_today_context", "list_daily_contexts"}:
            return "Reviewing our conversation and command history for today."
        if intent == "screen_perception":
            return "Inspecting and reading what is visible on your screen."
        if intent == "capture_screen":
            return "Capturing a screenshot of your screen."
        if intent == "list_windows":
            return "Checking all open application windows on your desktop."
        if intent == "active_window":
            return "Inspecting the currently active application window."
        if intent == "focus_window":
            target = "the application window"
            if steps and "target" in steps[0].parameters:
                target = steps[0].parameters["target"]
            return f"Bringing window '{target}' to the front."
        if intent == "close_window":
            return "Closing the window."
        if intent == "list_tabs":
            return "Checking open tabs in the active window."
        if intent in {"switch_tab", "switch_tab_prev", "switch_tab_index"}:
            return "Switching tab in the active application."
        if intent == "new_tab":
            return "Opening a new tab."
        if intent == "close_tab":
            return "Closing the current tab."
        if intent == "write_essay_libreoffice":
            return "Launching LibreOffice Writer and typing the requested essay."
        if intent == "write_code_in_editor":
            return "Writing Selection Sort algorithm code and opening it in your desktop editor."
        if intent == "visual_click":
            target = "target"
            if steps and "parameters" in steps[0].parameters and "text" in steps[0].parameters["parameters"]:
                target = steps[0].parameters["parameters"]["text"]
            return f"Visually locating '{target}' on your screen and clicking it."
        if intent == "scroll_screen":
            return "Scrolling the screen."
        if intent == "type_text":
            return "Typing text into the active field."
        if intent == "hover_mouse":
            return "Moving the mouse cursor to hover over the requested element."
        if intent == "coordinate_click":
            return "Executing mouse click at the target screen coordinates."
        if intent in {"trigger_hotkey", "press_key"}:
            return "Triggering keyboard shortcut."

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
        
        if steps and hasattr(steps[0], "description") and steps[0].description:
            return f"Thinking: {steps[0].description}."

        return "I will analyze your request and execute the required safe steps."

