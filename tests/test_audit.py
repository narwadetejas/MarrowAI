from __future__ import annotations

from marrowai.audit import AuditLogger, redact_sensitive
from marrowai.interfaces import ExecutionResult, PlanStep, SafetyDecision, TaskPlan


def test_redact_sensitive_keys():
    payload = {
        "username": "alice",
        "api_key": "supersecret123",
        "nested": {
            "password": "mypassword",
            "safe_field": "hello",
            "user_token": "token_abc",
        },
        "list_items": [{"auth_code": "code123"}, "plain_text"],
    }
    redacted = redact_sensitive(payload)
    assert redacted["username"] == "alice"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["password"] == "[REDACTED]"
    assert redacted["nested"]["user_token"] == "[REDACTED]"
    assert redacted["nested"]["safe_field"] == "hello"
    assert redacted["list_items"][0]["auth_code"] == "[REDACTED]"
    assert redacted["list_items"][1] == "plain_text"


def test_audit_logger_records_events(tmp_path):
    log_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(log_path=str(log_file))

    logger.log_request("List files")

    plan = TaskPlan(
        intent="list_files",
        steps=[PlanStep("step-1", "cli", "list files", "ls", {"path": "."})],
        risk_level="low",
    )
    logger.log_plan(plan)

    decision = SafetyDecision("ALLOW", "safe", 0.95)
    logger.log_decision(decision)

    logger.log_governor_check(True, "All good")

    res = ExecutionResult("success", "file1.txt", 0)
    logger.log_tool_execution("ls", {"path": ".", "secret_token": "abc"}, res)

    events = logger.get_recent_events(limit=10)
    assert len(events) == 5

    assert events[0]["event_type"] == "REQUEST"
    assert events[0]["data"]["prompt"] == "List files"

    assert events[1]["event_type"] == "PLAN"
    assert events[1]["data"]["intent"] == "list_files"

    assert events[2]["event_type"] == "SAFETY_DECISION"
    assert events[2]["data"]["decision"] == "ALLOW"

    assert events[3]["event_type"] == "GOVERNOR_CHECK"
    assert events[3]["data"]["is_healthy"] is True

    assert events[4]["event_type"] == "TOOL_EXECUTION"
    assert events[4]["data"]["tool_name"] == "ls"
    assert events[4]["data"]["parameters"]["secret_token"] == "[REDACTED]"
