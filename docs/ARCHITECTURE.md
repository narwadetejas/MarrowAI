# MarrowAI Architecture

## 1. Architectural principles
- Prefer small, modular responsibilities
- Keep the LLM outside of the privileged execution path
- Prefer typed interfaces over free-form text where practical
- Use providers for model, STT, TTS, tool, and executor integrations
- Default to local, offline operation
- Fail visibly and safely

## 2. High-level system architecture

User
  ↓
Voice / Text Input
  ↓
Input Normalizer
  ↓
Planner
  ↓
Structured Task Plan
  ↓
Risk Classifier
  ↓
Safety Policy
  ↓
Tool Router
  ↓
Executor
  ↓
Linux System
  ↓
Result & Activity Log

## 3. Userspace components
### 3.1 UI
Responsible for presenting the chat, voice controls, and status updates. The UI must make actions understandable to the user.

### 3.2 Voice input
Captures audio input and normalizes it into a request. This component should be modular and not coupled to a single microphone backend.

### 3.3 STT
Speech-to-text provider abstraction. This can use local offline providers or configured cloud providers when explicitly allowed.

### 3.4 LLM planner
Creates structured tasks from natural-language input. It must produce typed data contracts and never directly execute shell commands.

### 3.5 Retrieval and context
Optional retrieval layer for project context, previous sessions, or local memory. This must be explicit and privacy-aware.

### 3.6 Safety layer
Runs risk analysis and policy evaluation before command execution. This component is independent from the planner.

### 3.7 Executor
Takes validated operations and executes them using the right path: native API, CLI, accessibility interface, or GUI automation.

### 3.8 GUI automation
Used only as a fallback after API and CLI execution options are exhausted.

### 3.9 TTS
Converts assistant responses into spoken output with a clear, intelligible English voice profile.

### 3.10 Activity log
Tracks commands, approvals, outcomes, and failures. This is critical for auditability.

### 3.11 Configuration
Stores user configuration, model selection, capability detection results, and setup status.

## 4. Kernel and eBPF boundary
Only the following components genuinely belong in the kernel-adjacent boundary:
- Resource telemetry collection
- Enforcement hooks for cgroups/resource limits
- Minimal eBPF-based monitoring if the environment supports it

The application logic stays in userspace. Normal planning, execution orchestration, model calls, and tool routing remain outside the kernel.

## 5. Process boundaries
- Input handling
- Planning
- Risk assessment
- Tool routing
- Execution
- Monitoring
- Logging

These boundaries should be isolated and explicit. No component should bypass the safety layer.

## 6. Module responsibilities
### core
Application lifecycle, configuration, orchestration

### model
Model provider abstractions and providers such as LocalModelProvider and OllamaProvider

### planning
Prompt parsing, task decomposition, structured plan generation

### safety
Risk classification, policy decision, confirmation logic

### tools
Tool registry, tool schemas, adapters for CLI/API actions

### executors
Native execution, local shell execution, GUI automation execution

### telemetry
System diagnostics, resource measurements, governor rules

### voice
STT/TTS, session audio flow

### storage
Local config storage, secrets handling, activity logs

## 7. Inter-module interfaces
The application should favor typed objects and interfaces such as:

- ModelProvider
- STTProvider
- TTSProvider
- Tool
- Executor
- RiskClassifier
- MemoryStore
- RetrievalProvider
- SystemTelemetryProvider
- GUIExecutor

Messages between planner and executor should use structured data, not raw strings.

## 8. Resource Governor architecture
The Resource Governor is independent from the LLM. It consumes kernel telemetry and enforces resource limits or user-visible warnings. It may also trigger corrective actions without requiring model involvement.

The resource governor should degrade gracefully if eBPF or privileged capabilities are unavailable.

## 9. Configuration architecture
Configuration must include:
- model provider selection
- local model directory
- capability detection state
- approval policy settings
- voice settings
- log retention settings
- permission model

It must not hardcode one provider or model into the core application.

## 10. Storage architecture
Prefer simple local storage and structured files over unnecessary databases.

Planned storage categories:
- config
- model cache
- task logs
- audit records
- transcripts

## 11. Logging architecture
- Structured logs
- Action-level audit trail
- Explicit errors and exit conditions
- No secret leakage
- Clear separation of user-visible status and technical logs

## 12. Error handling architecture
Every subsystem should define failure behavior for:
- missing microphone
- missing model
- missing GPU
- package manager absence
- root permission denial
- eBPF unsupported
- AT-SPI unavailable
- no network
- partial installation

Errors should be logged, surfaced to the user, and mitigated when practical.

## 13. Packaging architecture
The Debian package should contain:
- application runtime
- launcher integration
- configuration directory structure
- model-management utilities
- resource-governor runtime components if required
- clean uninstall hooks

Large model downloads should be managed separately from the main package to keep the .deb lean.

## 14. Observed current state
The repository currently contains:
- a minimal configuration file pointing to an Ollama-compatible endpoint
- no implementation code
- no engineering documentation
- no test suite
- no feature registry

This means the project is in a pre-foundation state. The first engineering work must establish documentation and a safe MVP vertical slice.
