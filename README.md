# MarrowAI

The implementation blueprint is in [`docs/PROJECT_SPEC.md`](docs/PROJECT_SPEC.md).

## Documentation

- [`PROJECT_SPEC.md`](docs/PROJECT_SPEC.md): source-of-truth requirements, scope, constraints, and traceability summary
- [`PRD.md`](docs/PRD.md): feature behavior and acceptance criteria
- [`ARCHITECTURE.md`](docs/ARCHITECTURE.md): system boundaries and data flow
- [`TECH_STACK.md`](docs/TECH_STACK.md): approved/candidate technologies
- [`DATABASE.md`](docs/DATABASE.md): logical persistence model
- [`API_SPEC.md`](docs/API_SPEC.md): API and internal interface contracts
- [`UI_SPEC.md`](docs/UI_SPEC.md): screen behavior and states
- [`SECURITY.md`](docs/SECURITY.md): security and privacy controls
- [`TEST_PLAN.md`](docs/TEST_PLAN.md): requirement-linked test strategy
- [`TASKS.md`](docs/TASKS.md): dependency-ordered implementation plan
- [`AI_RULES.md`](docs/AI_RULES.md): coding-agent constraints and workflow
- [`TRACEABILITY.md`](docs/TRACEABILITY.md): requirement-to-test/code-area matrix
- [`OPEN_DECISIONS.md`](docs/OPEN_DECISIONS.md): unresolved decisions only

## Bootstrap MVP

The current implementation is an offline Ubuntu bootstrap with SQLite persistence and a safe deterministic planner. From the repository root:

```bash
python3 -m app.main --welcome
python3 -m app.main --text "show memory pressure"
```

The user-session service template is at [`deploy/systemd/marrowai.service`](deploy/systemd/marrowai.service). Full voice recognition, the production offline model, command execution, and eBPF governance remain staged tasks; the exact offline model called “Astra” must be resolved before integration.

To enable startup for the current Ubuntu user:

```bash
sh deploy/install-user-service.sh
```