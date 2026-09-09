# MarrowAI Project Specification

Status: implementation-ready Ubuntu baseline derived from PRD v3 and subsequent project decisions. This document is the source of truth for implementation.

## 1. Product Overview

MarrowAI is an Ubuntu desktop application that accepts voice and typed requests for system-administration and desktop tasks. It converts natural-language requests into structured plans, evaluates risk before execution, and routes work through direct CLI/API calls whenever possible. A separate Resource Governor monitors Linux kernel pressure signals and can intervene before memory and process load become unhealthy.

The language model, speech processing, safety classifier, command executor, GUI automation, and user interface run in user space. Only small, verifier-checked eBPF programs loaded by the Resource Governor touch kernel space. MarrowAI does not place an LLM in the kernel and does not require a custom kernel module.

## 2. Goals

- G-001: Reduce command-syntax burden for routine Linux administration and desktop tasks.
- G-002: Provide hands-free voice and typed interaction with risk-aware execution.
- G-003: Execute low-risk actions directly while requiring confirmation for moderate and destructive actions.
- G-004: Prefer reliable CLI/API execution over GUI clicking.
- G-005: Provide proactive, kernel-aware resource governance independently of the LLM.
- G-006: Preserve user control through least privilege, dry-run support, auditability, and a kill switch.
- G-007: Produce an MVP for phases 0-3 before treating eBPF, GUI automation, and full integration as stretch scope.
- G-008: Start automatically with the Ubuntu user's graphical session and greet that user by name through local voice output when available.
- G-009: Operate offline for voice processing, planning, persistence, and speech output; no hosted model is required for normal operation.
- G-010: Store durable application data in a portable SQLite `.db` file with versioned migrations.

## 3. Users and Roles

- U-001: Local Ubuntu desktop operator using typed or spoken requests.
- U-002: Administrator who grants scoped privileges and configures deployment.
- U-003: Shared-device participant who must be informed when always-listening wake-word detection is enabled.
- U-004: Developer/reviewer who evaluates plans, risk classification, performance, and audit records.

No separate multi-user account model, remote administration role, or tenant model is defined. [DECISION REQUIRED: deployment user/administrator model]

## 4. Scope

### In scope

- Ubuntu desktop packaging and automatic startup through a user-level systemd service.
- Personalized startup greeting using the current Ubuntu account name and local TTS.
- Typed and spoken natural-language requests.
- Wake word, VAD, local or configured STT, speaker verification, and TTS.
- Retrieval-augmented planning that returns a structured JSON task plan.
- Safe, Moderate, and Destructive risk classification.
- One confirmation loop for Moderate and Destructive actions.
- CLI/API-first execution with AT-SPI and vision fallback for GUI-only actions.
- Conversational context and semantic/intent retrieval.
- PSI and cgroups v2 monitoring.
- Small eBPF hooks for resource-governance telemetry/enforcement.
- Activity/audit logging, dry-run mode, and manual kill switch.
- Evaluation against task-planning, latency, usability, and resource-governance baselines.

### Out of scope for the baseline

- An LLM executing in kernel space.
- A custom kernel module or kernel patch.
- Unrestricted root access.
- A claim that the underlying techniques are individually novel.
- Guaranteed identical behavior on every distribution or hardened kernel.
- Full seven-phase delivery as an MVP.
- Any feature not supported by the supplied PRD.

## 5. Stable Requirements

### Product behavior

- REQ-001: The system MUST accept typed requests.
- REQ-002: The system MUST support spoken requests through wake-word/VAD/STT components when voice is enabled.
- REQ-003: The system MUST convert a request into an exact structured task plan before execution.
- REQ-004: Planning MUST use retrieval of semantically and/or intentionally similar prior requests where configured.
- REQ-005: Every planned action MUST receive a Safe, Moderate, or Destructive risk classification before execution.
- REQ-006: Safe actions MAY execute without an interactive confirmation.
- REQ-007: Moderate and Destructive actions MUST require one brief confirmation before execution.
- REQ-008: The system MUST support dry-run previews for destructive commands.
- REQ-009: The system MUST prefer a direct CLI/API path when one exists.
- REQ-010: GUI automation MUST use accessibility-tree control before vision fallback for GUI-only actions.
- REQ-011: The system MUST preserve conversational context for follow-up requests.
- REQ-012: The system MUST provide user feedback through TTS and a GUI activity log when those channels are enabled.
- REQ-013: A manual kill switch MUST stop in-progress or queued actions as quickly as the executor permits.

### Resource governance

- REQ-014: Resource governance MUST operate independently of the LLM.
- REQ-015: The Resource Governor MUST consume Linux PSI and cgroups v2 signals where supported.
- REQ-016: Kernel-space code MUST be limited to small, verifier-checked eBPF programs.
- REQ-017: Heavy models and reasoning MUST remain in user space.
- REQ-018: Resource-governance reaction target is sub-second through the eBPF path.
- REQ-019: The system MUST document and handle unsupported/insufficient kernel capabilities.

### Security, privacy, and operations

