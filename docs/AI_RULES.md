# MarrowAI Coding-Agent Rules

## Source of truth

1. Read the relevant documents in `docs/` before modifying code.
2. Treat `PROJECT_SPEC.md`, `PRD.md`, `ARCHITECTURE.md`, and the applicable contract as authoritative.
3. Never invent missing requirements; use `[DECISION REQUIRED]` and stop at the affected boundary.
4. Never silently change requirements or architecture.
5. Never introduce unnecessary dependencies or alternate frameworks.

## Safety and security

6. Never remove tests to make them pass.
7. Never weaken security, confirmation, least privilege, validation, audit, or privacy controls for convenience.
8. Never expose secrets, raw audio, speaker embeddings, credentials, or unsanitized command output.
9. Validate every external/model/user input on the enforcing side.
10. Never trust client-provided risk, authorization, execution path, or outcome.
11. Do not add custom kernel modules, kernel patches, or an LLM to kernel space.
12. Keep eBPF small, approved, verifier-checked, and capability-aware.

## Implementation discipline

13. Preserve working behavior unless an explicit requirement changes it.
14. Follow the defined repository structure and API/database contracts.
15. Implement requirements completely, including documented edge cases and failure states.
16. Write or update tests for every implemented behavior and link them to stable IDs.
17. Run focused tests, security checks, and relevant validation after changes.
18. Fix failures rather than ignoring, weakening, or masking them.
19. Update documentation when an approved architectural or contract change occurs.
20. Never mark a task complete unless its acceptance criteria and validation are satisfied.

## Required workflow

`READ -> UNDERSTAND -> PLAN -> IMPLEMENT -> TEST -> VALIDATE -> REVIEW -> DOCUMENT`

When uncertain:

`STOP -> IDENTIFY THE AMBIGUITY -> MARK [DECISION REQUIRED]`

## Review checklist

- Requirement IDs are referenced in code/tests/PR description.
- Input, output, permissions, state transitions, retries, and concurrency are explicit.
- Unknown execution state is not reported as success.
- Logs are structured, sanitized, and access controlled.
- No UI-only authorization exists.
- Performance and degraded-mode behavior are measured, not asserted.
