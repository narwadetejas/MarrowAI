# MarrowAI Product Requirements Document

## 1. Product vision
MarrowAI is an offline-first Linux desktop assistant that understands natural language, plans work, evaluates risk, and safely executes actions on the local system. It is designed to feel like a calm, capable, human-like operating partner while staying deterministic, transparent, and secure.

The product must be fast, local-first, and able to work without internet access. It should help a user complete real tasks such as project setup, file generation, package installation, code scaffolding, research, and local automation while keeping the user in control.

## 2. Problem statement
Developers and power users often need a local assistant that can act across the OS, filesystem, project workspace, package manager, model runtime, and editor tools. Existing AI experiences are often:

- Cloud-dependent and internet-reliant
- Not transparent about what they are doing
- Unsafe to execute arbitrary shell commands
- Slow, noisy, and difficult to trust on local workstations
- Not aligned to Linux desktop requirements

MarrowAI addresses this by enforcing a strict planning and safety pipeline before any tool is executed.

## 3. Target users
- Developers building projects on Ubuntu/Linux
- Power users managing workspace setup, automation, and local tools
- Teams that want a secure local AI assistant without cloud dependence
- Users who want voice-driven interaction that is clear, low-latency, and understandable

## 4. Goals
- Run fully offline where practical
- Keep latency low and UX smooth
- Maintain human-like but trustworthy interaction
- Convert natural-language instructions into structured executable plans
- Ensure the safety layer gates tool execution
- Support local model selection and model management
- Support voice input and spoken output with clear English
- Integrate into the Ubuntu desktop environment cleanly

## 5. Non-goals
- Full autonomous remote control of arbitrary internet services
- Unbounded self-directed command execution without approval gates
- Public cloud-first operation as a default
- Over-engineering into a distributed microservice system
- Shipping large model files in the base Debian package

## 6. Core features
- Natural-language task planning
- Structured task plans with typed data contracts
- Safety and risk assessment before execution
- Local CLI/API execution with validation
- Optional GUI automation as a fallback
- Offline model provider abstraction
- Resource governor for system protection
- Voice input and text-to-speech interaction
- Diagnostic and capability detection command
- Debian packaging with model-management infrastructure

## 7. Feature requirements
### 7.1 Input processing
The system accepts text and voice input and normalizes it into a task request.

### 7.2 Planning
The LLM produces structured plans rather than arbitrary shell commands.

### 7.3 Safety layer
Every plan step must be evaluated by a risk classifier and policy gate before execution.

### 7.4 Execution
Execution occurs via native API, CLI/tool, accessibility layer, and finally GUI automation only when necessary.

### 7.5 Resource governance
The system observes resource usage independently from the LLM and takes corrective action when needed.

### 7.6 Voice experience
The assistant should provide natural, intelligible spoken responses with a clear English voice and concise status updates during long-running work.

## 8. Functional requirements
1. Accept natural language requests.
2. Create a structured plan from the request.
3. Evaluate risk and policy compliance.
4. Route work to the appropriate executor.
5. Execute safe tasks locally.
6. Show user-visible progress updates.
7. Handle failures explicitly with logging and recovery steps.
8. Support offline or local model providers.
9. Support capability detection and setup guidance.
10. Keep the system usable on Ubuntu VMs and developer workstations.

## 9. Non-functional requirements
- Low-latency local operation
- Deterministic execution path
- Clear feedback to the user
- Minimal environmental assumptions
- Maintainable modular architecture
- Graceful degradation when kernel or runtime capabilities are missing
- Secure defaults

## 10. Security requirements
- The LLM must never be treated as a trusted execution authority
- Shell execution must pass through a safety layer
- Commands requiring privilege must be explicitly checked and controlled
- Audit logs must record actions and outcomes
- Secrets must never be exposed in logs or prompts
- GUI automation must be constrained and permission-aware

## 11. Privacy requirements
- Local-first processing is the default
- Remote processing is allowed only if the user explicitly opts in
- User activity logs should be privacy-aware and minimal
- Sensitive configuration should be stored securely and not embedded in prompts

## 12. Performance targets
- Startup time: under 5 seconds for a ready local session on modern laptops
- Planning latency: low enough for interactive tasks
- Voice interaction: responsive enough to feel natural
- Tool execution: fast and transparent
- Resource governor: near real-time enforcement

## 13. Platform requirements
- Linux desktop environment
- Ubuntu-focused first, but capable of generic Debian-compatible behavior
- Support for X11/Wayland
- Ensure AT-SPI availability detection
- Support cgroups, systemd, eBPF where present
- Prefer local model runtimes and local package managers

## 14. Packaging requirements
- Debian package is the primary distribution path
- Base package must remain reasonably sized
- Large models are downloaded separately and placed in a managed model directory
- Package must install required runtime components and services where needed
- The installer must support clean uninstall

## 15. MVP scope
The first usable MarrowAI must prove:

User input -> plan -> risk assessment -> safety check -> CLI/API tool execution -> result

This MVP is intentionally focused on a safe, structured local execution flow. Voice and GUI automation are added after the plan/execution foundation works reliably.

## 16. Future scope
- Voice-first assistance and natural spoken interaction
- Advanced resource control and policy automation
- GUI automation via accessibility and visual fallback
- Multi-tool orchestration and project-aware memory
- More robust package management and desktop integration
- Stronger diagnostics and self-healing setup flows

## 17. Product assumptions
- The user wants a system that feels like a highly capable local operating assistant
- The app should behave like a trusted teammate, but with explicit safety constraints
- The default model stack is local and offline-capable
- The first implementation is CLI-first to validate planning and execution safety
- The user will validate on Ubuntu VM and developer Linux environments
