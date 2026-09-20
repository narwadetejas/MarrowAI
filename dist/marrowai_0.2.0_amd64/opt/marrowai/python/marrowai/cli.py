from __future__ import annotations

import json
import sys
from .assistant import MarrowAssistant
from .audit import AuditLogger


def _show_audit(limit: int = 15) -> None:
    events = AuditLogger().get_recent_events(limit=limit)
    if not events:
        print("No audit events recorded yet.")
        return
    print(f"Recent Audit Log ({len(events)} events):")
    for event in events:
        ts = event.get("timestamp", "unknown")
        ev_type = event.get("event_type", "UNKNOWN")
        data = json.dumps(event.get("data", {}))
        print(f"[{ts}] {ev_type:<16} {data}")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help"}:
        print("Usage: marrowai [run] <prompt> | doctor | audit | chat | scaffold <name>")
        print("\nCommands:")
        print("  <prompt>            Execute natural-language request safely")
        print("  run <prompt>        Explicitly run a task plan")
        print("  doctor              Run system diagnostic check")
        print("  audit               View recent security and execution audit events")
        print("  chat                Start interactive conversational session")
        print("  scaffold <name>     Scaffold a new backend project")
        return

    first_arg = args[0].lower()

    if first_arg == "doctor":
        from .doctor import main as doctor_main
        doctor_main()
        return

    if first_arg == "audit":
        limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 15
        _show_audit(limit)
        return

    if first_arg == "chat":
        from .interactive import InteractiveSession
        InteractiveSession().run()
        return

    if first_arg == "scaffold" and len(args) > 1:
        from .scaffold import ProjectScaffold
        name = args[1]
        ok = ProjectScaffold().create_backend_project(name)
        print(f"Scaffold {name}: {'created successfully' if ok else 'failed'}")
        return

    if first_arg == "run":
        prompt_parts = args[1:]
    else:
        prompt_parts = args

    if not prompt_parts:
        print("Error: No prompt provided to execute.")
        sys.exit(1)

    text = " ".join(prompt_parts)
    result = MarrowAssistant().process(text)

    print(f"Intent: {result['intent']}")
    print(f"Risk: {result['risk_level']}")
    print(f"Safety: {result['decision']}")
    print(f"Status: {result['status']}")
    if result.get("output"):
        print(result["output"])


if __name__ == "__main__":
    main()
