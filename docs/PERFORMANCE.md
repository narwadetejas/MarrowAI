# MarrowAI Performance

## 1. Measurement principle
Performance must be measured, not guessed. The initial plan is to define a baseline for the measurable subsystems and then tune only when needed.

## 2. Target metrics
- Startup time: < 5s on modern laptop for a ready local session
- STT latency: low enough for near real-time voice interactions
- Planning latency: interactive but bounded
- Tool execution latency: targeted to operation speed without unbounded waits
- GUI automation latency: acceptable only as a fallback
- Resource Governor response: near real-time under load
- Memory consumption: reasonable for desktop development use
- CPU consumption: avoid unnecessary wakeups and loops
- GPU consumption: local inference should be configurable
- Model loading time: minimize cold starts through caching and reuse
- Idle resource usage: keep the app lightweight while waiting

## 3. Baseline measurement checklist
- cold start
- first plan generation
- tool execution roundtrip
- voice input to transcript
- speech output latency
- resource governor response under load
- memory after idle and after task execution

## 4. Performance goals by subsystem
### Input and planning
- fast text normalization
- structured plan generation with compact payloads
- minimal repeated model startup

### Execution
- prefer local native APIs and CLI tools
- avoid unnecessary subprocesses
- reuse connections and model runtime where possible

### Voice
- low latency audio pipeline
- clear output without excessive processing overhead

### Resource enforcement
- lightweight monitoring from telemetry sources
- graceful fallback when eBPF is not available

## 5. Current state
No benchmark data exists yet because the project is still at implementation foundation stage.
