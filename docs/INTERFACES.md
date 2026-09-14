# MarrowAI Interfaces

## 1. Top-level flow
User Input
  ↓
Planner
  ↓
Structured Task Plan
  ↓
Safety Layer
  ↓
Tool Router
  ↓
Executor
  ↓
Linux

## 2. Primary typed interfaces

### 2.1 UserInput
- text: str | None
- audio: bytes | None
- source: enum {text, voice}
- metadata: dict[str, str]

### 2.2 TaskPlan
- id: str
- intent: str
- steps: list[PlanStep]
- constraints: list[str]
- risk_level: enum {low, medium, high}

### 2.3 PlanStep
- id: str
- action_type: enum {api, cli, file, gui, question}
- description: str
- tool_name: str | None
- parameters: dict[str, Any]
- approval_required: bool

### 2.4 SafetyDecision
- decision: enum {ALLOW, REVIEW, DENY}
- reason: str
- confidence: float
- requires_confirmation: bool

### 2.5 ToolCall
- tool_name: str
- arguments: dict[str, Any]
- timeout_seconds: int
- resource_profile: str

### 2.6 ExecutionResult
- status: enum {success, failed, blocked, partial}
- output: str
- exit_code: int | None
- logs: list[str]
- warnings: list[str]

## 3. Validation rules
- The planner must not emit raw shell strings for execution.
- The safety layer must validate before execution.
- Tool calls must use typed arguments and a registered tool schema.
- Execution results must be logged and captured in structured output.

## 4. Interfaces between major modules
- UI -> Input Normalizer
- Input Normalizer -> Planner
- Planner -> Safety Layer
- Safety Layer -> Tool Router
- Tool Router -> Executor
- Executor -> Linux runtime and providers

## 5. Provider interfaces
### ModelProvider
- generate_plan(input: UserInput) -> TaskPlan
- explain_result(result: ExecutionResult) -> str

### STTProvider
- transcribe(audio: bytes) -> str

### TTSProvider
- speak(text: str) -> None

### Tool
- name: str
- schema: dict
- execute(args: dict) -> ExecutionResult

### Executor
- execute(tool_call: ToolCall) -> ExecutionResult

### RiskClassifier
- classify(plan: TaskPlan) -> SafetyDecision

## 6. Security constraint
The LLM should generate structured tasks, but it must never be treated as the authority to run arbitrary commands without the validation gate.
