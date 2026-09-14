from __future__ import annotations

import argparse

from .executor import SafeExecutor
from .planner import RuleBasedPlanner
from .safety import SafetyGate


def main() -> None:
    parser = argparse.ArgumentParser(description="MarrowAI safe local assistant")
    parser.add_argument("prompt", nargs="+", help="Natural-language request")
    args = parser.parse_args()

    text = " ".join(args.prompt)
    planner = RuleBasedPlanner()
    plan = planner.plan(text)
    gate = SafetyGate()
    decision = gate.evaluate(plan)

    print(f"Intent: {plan.intent}")
    print(f"Risk: {plan.risk_level}")
    print(f"Safety: {decision.decision} ({decision.reason})")

    if decision.decision == "DENY":
        print("Execution blocked by safety policy.")
        return

    if plan.steps and plan.steps[0].tool_name == "ls":
        executor = SafeExecutor()
        result = executor.execute_command("ls")
        print(result.output)
        return

    print("No executable MVP action available for this request.")


if __name__ == "__main__":
    main()
