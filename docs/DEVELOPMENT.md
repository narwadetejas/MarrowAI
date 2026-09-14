# MarrowAI Development Guide

## 1. Repository structure
- `docs/` - product, architecture, feature, and engineering documentation
- `src/` - application implementation (to be created)
- `tests/` - automated tests (to be created)
- `packaging/` - Debian packaging assets (to be created)

## 2. Development setup
This project is currently in foundation phase. The intended setup is a local Python environment on Ubuntu/Linux, with a local model runtime for offline operation.

Recommended initial environment:
- Ubuntu 22.04+ or 24.04+
- Python 3.11+
- local model runtime such as Ollama
- optional audio tooling
- optional desktop integration packages for GUI automation

## 3. Commands
Initial commands will evolve as the project is implemented. The first commands should include:
- project tests
- planner unit tests
- safety gate tests
- local execution smoke tests

## 4. Testing commands
- `pytest`
- `pytest -q`
- `pytest tests/unit -q`

## 5. Formatting and linting
- `ruff check .`
- `ruff format .`
- `mypy .`

## 6. Building
- use the project build system once implemented
- aim for a lightweight local Python app with packaging support

## 7. Running locally
- use the CLI entrypoint for safe plan-and-execute testing
- start with text input and structured planning

## 8. Debugging
- log all actions and safety decisions
- use a doctor/diagnostic command for capability detection
- validate missing-runtime behavior explicitly

## 9. Adding a feature
1. Check `docs/FEATURES.md`
2. Determine status and dependencies
3. Review the architecture and interfaces
4. Implement the minimal required change
5. Add tests
6. Update `PROGRESS.md`
7. Update documentation if the architecture changes

## 10. Adding a tool
- define a typed tool schema
- register it in the tool registry
- add validation and safety metadata
- add tests for allow/deny behavior

## 11. Adding a model provider
- implement the provider interface
- isolate provider-specific setup and config
- keep the core app independent from the provider implementation

## 12. Adding a GUI executor
- keep it as a fallback only
- prefer native API or CLI actions first
- enforce explicit approval for risky UI actions

## 13. Updating documentation
Any meaningful architectural change must be reflected in:
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/FEATURES.md`
- `docs/PROGRESS.md`

## 14. AI coding workflow
Always:
- read the docs first
- check the feature registry
- implement the smallest vertical slice
- test and verify before claiming completion
- update progress and docs
