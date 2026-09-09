# MarrowAI Product Requirements Document

## Product promise

MarrowAI lets a Linux operator describe system and desktop tasks in speech or text, produces a structured plan, applies a risk gate, and executes through the safest reliable path. Separately, it protects system health with kernel-aware resource governance that does not depend on the language model.

## Features

### F-001 Input and feedback
- Purpose: Accept typed or spoken requests and return understandable status/results.
- User: U-001; shared-device implications apply to U-003.
- Preconditions: The relevant input/output channel is installed and enabled.
- Main behavior: Accept text directly. For voice, use wake word, VAD, STT, and speaker verification as configured; return TTS and activity-log feedback when enabled.
- Alternative behavior: If voice is unavailable, continue with typed input. If TTS is unavailable, show textual status.
- Failure behavior: Show an actionable error and do not execute an unparsed request.
- Edge cases: Empty speech, speech timeout, unintelligible audio, disabled microphone, unavailable audio device, speaker verification failure.
- Acceptance criteria:
  - AC-001: A valid typed request enters the planning pipeline.
  - AC-002: An enabled voice request produces text or a clear non-execution error.
  - AC-003: No empty or failed transcription is executed.

### F-002 Retrieval-augmented planning
- Purpose: Convert natural language into an exact structured task plan.
- User: U-001.
- Preconditions: A planner/model is configured; retrieval may be empty on first use.
- Main behavior: Retrieve similar semantic/intent examples, provide targeted context to the planner, and validate the returned JSON plan.
- Alternative behavior: Use a bounded no-retrieval prompt when the retrieval store has no match.
- Failure behavior: Reject malformed or incomplete plans and request clarification or report inability to plan.
- Edge cases: Ambiguous target, unsupported task, malformed model output, conflicting retrieved examples, prompt/context limits.
- Acceptance criteria:
  - AC-004: Every accepted request yields a schema-valid plan containing action, target, arguments, execution path, and risk result or a recorded planning failure.
  - AC-005: Unsupported or ambiguous requests never reach execution.
  - AC-006: Retrieval failure does not silently fabricate context.

### F-003 Risk classification and confirmation
- Purpose: Prevent unsafe hands-free execution.
- User: U-001; U-002 configures privileges.
- Preconditions: A plan exists.
- Main behavior: Classify each action Safe, Moderate, or Destructive. Execute Safe without confirmation; require one confirmation for the other tiers. Voice Moderate/Destructive actions also require successful speaker verification.
- Alternative behavior: Typed confirmation may be used when voice is unavailable, subject to the configured deployment policy. [DECISION REQUIRED]
- Failure behavior: Deny or hold execution when classification, confirmation, or speaker verification fails.
- Edge cases: Confirmation timeout, changed plan after confirmation, repeated confirmation, kill switch during confirmation.
- Acceptance criteria:
  - AC-007: Safe actions can proceed without confirmation.
  - AC-008: Moderate and Destructive actions cannot execute without exactly one valid confirmation for the current plan.
  - AC-009: A failed speaker check blocks voice-triggered Moderate/Destructive execution.
  - AC-010: Dry run displays the proposed destructive command without executing it.

### F-004 Execution and GUI fallback
- Purpose: Carry out approved plans through reliable system interfaces.
- User: U-001.
- Preconditions: Plan is valid, risk gate passed, required privilege is available.
- Main behavior: Use a CLI/API executor first. For GUI-only actions, use AT-SPI first, then vision fallback. Record command, path, result, and outcome.
- Alternative behavior: Report that no safe supported execution path exists.
- Failure behavior: Stop the current action, preserve stderr/error context, and log failure without pretending success.
- Edge cases: Missing binary/API, timeout, non-zero exit, shell metacharacters, inaccessible app, stale GUI element, vision uncertainty, kill switch.
- Acceptance criteria:
  - AC-011: A supported CLI/API path is selected before GUI automation.
  - AC-012: GUI fallback order is AT-SPI then vision.
  - AC-013: Non-zero execution results are surfaced as failures and audited.
  - AC-014: User-controlled values are passed without unsafe shell interpolation.

### F-005 Conversational memory
- Purpose: Support follow-up requests without repeating context.
- User: U-001.
- Preconditions: A prior interaction exists in the active context.
- Main behavior: Resolve references from recent context and retrieval records while preserving plan validation and risk gates.
- Alternative behavior: Ask for clarification when context is insufficient.
- Failure behavior: Never infer a destructive target solely from uncertain context.
- Edge cases: Multiple possible antecedents, stale state, context truncation, deleted audit records.
- Acceptance criteria:
  - AC-015: A valid follow-up can reuse prior context.
  - AC-016: Ambiguous follow-ups ask for clarification and do not execute.

### F-006 Resource Governor
- Purpose: Detect and mitigate unhealthy memory/process pressure independently of the LLM.
- User: U-001 and U-002.
- Preconditions: Supported Linux PSI/cgroups/eBPF capabilities and configured policy.
- Main behavior: A user-space daemon reads telemetry and loads approved eBPF hooks; small verified kernel programs collect/enforce fast-path policy, while heavier classification remains in user space.
- Alternative behavior: Run deterministic PSI/cgroups baseline without ML when eBPF/model support is unavailable.
- Failure behavior: Report degraded mode; do not claim kernel enforcement if hooks are not loaded.
- Edge cases: Unsupported kernel, verifier rejection, capability denial, daemon crash, pressure oscillation, process exits before action.
- Acceptance criteria:
  - AC-017: Governor can report active, degraded, and unavailable states.
  - AC-018: Governor does not require an LLM round trip to react to pressure.
  - AC-019: Only verifier-accepted eBPF programs are loaded.
  - AC-020: Response latency is measured and compared with systemd-oomd and earlyoom.

### F-007 Audit, privacy, and control
- Purpose: Make actions accountable and protect sensitive data.
- User: U-001/U-002/U-003.
- Preconditions: Local storage and configured permissions.
- Main behavior: Log plan, risk, confirmation, execution path, outcome, and relevant errors; protect embeddings and logs; expose a manual kill switch.
- Alternative behavior: Disable voice/cloud features when privacy prerequisites are not met.
- Failure behavior: A logging failure must be visible and must not be treated as successful execution. [DECISION REQUIRED: fail closed vs. fail open]
- Edge cases: Disk full, log corruption, concurrent actions, retention expiry, re-enrollment, shared device.
- Acceptance criteria:
  - AC-021: Each attempted action has an audit record with outcome.
  - AC-022: Embeddings are encrypted at rest and can be deleted/re-enrolled.
  - AC-023: Kill switch prevents queued actions and requests cancellation of in-progress actions.
  - AC-024: Always-listening status is disclosed to shared-device users.

## MVP boundary

Phases 0-3 are the recommended MVP: command taxonomy/dataset, text planning and CLI/API execution, risk confirmation, and voice I/O. Resource Governor, GUI automation, shell, and full integration are stretch phases unless the team explicitly changes scope.

## Product gaps requiring decisions

See `OPEN_DECISIONS.md`. No feature may resolve those gaps by assumption.
