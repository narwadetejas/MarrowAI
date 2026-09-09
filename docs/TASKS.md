# MarrowAI Implementation Tasks

Tasks are ordered by dependency. A task depending on an unresolved decision must remain blocked until that decision is recorded in `OPEN_DECISIONS.md`.

## TASK-001 Repository and specification baseline
- Requirements: all.
- Dependencies: none.
- Files/modules: repository structure, `docs/`.
- Objective: preserve docs as source of truth and establish implementation conventions.
- Validation: document consistency review.
- Complete when: every implementation PR links requirements and tests.

## TASK-002 Resolve release decisions and security model
- Requirements: REQ-020 to REQ-028.
- Dependencies: TASK-001; DEC-005, DEC-007, DEC-010, DEC-012, DEC-013, DEC-014, DEC-015, DEC-018, DEC-020.
- Files/modules: config, privilege policy, deployment docs.
- Objective: select supported OS/kernel, identity, permissions, secrets, retention, packaging, and kill-switch semantics.
- Validation: approval record and threat-model review.
- Complete when: no security-critical ambiguity remains.

## TASK-003 Input/output adapters
- Requirements: REQ-001, REQ-002, REQ-012, REQ-026, REQ-029, REQ-030.
- Dependencies: TASK-002; DEC-002, DEC-009.
- Files/modules: text/voice adapters, TTS, disclosure UI.
- Objective: normalize text and voice input and expose explicit failure states.
- Validation: TEST-001, TEST-015, TEST-017.
- Complete when: valid input is normalized and failed input cannot execute.

## TASK-004 Plan schema, retrieval, and planner adapter
- Requirements: REQ-003, REQ-004, REQ-011, REQ-028.
- Dependencies: TASK-002; DEC-002, DEC-003, DEC-006, DEC-007.
- Files/modules: plan schema, model adapter, retrieval adapter, context store.
- Objective: produce validated, versioned plans without direct execution capability.
- Validation: TEST-002, TEST-008, malformed-provider tests.
- Complete when: accepted plans are schema-valid and unsupported/ambiguous requests stop.

## TASK-005 Safety policy and confirmation state machine
- Requirements: REQ-005 to REQ-008, REQ-021, REQ-028.
- Dependencies: TASK-004; DEC-008, DEC-009, DEC-019.
- Files/modules: classifier, deterministic policy, confirmation/speaker gate.
- Objective: enforce risk tiers and current-plan confirmation.
- Validation: TEST-003, TEST-004, TEST-005, TEST-013, replay tests.
- Complete when: no Moderate/Destructive action bypasses gates.

## TASK-006 CLI/API executor
- Requirements: REQ-009, REQ-013, REQ-020, REQ-022, REQ-028.
- Dependencies: TASK-005; DEC-007, DEC-013.
- Files/modules: operation allowlist, subprocess/API adapters, cancellation.
- Objective: execute approved operations safely with bounded output/time and least privilege.
- Validation: TEST-006, TEST-009, TEST-012.
- Complete when: non-zero/timeout/cancel results are accurately reported and audited.

## TASK-007 GUI executor and shell
- Requirements: REQ-010, REQ-012, REQ-013, REQ-032.
- Dependencies: TASK-006; DEC-004, DEC-014, DEC-016, DEC-020.
- Files/modules: AT-SPI adapter, vision fallback, input simulation, GUI shell.
- Objective: implement accessibility-first GUI-only fallback and status/activity UI.
- Validation: TEST-007, TEST-009, TEST-018, accessibility tests.
- Complete when: path order and failure states are observable and safe.

## TASK-008 Resource Governor
- Requirements: REQ-014 to REQ-019, REQ-022, REQ-035.
- Dependencies: TASK-002; DEC-005, DEC-014.
- Files/modules: PSI/cgroups daemon, eBPF programs, capability detection.
- Objective: implement independent telemetry/enforcement with honest degraded modes.
- Validation: TEST-010, TEST-011, TEST-020, verifier tests.
- Complete when: governor reacts without LLM and reports capability state correctly.

## TASK-009 Persistence, audit, privacy controls
- Requirements: REQ-022 to REQ-028.
- Dependencies: TASK-002, TASK-004, TASK-005, TASK-006; DEC-010, DEC-011.
- Files/modules: migrations, repositories, encryption/key handling, audit writer.
- Objective: make plans/outcomes/audit authoritative and protect sensitive records.
- Validation: TEST-013 to TEST-016, database and disk-failure tests.
- Complete when: every attempt is durable or an explicit policy-controlled failure is surfaced.

## TASK-010 Evaluation and release hardening
- Requirements: REQ-029 to REQ-036.
- Dependencies: TASK-003 through TASK-009.
- Files/modules: benchmark harness, metrics, regression/security suites.
- Objective: measure targets, compare baselines, run SUS/planning evaluation, and close release gates.
- Validation: TEST-017 to TEST-020 plus full regression/security suite.
- Complete when: results and residual risks are documented.

## TASK-011 Ubuntu bootstrap, SQLite, startup, and offline model boundary
- Requirements: REQ-037 to REQ-043.
- Dependencies: TASK-001, TASK-002; DEC-014, DEC-021, DEC-022, DEC-023, DEC-024.
- Files/modules: `app/bootstrap/`, `app/storage/`, `app/model/`, `deploy/systemd/`, SQLite migrations.
- Objective: create the Ubuntu application entry point, portable `.db` initialization/migrations, offline model adapter contract, user-session startup service, and personalized welcome fallback.
- Validation: TEST-021 to TEST-024 plus supported-release and permission checks.
- Complete when: a supported Ubuntu user can install, start on login, hear or see the personalized welcome, use the offline adapter, and reopen the same `.db` without data loss.
