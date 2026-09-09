"""MarrowAI Ubuntu bootstrap and typed MVP entry point."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from .model import OfflinePlanner
from .storage import Database

DEFAULT_DB = Path.home() / ".local" / "share" / "marrowai" / "marrowai.db"


def welcome_message() -> str:
    user = os.environ.get("USER") or os.environ.get("LOGNAME") or "Ubuntu user"
    return f"Welcome {user}. MarrowAI is ready."


def speak(message: str) -> bool:
    """Use an installed local speech command when available; never require it."""
    for command in (("spd-say", message), ("espeak-ng", message), ("espeak", message)):
        if not _command_exists(command[0]):
            continue
        try:
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except OSError:
            continue
    return False


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run(request: str, database: Database) -> int:
    planner = OfflinePlanner()
    request_id = database.record_request("text", request)
    plan = planner.plan(request)
    plan_id = database.record_plan(
        request_id, planner.to_json(plan), plan.risk_tier, "planned"
    )
    database.record_event("plan_created", f"plan_id={plan_id}")
    print(planner.to_json(plan))
    if not plan.executable:
        return 2
    print(f"Planned safe operation; execution is intentionally disabled in bootstrap: {plan.operation}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline Ubuntu bootstrap for MarrowAI")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--welcome", action="store_true")
    parser.add_argument("--text", help="Plan a typed request")
    args = parser.parse_args()

    with Database(args.db) as database:
        if args.welcome or args.text is None:
            message = welcome_message()
            database.record_event("startup", message)
            print(message)
            speak(message)
        if args.text:
            return run(args.text, database)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
