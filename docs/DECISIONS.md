# Architecture Decision Record (ADR)

## ADR-001: Safe planning before execution
- Date: 2026-09-13
- Decision: The system will convert user intent into a typed structured plan before any execution.
- Context: The PRD requires a safe, explainable system that should not execute arbitrary shell commands directly from untrusted user input.
- Options considered:
  - Direct LLM-to-shell execution
  - Planner + executor with typed schema
  - Planner + executor + safety gate
- Chosen approach: Planner + executor + safety gate
- Reason: This is the smallest safe architecture that aligns with the PRD and reduces risk.
- Consequences: Execution becomes more deterministic, user-visible, and auditable.

## ADR-002: Model provider abstraction
- Date: 2026-09-13
- Decision: Core application code must depend on a model-provider interface, not a single runtime.
- Context: The PRD explicitly requires local models, Ollama support, future inference options, and optional hosted providers.
- Options considered:
  - Hardcode one model provider
  - Abstract provider interface with multiple implementations
- Chosen approach: ModelProvider interface with LocalModelProvider, OllamaProvider, and optional HostedProvider
- Reason: Keeps the architecture flexible and matches the product requirement for offline-first operation.
- Consequences: The core runtime remains portable while provider-specific logic remains isolated.

## ADR-003: Resource Governor independence from the LLM
- Date: 2026-09-13
- Decision: Resource limits and telemetry enforcement are managed by a separate subsystem.
- Context: The PRD requires the resource governor to act independently from the planner and to degrade gracefully when kernel telemetry is unavailable.
- Options considered:
  - Let the LLM decide live resource actions
  - Dedicated telemetry + policy subsystem
- Chosen approach: Dedicated resource governor with kernel telemetry + userspace fallback
- Reason: Real-time system protection should not depend on model output.
- Consequences: Safer operation and more deterministic protection under load.

## ADR-004: CLI/API execution precedes GUI automation
- Date: 2026-09-13
- Decision: The application will prefer native APIs and CLI tools before using GUI automation.
- Context: The PRD explicitly prioritizes API, CLI, accessibility tree, then vision-based GUI automation.
- Options considered:
  - GUI-first execution
  - CLI-first with GUI fallback
- Chosen approach: CLI/API first, then accessibility, then vision fallback
- Reason: This improves speed, determinism, and security.
- Consequences: Most tasks remain reliable and low-overhead.

## ADR-005: Debian packaging with model-management separation
- Date: 2026-09-13
- Decision: The package should carry the runtime, launcher, and setup infrastructure, while large models are downloaded separately.
- Context: The PRD requires a reasonably sized .deb and a good first-run setup experience.
- Options considered:
  - Bundle every model into the package
  - Keep the package lean and manage models externally
- Chosen approach: Lean package + external model management
- Reason: This keeps installs small and preserves user experience.
- Consequences: A model manager and first-run setup flow are necessary.

## ADR-006: Offline-first architecture
- Date: 2026-09-13
- Decision: MarrowAI defaults to local and offline operation with optional explicit remote configuration.
- Context: The user requirement is a fully offline system with low latency and no dependence on internet access.
- Options considered:
  - Cloud-first default
  - Local-first default with remote opt-in
- Chosen approach: Local-first default
- Reason: Matches user expectations and security posture.
- Consequences: The project must support a local model provider and local execution path without internet dependency.

## ADR-007: Minimal eBPF and kernel boundary
- Date: 2026-09-13
- Decision: Keep eBPF and kernel involvement minimal and only for justified telemetry or enforcement.
- Context: The PRD explicitly says kernel eBPF logic must stay minimal and verified, with userspace fallback.
- Options considered:
  - Full kernel injection for all monitoring
  - Small, bounded kernel telemetry with userspace fallback
- Chosen approach: Small, bounded kernel telemetry with fallback
- Reason: The project should remain portable and safer across Linux configurations.
- Consequences: Some systems will rely on userspace monitoring when kernel capabilities are unsupported.
