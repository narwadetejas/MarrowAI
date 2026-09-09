# MarrowAI UI Specification

The PRD requires a GUI shell with terminal plus voice/chat panel and an activity log, but does not select a toolkit or visual system. The following defines behavior without inventing visual styling. Visual tokens/layout are [DESIGN DECISION REQUIRED].

On each enabled Ubuntu graphical-session startup, the shell must show `Welcome <current user>. MarrowAI is ready.` and request local TTS for the same message. Audio failure must leave the shell usable and show the text message.

## Screen: Main assistant
- Route: local shell main view; exact route is [DESIGN DECISION REQUIRED].
- User: U-001.
- Components: text input, voice status/control, submit action, current plan/status, confirmation region, result/error region, kill-switch control, governor status indicator.
- Data: current request, plan summary, risk tier, required confirmation, execution state, result.
- Actions: submit, confirm, reject/cancel, dry-run, kill switch, open activity.
- Loading: show planning/executing state and disable duplicate submission for the same idempotency key.
- Empty: show an input-ready state with no fabricated example task.
- Error: identify whether failure occurred in input, planning, authorization, capability, or execution; state whether anything ran.
- Success: show outcome, execution path, duration, and audit reference.
- Validation: reject blank/oversized input locally, then repeat server validation.
- Responsive/accessibility: keyboard usable, screen-reader labels, focus moves to confirmation/error, status not conveyed by color alone. Exact breakpoints are [DESIGN DECISION REQUIRED].

## Screen: Confirmation
- Purpose: make Moderate/Destructive action and consequences explicit.
- Data: plan fingerprint, action summary, target, risk tier, dry-run preview/warnings, required privilege, expiry.
- Actions: confirm, cancel, dry run.
- Behavior: confirmation is tied to the exact plan fingerprint; changed plans require a new confirmation.
- Error: stale, expired, failed speaker verification, or unavailable privilege blocks execution.
- Accessibility: confirmation and cancellation are distinct, keyboard reachable, and announced.

## Screen: Activity log
- Purpose: inspect planned actions and outcomes.
- Data: time, request summary, risk, path, status, result, correlation/audit ID.
- Actions: filter by time/status/risk, open detail, request cancellation where permitted.
- Loading/empty/error/success: standard asynchronous states; an empty log is a valid state.
- Privacy: redact secrets and restrict access according to audit permissions.

## Screen: Resource Governor status
- Purpose: show active/degraded/unavailable governance honestly.
- Data: capability state, PSI snapshot, cgroup/policy state, latest reaction latency, recent interventions.
- Actions: inspect detail and navigate to activity events. Controls that change governance policy are [DECISION REQUIRED].
- Error: explain unsupported kernel/capability without claiming eBPF operation.

## Reusable components

- `StatusBadge`: text plus accessible status, never color-only.
- `PlanSummary`: renders server-validated plan fields, never raw model prose as executable instruction.
- `RiskNotice`: consistent Safe/Moderate/Destructive treatment.
- `ConfirmationPanel`: exact-plan confirmation and expiry.
- `ActivityRow`: sanitized event summary with stable IDs.
- `KillSwitch`: prominent, keyboard accessible, requires defined interaction policy [DECISION REQUIRED].
- `VoiceState`: microphone/listening/transcribing/verification/error state with disclosure when always-listening is enabled.

## Navigation and failure policy

Navigation must not discard an active confirmation or execution state without warning. Network failure after submission must allow status re-fetch and must not encourage duplicate execution. UI authorization is advisory; all enforcement is server/executor-side.
