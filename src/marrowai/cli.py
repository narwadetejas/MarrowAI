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
        print("Usage: marrowai [run] <prompt> | doctor | audit | chat [--voice female|male] | gui | web | scaffold <name>")
        print("\nCommands:")
        print("  <prompt>                       Execute natural-language request safely")
        print("  run <prompt>                   Explicitly run a task plan")
        print("  doctor                         Run system diagnostic check")
        print("  audit                          View recent security and execution audit events")
        print("  chat [--voice female|male]     Start interactive conversational session with Indian voice")
        print("  gui                            Launch desktop Dark Mode workstation GUI")
        print("  web                            Launch modern browser Web Workstation dashboard")
        print("  scaffold <name>                Scaffold a new backend project")
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

    if first_arg == "gui":
        from .gui import main as gui_main
        gui_main()
        return

    if first_arg == "web":
        from .web_gui import run_web_dashboard
        port = int(args[1]) if len(args) > 1 and args[1].isdigit() else 8765
        run_web_dashboard(port=port)
        return

    if first_arg == "chat":
        from .interactive import InteractiveSession
        voice = None
        if len(args) > 2 and args[1] in {"--voice", "-v"}:
            voice = args[2]
        elif len(args) > 1 and not args[1].startswith("-"):
            voice = args[1]
        InteractiveSession(voice_profile=voice).run()
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

    auto_confirm = False
    filtered_parts = []
    for p in prompt_parts:
        if p in {"-y", "--yes"}:
            auto_confirm = True
        else:
            filtered_parts.append(p)

    text = " ".join(filtered_parts)
    assistant = MarrowAssistant()
    result = assistant.process(text, confirmed=auto_confirm)

    if result.get("status") == "requires_confirmation" and not auto_confirm:
        conf_msg = result.get("output", "⚠️ This task requires confirmation to proceed.")
        print(f"\n[SECURITY GATE]: {conf_msg}")
        try:
            conf_input = input("Authorize and execute? [y/N or sudo password]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(0)
        if conf_input.lower() in {"y", "yes", "confirm", "proceed", "approve"}:
            result = assistant.process("yes", confirmed=True)
        elif len(conf_input) > 0 and conf_input.lower() not in {"n", "no", "cancel"}:
            result = assistant.process("yes", confirmed=True, password=conf_input)
        else:
            print("Action cancelled.")
            sys.exit(0)

    print(f"Intent: {result['intent']}")
    print(f"Risk: {result['risk_level']}")
    print(f"Safety: {result['decision']}")
    print(f"Status: {result['status']}")
    if result.get("output"):
        print(result["output"])



if __name__ == "__main__":
    main()