- REQ-020: Execution MUST use scoped sudoers rules and/or Linux capabilities rather than blanket root access.
- REQ-021: Moderate and Destructive actions MUST be gated by speaker verification when voice is used.
- REQ-022: The system MUST record each planned action, risk classification, and outcome in an audit log.
- REQ-023: Voice processing SHOULD default to on-device; hosted reasoning MUST disclose what leaves the device and the provider retention policy.
- REQ-024: Speaker embeddings MUST be encrypted at rest, deletable, and non-exported by default.
- REQ-025: Audit logs MUST have access controls and a defined retention window. [DECISION REQUIRED: retention duration]
- REQ-026: Shared-device users MUST be informed when always-listening wake-word detection is enabled.
- REQ-027: Academic/demo deployments SHOULD use a sandboxed VM or container before production/root access.
- REQ-028: External and user input MUST be validated before planning, confirmation, and execution.
- REQ-037: The system MUST target Ubuntu desktop and document a supported release range; it MUST report unsupported releases instead of claiming universal compatibility.
- REQ-038: The system MUST use SQLite as its local durable database and store it as a `.db` file with versioned migrations.
- REQ-039: The system MUST start automatically for the configured Ubuntu graphical user session through a user-level startup service.
- REQ-040: On successful startup, the system MUST greet the current Ubuntu user by name through local TTS when audio output is available.
- REQ-041: If TTS or audio output is unavailable, startup MUST continue and display the welcome message as text.
- REQ-042: Normal request planning, voice processing, TTS, audit logging, and database access MUST work offline.
- REQ-043: The model layer MUST use a replaceable offline model adapter; the exact model/runtime is blocked on DEC-021.

### Quality targets

- REQ-029: Wake-word detection target is under 300 ms.
- REQ-030: Short-command local STT target is under 1 second.
- REQ-031: Safe-tier CLI/API end-to-end target is under 2 seconds.
- REQ-032: GUI fallback target is 2-4 seconds and is not the default path.
- REQ-033: Evaluation MUST report p50 and p95 latency by execution path.
- REQ-034: Evaluation MUST report risk-classifier precision and recall per class, prioritizing Destructive recall.
- REQ-035: Evaluation MUST compare Resource Governor response against systemd-oomd and earlyoom baselines.
- REQ-036: Evaluation MUST include task-planning accuracy/edit distance and a SUS study against manual CLI use.

## 6. Business and Safety Rules

- RULE-001: No action executes before planning and risk classification.
- RULE-002: Confirmation is mandatory for Moderate and Destructive actions and cannot be removed as a convenience setting.
- RULE-003: The fastest path is not automatically the selected path; reliable and safe CLI/API execution takes precedence over GUI automation.
- RULE-004: The LLM is not a real-time resource-governance dependency.
- RULE-005: A model is not permitted in eBPF merely because it is accurate; it must fit verifier and performance limits.
- RULE-006: The system must not claim kernel-integrated LLM execution.
- RULE-007: User-supplied command text, paths, arguments, and confirmation responses are untrusted input.
- RULE-008: Automatic startup must not grant root privileges to the graphical application.
- RULE-009: A portable `.db` file does not make kernel hooks or third-party model runtimes portable; capability checks remain mandatory.
- RULE-010: Offline mode is the default and must not silently send request/audio data to a remote provider.

## 7. Assumptions and Constraints

- Ubuntu desktop is the target operating system. The supported Ubuntu release range is [DECISION REQUIRED].
- The SQLite database file is portable across supported Ubuntu releases, but application dependencies and eBPF capabilities are not guaranteed on every Ubuntu release.
- Normal operation must not require internet access or a hosted LLM.
- “Astra” is not yet an implementable model selection because its exact offline model/runtime identity is unspecified. See DEC-021.
- eBPF requires a sufficiently recent kernel, stated by the PRD as 5.x+, and elevated capabilities.
- Distribution and hardened-kernel behavior may differ.
- Local LLMs improve privacy but may trade accuracy and speed against hosted APIs.
- The complete scope is ambitious for a solo/small student team; phases 0-3 are the recommended MVP.
- Concrete model, vector database, UI toolkit, packaging, and API provider are not fixed. See `OPEN_DECISIONS.md`.

## 8. Traceability Matrix

| Requirement | Feature | Architecture | Task | Code area | Test |
|---|---|---|---|---|---|
| REQ-001, REQ-002 | F-001 Input | Input layer | TASK-003 | input adapters | TEST-001 |
| REQ-003 to REQ-005 | F-002 Planning and risk | Reasoning/Safety layers | TASK-004, TASK-005 | planner, classifier | TEST-002, TEST-003 |
| REQ-006 to REQ-008 | F-003 Confirmation/dry run | Safety/execution | TASK-005, TASK-006 | policy gate | TEST-004, TEST-005 |
| REQ-009 to REQ-013 | F-004 Execution/feedback | Executor/feedback | TASK-006, TASK-007 | CLI, GUI, activity log | TEST-006 to TEST-009 |
| REQ-014 to REQ-019 | F-005 Resource Governor | Governor/eBPF | TASK-008 | governor daemon, eBPF | TEST-010, TEST-011 |
| REQ-020 to REQ-028 | F-006 Security/privacy | Security controls | TASK-002, TASK-005, TASK-009 | privilege, audit, secrets | TEST-012 to TEST-016 |
| REQ-029 to REQ-036 | F-007 Evaluation | Observability/evaluation | TASK-010 | benchmark harness | TEST-017 to TEST-020 |
| REQ-037 to REQ-043 | F-008 Ubuntu/offline startup | Ubuntu service, SQLite, local model adapter | TASK-011 | `app/bootstrap/`, `app/storage/`, `deploy/systemd/`, `app/model/` | TEST-021 to TEST-024 |

Unresolved traceability items are listed in `OPEN_DECISIONS.md`; they must be resolved before implementation tasks that depend on them begin.
