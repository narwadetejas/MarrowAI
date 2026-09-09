# MarrowAI Architecture

## 1. Architectural principles

- Linux-first, local-first, least privilege.
- The LLM plans; deterministic policy gates and executors decide whether/how to act.
- CLI/API before GUI; AT-SPI before vision.
- Resource governance is independent of planning and must degrade honestly.
- Kernel contact is limited to verified eBPF loaded by a user-space daemon.

## 2. Logical architecture

```text
Typed/Voice Input
  -> Input Adapter (user space)
  -> Planner + Retrieval (user space)
  -> Plan Schema Validator
  -> Risk Classifier + Policy Gate
  -> Confirmation/Speaker Gate (when required)
  -> Executor Router
       -> CLI/API Executor
       -> GUI Executor: AT-SPI -> vision fallback
  -> Audit/Event Store
  -> TTS + Activity Log

PSI/cgroups/eBPF telemetry -> Resource Governor daemon
  -> deterministic/small fast-path policy
  -> cgroup/process action + audit event
```

Components communicate through typed internal interfaces. The planner never invokes subprocesses directly. The executor never accepts an unvalidated free-form model response.

## 3. Components and boundaries

- Input adapters: text, wake-word/VAD, STT, speaker verification. User space.
- Planner: model adapter, retrieval adapter, structured-plan validator. User space.
- Safety: risk classifier, allowlist/policy engine, confirmation coordinator. User space.
- Execution: subprocess/API adapter, GUI adapter, cancellation manager. User space.
- Resource Governor: daemon for PSI/cgroups/eBPF lifecycle and policy; restricted eBPF programs in kernel space.
- Feedback: TTS adapter and activity-log reader. User space.
- Persistence: plans, actions, confirmations, audit events, conversation context, embeddings metadata, governor events.

The exact process split, IPC mechanism, and deployment service layout are [DECISION REQUIRED]. A modular single-host process is the default starting point; split services require a measured isolation need.

## 4. Data flow

1. Input adapter emits a normalized request with source and timestamp.
2. Planner retrieves relevant prior examples/context and returns a versioned JSON plan.
3. Schema validator rejects malformed plans.
4. Risk classifier and deterministic policy evaluate every action.
5. Safety coordinator requests confirmation and speaker verification as required.
6. Executor router selects CLI/API, AT-SPI, or vision path.
7. Cancellation manager checks kill-switch state before and during cancellable operations.
8. Audit writer records plan, policy, confirmation, execution, and outcome.
9. Feedback adapter reports status/result.
10. Governor operates independently and emits resource events to the same audit/event boundary.

## 5. Authentication and authorization

The baseline assumes the process runs under a local Linux account and uses OS permissions plus narrowly scoped sudoers/capabilities. No application login protocol is specified. [DECISION REQUIRED: additional authentication model]

Authorization is enforced server-/executor-side using an allowlist of operations, validated arguments, scoped privilege escalation, and policy checks. UI state cannot authorize an action.

## 6. Background processing and concurrency

Voice capture, resource telemetry, and long-running executions are asynchronous concerns. Each action receives an ID and lifecycle state. The system must prevent a stale confirmation from authorizing a changed plan. Exact queue/concurrency policy is [DECISION REQUIRED].

## 7. Persistence, cache, and storage

Use SQLite for durable records in the configured `.db` file and a separate protected location for speaker embeddings. Retrieval indexes may be rebuildable derived data. No remote object storage is required. SQLite migration tooling and the final database path remain [DECISION REQUIRED], but the database family is fixed.

## 8. Error handling

Errors are typed by input, planning, validation, authorization, capability, execution, cancellation, persistence, and integration categories. Every error exposed to the user is safe to display and includes whether execution occurred. Unknown execution state is never reported as success.

Degraded modes:

- Text-only when voice fails.
- No-retrieval planning when the index is unavailable, without fabricating examples.
- Deterministic PSI/cgroups governance when eBPF/model support is unavailable.
- No GUI action when both AT-SPI and vision paths fail.

## 9. Logging and observability

Structured logs must include correlation ID, action ID, component, lifecycle state, duration, and sanitized error details. Audit records are separate from diagnostic logs and have stronger access/retention controls. Secrets, raw audio, embeddings, and command credentials must not enter ordinary logs.

## 10. Deployment

The target deployment is an Ubuntu desktop user session. The application starts through a user-level systemd service, stores ordinary state under the user account, and does not run the GUI application as root. The Resource Governor may require separately approved capabilities. Demo deployments should run in a VM/container before privileged execution. Packaging and supported Ubuntu releases remain [DECISION REQUIRED].
