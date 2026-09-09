# MarrowAI Database Specification

The application uses SQLite for durable plans, outcomes, context, audit data, and protected speaker metadata. The schema below is logical; SQLite driver, migration tooling, database path, and encryption mechanism are [DECISION REQUIRED].

## Source-of-truth rules

- The validated task plan is the source of truth for intended action.
- The policy decision is the source of truth for risk/authorization at execution time.
- The execution result is the source of truth for outcome; model text is not.
- Retrieval indexes are derived and rebuildable, never the authoritative action record.
- Speaker embeddings are sensitive credentials/biometric data and are not stored in the ordinary audit table.

## Tables

### `conversation_sessions`
Purpose: active conversational context.

Columns: `id` UUID/text PK; `created_at` timestamp required; `updated_at` timestamp required; `status` enum required; `context_version` integer required.

Indexes: `(updated_at)`, `(status, updated_at)`.

Rules: status values and expiration policy are [DECISION REQUIRED]. Delete behavior must not delete required audit records.

### `requests`
Purpose: normalized user input.

Columns: `id` PK; `session_id` FK required; `source` enum (`text`, `voice`) required; `input_text` encrypted/protected text required after transcription; `received_at` timestamp required; `correlation_id` unique required; `transcription_metadata` protected JSON optional.

Indexes: unique `correlation_id`, `(session_id, received_at)`.

Rules: raw audio is not stored by default; retention is [DECISION REQUIRED].

### `plans`
Purpose: validated planner output.

Columns: `id` PK; `request_id` FK unique required; `schema_version` text required; `plan_json` validated JSON required; `planner_provider` text required; `retrieval_status` enum required; `created_at` timestamp required; `validation_status` enum required.

Rules: immutable after validation; a changed plan gets a new record.

### `actions`
Purpose: individual executable actions from a plan.

Columns: `id` PK; `plan_id` FK required; `sequence_no` integer required; `operation` text required; `target` text required; `arguments_json` validated JSON required; `preferred_path` enum required; `lifecycle_state` enum required; `created_at` timestamp required.

Constraints: unique `(plan_id, sequence_no)`; state transitions must be validated.

### `policy_decisions`
Purpose: risk and authorization result.

Columns: `id` PK; `action_id` FK unique required; `risk_tier` enum (`safe`, `moderate`, `destructive`) required; `classifier_version` text required; `policy_result` enum required; `reasons_json` required; `created_at` timestamp required.

Rules: deterministic policy may raise risk; no action executes without an accepted decision.

### `confirmations`
Purpose: confirmation and speaker-gate events.

Columns: `id` PK; `action_id` FK required; `method` enum required; `result` enum required; `speaker_verification_result` enum optional; `plan_fingerprint` required; `created_at` timestamp required; `expires_at` timestamp required.

Constraints: confirmation must match current plan fingerprint; only one accepted confirmation may authorize an action. Timeout/retry policy is [DECISION REQUIRED].

### `executions`
Purpose: execution attempt and result.

Columns: `id` PK; `action_id` FK required; `path` enum (`cli_api`, `at_spi`, `vision`) required; `started_at` timestamp required; `finished_at` timestamp optional; `exit_code` integer optional; `status` enum required; `stdout` protected text optional; `stderr` protected text optional; `cancellation_requested` boolean required.

Rules: unknown status is distinct from success; secrets must be redacted.

### `audit_events`
Purpose: append-only accountability record.

Columns: `id` PK; `correlation_id` required; `event_type` required; `actor` required; `action_id` FK optional; `payload_json` sanitized required; `created_at` timestamp required.

Indexes: `(correlation_id, created_at)`, `(event_type, created_at)`.

Rules: append-only for ordinary application roles; retention and deletion are [DECISION REQUIRED].

### `governor_events`
Purpose: resource-governance telemetry/intervention events.

Columns: `id` PK; `event_type` required; `kernel_capability_state` required; `pressure_snapshot_json` required; `policy_action` optional; `latency_ms` optional; `created_at` timestamp required.

Indexes: `(created_at)`, `(event_type, created_at)`.

### `speaker_profiles`
Purpose: metadata for protected embeddings.

Columns: `id` PK; `subject_label` required; `embedding_reference` unique required; `enrolled_at` required; `updated_at` required; `status` enum required; `deleted_at` optional.

The embedding bytes must be stored encrypted in a protected store; exact format/key management is [DECISION REQUIRED].

## Relationships

Session 1-to-many requests; request 1-to-1 plan; plan 1-to-many actions; action 1-to-1 policy decision and 0-to-many confirmations/executions; actions and governor activity produce audit events; speaker profiles are referenced only by verification metadata.

## Migration requirements

Use versioned, reversible migrations where possible. Schema changes must preserve audit immutability, plan schema versioning, and encrypted-data key rotation compatibility. Add indexes based on measured query paths, not speculation.
