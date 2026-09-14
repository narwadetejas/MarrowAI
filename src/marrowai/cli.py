from __future__ import annotations

import argparse

from .assistant import MarrowAssistant


def main() -> None:
    parser = argparse.ArgumentParser(description="MarrowAI safe local assistant")
    parser.add_argument("prompt", nargs="+", help="Natural-language request")
    args = parser.parse_args()

    text = " ".join(args.prompt)
    result = MarrowAssistant().process(text)

    print(f"Intent: {result['intent']}")
    print(f"Risk: {result['risk_level']}")
    print(f"Safety: {result['decision']}")
    print(f"Status: {result['status']}")
    if result.get("output"):
        print(result["output"])


if __name__ == "__main__":
    main()
