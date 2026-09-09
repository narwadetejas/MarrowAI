# MarrowAI API and Interface Specification

The PRD does not define transport. The contracts below are logical local interfaces. HTTP route names are a proposed local API and require DEC-012/DEC-015 approval before public exposure.

## Conventions

- JSON UTF-8; timestamps are ISO-8601 UTC; IDs are opaque.
- Every request includes or receives a correlation ID.
- Client-provided risk, privilege, execution path, and outcome are ignored; server policy computes them.
- Error body: `{ "error": { "code": "string", "message": "safe string", "correlation_id": "string", "retryable": boolean } }`.
- No endpoint returns secrets, raw embeddings, or unsanitized credentials.

## `POST /v1/requests`
Purpose: submit typed or transcribed text for planning.

Auth: local OS/API authentication per DEC-012. Authorization: operator.

Request:
```json
{"session_id":"id","source":"text","text":"show memory pressure","dry_run":false}
```
Validation: non-empty bounded text; source must be `text` or `voice`; session must be accessible; dry_run boolean. Idempotency: optional `Idempotency-Key`; duplicate key returns the original request/result.

Response `202 Accepted`:
```json
{"request_id":"id","status":"planning","correlation_id":"id"}
```
Errors: `400` invalid input, `401` unauthenticated, `403` forbidden, `409` duplicate/conflict, `413` too large, `429` rate limit, `503` unavailable.

## `GET /v1/requests/{request_id}`
Returns request, plan status, policy status, execution status, and sanitized result. Auth/authorization: owner/operator. `200`, `401`, `403`, `404`.

## `POST /v1/actions/{action_id}/confirm`
Purpose: authorize a current Moderate/Destructive action.

Request:
```json
{"confirmation":"approve","speaker_verification_token":"opaque"}
```
Validation: confirmation must match the displayed plan fingerprint; token required for voice-gated action; expired/stale confirmations rejected. The exact typed/voice policy is DEC-008.

Response `202` with action lifecycle or `409` if stale/already handled. Other errors: `400`, `401`, `403`, `404`, `410` expired, `429`.

## `POST /v1/actions/{action_id}/cancel`
Purpose: request cancellation and/or remove a queued action.

Auth: operator. Request may include a reason. Response `202` with `cancellation_requested`; `404`, `409`, or `503` as appropriate. Cancellation is best effort for non-interruptible OS operations and must be audited.

## `POST /v1/actions/{action_id}/dry-run`
Purpose: produce a non-executing preview for a destructive action.

Auth: operator; policy still validates the plan. Response `200` includes sanitized planned path/command, risk, required privileges, and warnings. It must not run the command. `409` if plan changed or unsupported.

## `GET /v1/activity`
Purpose: paginated activity/audit view.

Query: `cursor`, `limit` bounded by server, optional `status`, `risk_tier`, `from`, `to`. Auth: operator with audit-read permission. Response `200`: `{items,next_cursor}`. `400`, `401`, `403`, `429`.

## `GET /v1/governor/status`
Returns capability state (`active`, `degraded`, `unavailable`), kernel/eBPF support summary, latest pressure snapshot, and last reaction latency. Auth: operator. `200`, `401`, `403`, `503`.

## `POST /v1/governor/kill-switch`
Purpose: stop queued/in-progress MarrowAI actions. Auth: operator with kill-switch permission. Response `202`; action outcomes remain auditable. Exact cancellation guarantee is DEC-020.

## Internal interfaces

- `Planner.plan(request, retrieved_context) -> ValidatedPlan | PlanningError`
- `RiskPolicy.evaluate(action, context) -> PolicyDecision`
- `ConfirmationGate.authorize(action, decision, proof) -> AuthorizationResult`
- `Executor.execute(action, cancellation_token) -> ExecutionResult`
- `Governor.status() -> GovernorStatus`
- `Audit.append(event) -> durable acknowledgment`

All interfaces must return explicit failure states and must not throw unclassified execution ambiguity across the safety boundary.
