# Feature Registry

## 1. Feature registry master list

### MA-CORE-001: Natural Language Task Planning
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: Model provider, tool registry, safety layer
- Inputs: user request text or transcript
- Outputs: structured task plan
- Security level: Medium
- Performance requirements: low latency, deterministic schema
- Implementation location: `marrowai/planner.py`, `marrowai/interfaces.py`
- Tests required: unit tests for schema validation and prompt normalization

### MA-CORE-002: Risk Classification and Safety Gate
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: plan schema, tool registry
- Inputs: candidate action and context
- Outputs: ALLOW, REVIEW, DENY decision
- Security level: High
- Performance requirements: near real-time classification
- Implementation location: `marrowai/safety.py`
- Tests required: allow/deny classification tests

### MA-CORE-003: Safe CLI/API Execution
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: tool registry, safety gate, executor
- Inputs: validated action payload
- Outputs: command or API invocation result
- Security level: High
- Performance requirements: stable and bounded execution
- Implementation location: `marrowai/executor.py`, `marrowai/tools.py`
- Tests required: execution success and rejection tests

### MA-CORE-004: Voice Input and Output
- Priority: P1
- Status: IMPLEMENTED
- Dependencies: STT/TTS provider abstraction, UI
- Inputs: microphone audio
- Outputs: transcript and spoken response
- Security level: Medium
- Performance requirements: smooth interactive flow
- Implementation location: `marrowai/voice.py`, `marrowai/voice_engine.py`
- Tests required: provider contract tests and audio pipeline tests

Note: The current version uses a local-first, offline abstraction with deterministic text pass-through suitable for a future spoken assistant surface.

### MA-CORE-011: Interactive Assistant Loop
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: planner, safety gate, executor, config
- Inputs: user text commands
- Outputs: assistant status and action result
- Security level: Medium
- Performance requirements: low-latency conversational interaction
- Implementation location: `marrowai/interactive.py`
- Tests required: session construction and command loop smoke tests

Note: This is the first human-like conversational session layer for MarrowAI and remains intentionally constrained to safe actions.

### MA-CORE-012: Offline Model Manager
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: Ollama-compatible local runtime, model directory
- Inputs: model name and runtime availability
- Outputs: model installation status and local model registry
- Security level: Medium
- Performance requirements: responsive startup and model reuse
- Implementation location: `marrowai/model_manager.py`
- Tests required: runtime-unavailable fallback and model status checks

### MA-CORE-013: Project Scaffolding and Workspace Automation
- Priority: P1
- Status: IMPLEMENTED
- Dependencies: workspace root, project template
- Inputs: project name and desired type
- Outputs: scaffolded local project files
- Security level: Medium
- Performance requirements: fast project set up
- Implementation location: `marrowai/scaffold.py`, `marrowai/workspace.py`
- Tests required: scaffold creation smoke tests

### MA-CORE-014: Offline Voice Engine and Ubuntu Setup
- Priority: P1
- Status: IMPLEMENTED
- Dependencies: Ubuntu runtime, FFmpeg, speech engine, setup script
- Inputs: text or audio payload
- Outputs: spoken status and offline voice readiness
- Security level: Medium
- Performance requirements: fast local startup and speech synthesis
- Implementation location: `marrowai/voice_engine.py`, `marrowai/ubuntu_setup.py`
- Tests required: voice status and setup script generation tests

### MA-CORE-005: Resource Governor
- Priority: P1
- Status: IMPLEMENTED
- Dependencies: telemetry, kernel/proc detection
- Inputs: system telemetry
- Outputs: resource enforcement actions
- Security level: High
- Performance requirements: low-latency detection and response
- Implementation location: `marrowai/governor.py`
- Tests required: telemetry rule tests and fallback behavior tests

### MA-CORE-006: GUI Automation
- Priority: P2
- Status: IMPLEMENTED
- Dependencies: accessibility detection, executor abstraction
- Inputs: UI task request and app metadata
- Outputs: GUI actions
- Security level: High
- Performance requirements: reliable fallback behavior
- Implementation location: `marrowai/gui_automation.py`, `marrowai/tools.py`
- Tests required: automation decision tests and permission tests

### MA-CORE-007: Capability Detection and Diagnostics
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: OS runtime detection
- Inputs: system environment
- Outputs: support matrix and setup advice
- Security level: Medium
- Performance requirements: fast diagnostic run
- Implementation location: `marrowai/diagnostics.py`, `marrowai/doctor.py`
- Tests required: detection tests for Linux environment

Note: The implementation currently checks OS, Python, CPU, Ollama, Git, FFmpeg, PulseAudio, and Wayland availability.

### MA-CORE-008: Model Provider Abstraction
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: runtime capability detection
- Inputs: model selection and config
- Outputs: model interface instance
- Security level: Medium
- Performance requirements: fast provider startup and reuse
- Implementation location: `marrowai/model.py`
- Tests required: provider selection and failure-mode tests

### MA-CORE-009: Activity Logging and Audit Trail
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: executor, config
- Inputs: actions and outcomes
- Outputs: structured audit log
- Security level: High
- Performance requirements: bounded overhead
- Implementation location: `marrowai/audit.py`
- Tests required: log integrity and redaction tests

### MA-CORE-010: Debian Packaging and Desktop Integration
- Priority: P1
- Status: IMPLEMENTED
- Dependencies: app runtime, launcher integration, service setup
- Inputs: packaging build inputs
- Outputs: installable Debian package
- Security level: Medium
- Performance requirements: standard installation time
- Implementation location: `build_deb.sh`
- Tests required: install/uninstall and launcher tests

### MA-CORE-015: Virtual Machine Orchestration (Ubuntu & Arch Linux)
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: Multipass, QEMU/KVM, VirtualBox, shell runner
- Inputs: target OS (`ubuntu`, `arch`), VM configuration
- Outputs: hypervisor detection, VM creation, launch script configuration
- Security level: High
- Performance requirements: reliable zero-error pre-checks
- Implementation location: `marrowai/vm_manager.py`, `marrowai/tools.py`
- Tests required: hypervisor detection and creation tests

### MA-CORE-016: Indian English Voice Profiles & Pre-Execution Narration
- Priority: P0
- Status: IMPLEMENTED
- Dependencies: `espeak-ng`, `spd-say`, PowerShell SAPI fallback
- Inputs: spoken narration request, voice profile selection (`indian_female`, `indian_male`)
- Outputs: synthesized audio with calibrated speed/pitch, pre-execution action announcements
- Security level: Medium
- Performance requirements: immediate sub-second spoken feedback
- Implementation location: `marrowai/voice_engine.py`, `marrowai/assistant.py`, `marrowai/interactive.py`
- Tests required: voice profile configuration, switching, and narration callback tests

## 2. Current implementation status
The core foundation and operational subsystems are implemented and verified. MarrowAI supports typed task planning, risk classification and policy gating, resource governance, allowlisted tool execution, structured audit logging, local model management, Indian English voice synthesis (female and male), Arch Linux & Ubuntu VM provisioning, project scaffolding, diagnostics, and Debian package distribution.

