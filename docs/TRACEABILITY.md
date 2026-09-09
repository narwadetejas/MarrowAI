# MarrowAI Requirement Traceability

This matrix connects the stable requirements to product features, architecture, implementation tasks, code areas, and tests. Code-area paths are planned boundaries because implementation has not started.

| Requirements | Feature | Architecture | Task | Planned code area | Tests |
|---|---|---|---|---|---|
| REQ-001-002 | F-001 | Input layer | TASK-003 | `src/input/` | TEST-001, TEST-015, TEST-017 |
| REQ-003-004 | F-002 | Planner/retrieval | TASK-004 | `src/planner/`, `src/retrieval/` | TEST-002 |
| REQ-005-008 | F-003 | Safety/policy | TASK-005 | `src/safety/` | TEST-003-005 |
| REQ-009-010 | F-004 | Executor router | TASK-006, TASK-007 | `src/execution/` | TEST-006-007 |
| REQ-011-012 | F-001/F-005 | Context/feedback | TASK-003, TASK-004, TASK-007 | `src/context/`, `src/feedback/` | TEST-008-009 |
| REQ-013 | F-004/F-007 | Cancellation | TASK-006, TASK-007 | `src/control/` | TEST-009 |
| REQ-014-019 | F-006 | Governor/eBPF | TASK-008 | `src/governor/`, `ebpf/` | TEST-010-011, TEST-020 |
| REQ-020-022 | F-004/F-007 | Privilege/audit | TASK-006, TASK-009 | `src/security/`, `src/audit/` | TEST-012, TEST-014 |
| REQ-023-027 | F-007 | Privacy/deployment | TASK-002, TASK-009 | `src/privacy/`, deployment config | TEST-013-016 |
| REQ-028 | All | Validation boundary | TASK-003-009 | all input boundaries | TEST-003, TEST-012 |
| REQ-029-032 | Quality targets | Observability | TASK-003, TASK-007, TASK-010 | `tests/performance/` | TEST-017-018 |
| REQ-033-036 | Evaluation | Evaluation harness | TASK-010 | `evaluation/` | TEST-019-020 |

## Coverage review

- No requirement is intentionally without a task or test in the baseline matrix.
- Code areas are not implementation commitments until stack and repository structure decisions are approved.
- DEC-001 through DEC-020 can block corresponding tasks; see `OPEN_DECISIONS.md`.
- Acceptance criteria are defined in `PRD.md`; test IDs and negative cases are defined in `TEST_PLAN.md`.
