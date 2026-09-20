from __future__ import annotations

import threading
from .assistant import MarrowAssistant
from .config import get_config
from .voice_engine import OfflineVoiceEngine


class InteractiveSession:
    def __init__(self, voice_profile: str | None = None) -> None:
        config = get_config()
        self.assistant = MarrowAssistant()
        prof = voice_profile or config.voice_profile or "indian_female"
        if prof in {"man", "male", "indian_male"}:
            prof = "indian_male"
        elif prof in {"woman", "female", "indian_female"}:
            prof = "indian_female"
        self.voice_engine = OfflineVoiceEngine(profile=prof)
        self.voice_enabled = config.voice_enabled
        self.interactive_mode = config.interactive_mode

    def _speak(self, text: str) -> None:
        if self.voice_enabled and text:
            # Run in daemon thread to avoid blocking prompt input
            threading.Thread(target=self.voice_engine.speak, args=(text,), daemon=True).start()

    def run(self) -> None:
        label = self.voice_engine.profile.get("label", "Indian English")
        welcome = (
            f"MarrowAI ready. Active voice: {label}.\n"
            "I can create Arch/Ubuntu VMs, manage AI models, inspect system telemetry, and answer questions.\n"
            "Tip: Say 'switch to male voice' or 'switch to female voice' to change voice profile, or '/listen' for voice input."
        )
        print(welcome)
        self._speak(f"MarrowAI ready. Active voice: {label}. How may I help you?")

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSession closed.")
                break

            if not user_input:
                continue

            # Command to simulate or capture voice input
            if user_input.lower() in {"/listen", "/mic", "listen"}:
                try:
                    user_input = input("[Listening for voice input...] Speak your request (e.g. 'create an arch linux vm'): ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not user_input:
                    continue

            if user_input.lower() in {"exit", "quit", "bye"}:
                goodbye = "Goodbye. I will be ready when you need me again."
                print(f"MarrowAI: {goodbye}")
                self._speak(goodbye)
                break

            lowered = user_input.lower()

            # Dynamic voice profile switching commands
            if any(cmd in lowered for cmd in ["switch to male", "use male voice", "use man voice", "switch to man voice", "voice male", "voice man", "set voice male", "set voice man"]):
                self.voice_engine.set_profile("indian_male")
                ack = "Voice switched to Indian English Male. How can I assist you?"
                print(f"MarrowAI: {ack}")
                self._speak(ack)
                continue

            if any(cmd in lowered for cmd in ["switch to female", "use female voice", "use woman voice", "switch to woman voice", "voice female", "voice woman", "set voice female", "set voice woman"]):
                self.voice_engine.set_profile("indian_female")
                ack = "Voice switched to Indian English Female. How can I assist you?"
                print(f"MarrowAI: {ack}")
                self._speak(ack)
                continue

            # Real-time spoken announcement before step execution
            def _on_narration(msg: str) -> None:
                print(f"\nMarrowAI (Voice Announcement): {msg}")
                self._speak(msg)

            result = self.assistant.process(user_input, on_narration=_on_narration)

            if result.get("status") == "requires_confirmation":
                conf_msg = result.get("output", "⚠️ This task requires confirmation to proceed.")
                print(f"\nMarrowAI: {conf_msg}")
                self._speak("This high risk operation requires confirmation. Please confirm or provide password to proceed.")
                try:
                    conf_input = input("Confirm execution? [y/N or sudo password]: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
                    continue

                if conf_input.lower() in {"y", "yes", "confirm", "proceed", "approve"}:
                    result = self.assistant.process("yes", on_narration=_on_narration, confirmed=True)
                elif len(conf_input) > 0 and conf_input.lower() not in {"n", "no", "cancel"}:
                    result = self.assistant.process("yes", on_narration=_on_narration, confirmed=True, password=conf_input)
                else:
                    cancel_msg = "Task cancelled by user."
                    print(f"MarrowAI: {cancel_msg}")
                    self._speak(cancel_msg)
                    continue

            if result.get("decision") == "DENY":
                deny_msg = "I blocked that action because it violates security or safety policy."
                print(f"MarrowAI: {deny_msg}")
                self._speak(deny_msg)
                continue

            if result.get("status") == "blocked":
                block_msg = f"The action was blocked: {result.get('output', 'Policy restriction')}"
                print(f"MarrowAI: {block_msg}")
                self._speak(block_msg)
                continue

            if result.get("status") == "unsupported":
                unsupp_msg = (
                    "I can help you create Arch Linux and Ubuntu VMs, manage offline AI models, scaffold backends, "
                    "run test suites, monitor live system status, and switch Indian voice profiles. What would you like to do?"
                )
                print(f"MarrowAI: {unsupp_msg}")
                self._speak(unsupp_msg)
                continue

            is_conversational = result.get("intent") in {
                "explain_arch_linux", "explain_ubuntu", "explain_vm", "explain_models",
                "voice_info", "assistant_info", "greeting", "general_question", "answer_question"
            }
            if result.get("output"):
                print(result["output"])
                if not is_conversational:
                    first_line = result["output"].strip().splitlines()[0] if result["output"].strip() else ""
                    self._speak(f"Done. {first_line[:160]}")
            elif not is_conversational:
                completion_msg = f"Task completed with status: {result.get('status')}."
                print(f"MarrowAI: {completion_msg}")
                self._speak(completion_msg)


def main() -> None:
    InteractiveSession().run()


if __name__ == "__main__":
    main()

