# MarrowAI Implementation Plan

## 1. Implementation principle
Build the smallest working vertical slice and validate it before moving to the next layer. The core path is:

Text input -> structured plan -> risk assessment -> safety gate -> tool execution -> result

## 2. Milestones
### Milestone 1: Project foundation
- Establish engineering docs
- Create feature registry
- Create architecture and decision records
- Define interfaces and safety contracts
- Set up Python project structure and test harness

Acceptance criteria:
- Required docs exist
- Feature registry is authoritative
- Initial tests run
- The project can be understood by a new AI agent

### Milestone 2: MVP safe planning and execution
- Create planning schema
- Implement risk classification
- Build a safe local executor
- Add logging and structured results
- Add CLI entrypoint

Acceptance criteria:
- User can provide a text prompt
- The system produces a plan
- The system evaluates risk
- Only safe actions execute
- Execution result is returned and logged

### Milestone 3: Voice and feedback
- Add STT/TTS provider abstraction
- Add voice command path
- Add user-visible system status updates
- Support clearer spoken interactions

Acceptance criteria:
- Voice input can start a task
- Spoken feedback is intelligible
- Voice and text flows share the same planning pipeline

### Milestone 4: Resource Governor
- Add telemetry detection
- Add resource thresholds
- Add safe degrading behavior when eBPF is unavailable

Acceptance criteria:
- System can detect resource pressure
- Governor enforces limits without LLM dependency

### Milestone 5: GUI automation and desktop integration
- Add accessibility fallback and GUI executor
- Integrate with Linux desktop environment
- Validate permission and fallback behavior

Acceptance criteria:
- GUI automation is used only when necessary
- Risk controls remain enforced

### Milestone 6: Packaging and deployment
- Prepare Debian packaging
- Add installer/uninstall flow
- Add model management support
- Add doctor/diagnostics command

Acceptance criteria:
- Package installs cleanly
- Model management is separate from the app package

## 3. Phase roadmap
### Phase 0: foundation
- docs
- architecture
- project config
- tests

### Phase 1: text to structured plan to execution
- planner
- risk classifier
- safe CLI executor

### Phase 2: safety and confirmation
- approval policy
- audit logging
- command validation

### Phase 3: voice
- STT/TTS and user interaction

### Phase 4: resource governor
- telemetry + enforcement

### Phase 5: GUI automation
- accessibility + desktop actions

### Phase 6: packaging and deployment
- Debian package and installation flow

## 4. Dependencies
- Python runtime
- Local model provider (Ollama first candidate)
- Ubuntu/Linux developer environment
- AT-SPI and accessibility stack for GUI automation
- eBPF support opportunistically

## 5. Deliverables
- working CLI MVP
- risk model and safety contract
- test suite
- engineering docs
- package and installation plan

## 6. First implementation task
Implement the safe planning and execution vertical slice with typed plan objects, risk analysis, and a local execution path. This is the highest-priority unblocked task because it proves the system can reason about user intent and safely carry out local actions.
