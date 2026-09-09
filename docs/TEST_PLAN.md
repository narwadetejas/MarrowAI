# MarrowAI Test Plan

## Test levels

- Unit: schema validation, risk rules, path routing, state machines, redaction, cancellation.
- Integration: planner/provider adapter, retrieval, database, executor sandbox, audit writer, governor capability detection.
- API: contract/status/auth/idempotency/rate-limit/error tests.
- End-to-end: typed and voice-simulated journeys through confirmation, execution, feedback, and audit.
- Security: injection, privilege, replay, spoofing, secret leakage, eBPF rejection, unauthorized access.
- Accessibility: keyboard, screen reader labels/focus, non-color status, confirmation and kill switch.
- Performance: wake word, STT, safe CLI latency, GUI fallback latency, governor reaction, p50/p95.
- Regression: every fixed defect becomes a stable test.

## Requirement traceability

| Test | Requirement | Scenario and expected result |
|---|---|---|
| TEST-001 | REQ-001, REQ-002 | Submit valid text and simulated voice; both enter input pipeline; empty/unintelligible input does not execute. |
| TEST-002 | REQ-003, REQ-004 | Planner returns valid versioned JSON with retrieval hit; empty index uses bounded fallback and records retrieval status. |
| TEST-003 | REQ-005, REQ-028 | Safe/moderate/destructive fixtures classify correctly; malformed/untrusted fields are rejected. |
| TEST-004 | REQ-006, REQ-007 | Safe executes without confirmation; Moderate/Destructive remain blocked until current-plan confirmation. |
| TEST-005 | REQ-008 | Dry-run returns preview and creates no process/file/package side effect. |
| TEST-006 | REQ-009 | Supported operation selects CLI/API and never GUI path. |
| TEST-007 | REQ-010 | GUI-only fixture attempts AT-SPI first and vision only after AT-SPI failure. |
| TEST-008 | REQ-011 | Follow-up resolves valid context; ambiguous context asks clarification and executes nothing. |
| TEST-009 | REQ-012, REQ-013 | Feedback is emitted; kill switch cancels queued work and requests cancellation for active work. |
| TEST-010 | REQ-014, REQ-015, REQ-018 | Governor reacts to synthetic pressure without planner/LLM and records latency. |
| TEST-011 | REQ-016, REQ-017, REQ-019 | Approved eBPF loads; verifier/capability/kernel failure produces degraded/unavailable state with no false claim. |
| TEST-012 | REQ-020, REQ-028 | Operation runs with scoped privilege; shell metacharacters/paths cannot escape policy. |
| TEST-013 | REQ-021, REQ-024 | Failed speaker verification blocks voice-sensitive action; embedding is encrypted and deletion works. |
| TEST-014 | REQ-022, REQ-025 | Every attempt has sanitized audit record; retention/access policy is enforced after DEC-010. |
| TEST-015 | REQ-023, REQ-026 | Local-first voice path sends no audio off-device; hosted disclosure is shown; listening state is visible. |
| TEST-016 | REQ-027 | Demo profile refuses or constrains privileged execution outside approved sandbox policy. |
| TEST-017 | REQ-029, REQ-030 | Measure wake-word and short-command STT latency against targets. |
| TEST-018 | REQ-031, REQ-032 | Measure p50/p95 safe CLI and GUI fallback latency against targets. |
| TEST-019 | REQ-033, REQ-034 | Produce latency percentiles and per-class precision/recall; report destructive recall separately. |
| TEST-020 | REQ-035, REQ-036 | Compare governor with systemd-oomd/earlyoom and run planning/edit-distance plus SUS study. |
| TEST-021 | REQ-037, REQ-039 | Install/run on each supported Ubuntu release; user service starts in the graphical session without root-owned application state. |
| TEST-022 | REQ-038 | Create, migrate, close, reopen, and copy the SQLite `.db`; records remain readable and migrations are versioned. |
| TEST-023 | REQ-040, REQ-041 | Startup greets the current user through local TTS; unavailable audio produces a visible text welcome and does not block startup. |
| TEST-024 | REQ-042, REQ-043 | Disable network access and verify planning, STT/TTS adapter behavior, audit logging, SQLite access, and model adapter operate without remote calls; unknown Astra metadata is rejected. |

## Required negative and boundary cases

Test missing fields, blank input, oversized input/output, malformed provider output, unsupported command, missing binary/API, non-zero exit, timeout, duplicate submission, network/provider failure, database failure, disk-full audit failure, stale/expired confirmation, changed plan, concurrent cancellation, process disappearance, inaccessible GUI, low vision confidence, unsupported kernel, verifier rejection, capability denial, unauthorized user, forbidden action, replayed token, prompt injection in retrieved context, and secrets in logs.

## Release gates

All requirement tests mapped to implemented scope pass; no high-severity security finding remains; audit and cancellation behavior is verified; performance results are recorded; unsupported capabilities are represented honestly; unresolved decisions that affect the release scope are closed.
