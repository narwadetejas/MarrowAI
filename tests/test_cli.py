from __future__ import annotations

import sys
from marrowai.cli import main


def test_cli_help(capsys):
    sys.argv = ["marrowai", "--help"]
    main()
    captured = capsys.readouterr()
    assert "Usage: marrowai" in captured.out
    assert "doctor" in captured.out
    assert "audit" in captured.out


def test_cli_doctor(capsys):
    sys.argv = ["marrowai", "doctor"]
    main()
    captured = capsys.readouterr()
    assert "Platform:" in captured.out
    assert "Python:" in captured.out


def test_cli_run_safe_task(capsys):
    sys.argv = ["marrowai", "run", "List the files in the current workspace"]
    main()
    captured = capsys.readouterr()
    assert "Intent: list_files" in captured.out
    assert "Safety: ALLOW" in captured.out
    assert "Status: success" in captured.out


def test_cli_audit_command(capsys):
    sys.argv = ["marrowai", "audit"]
    main()
    captured = capsys.readouterr()
    assert "Audit Log" in captured.out or "No audit events" in captured.out
