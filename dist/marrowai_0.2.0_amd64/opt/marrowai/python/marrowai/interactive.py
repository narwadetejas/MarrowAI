from __future__ import annotations

from .assistant import MarrowAssistant
from .config import get_config


class InteractiveSession:
    def __init__(self) -> None:
        config = get_config()
        self.assistant = MarrowAssistant()
        self.voice_enabled = config.voice_enabled
        self.interactive_mode = config.interactive_mode

    def run(self) -> None:
        print("MarrowAI ready. I am here to help, and I will keep actions safe and transparent.")
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                print("\nSession closed.")
                break

            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit", "bye"}:
                print("MarrowAI: Goodbye. I will be ready when you need me again.")
                break

            print("MarrowAI: I am checking the request, mapping it to a safe plan, and then I will act.")
            result = self.assistant.process(user_input)

            if result.get("decision") == "DENY":
                print("MarrowAI: I blocked that action because it is not safe for this system.")
                continue

            if result.get("status") == "blocked":
                print("MarrowAI: The action was blocked by policy.")
                continue

            if result.get("status") == "unsupported":
                print("MarrowAI: I can help with a supported safe task, but this request is not in the current MVP tool set yet.")
                continue

            print(f"MarrowAI: The task completed with status: {result.get('status')}.")
            if result.get("output"):
                print(result["output"])


def main() -> None:
    InteractiveSession().run()


if __name__ == "__main__":
    main()
