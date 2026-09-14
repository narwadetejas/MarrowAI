# MarrowAI Testing Strategy

## 1. Testing goals
The project should prove behavior through automated tests wherever practical and should avoid false confidence from mock-only validation.

## 2. Unit testing
- planner schema validation
- risk classification decisions
- tool registry validation
- provider interface contract tests
- config parsing and default setup tests

## 3. Integration testing
- local model provider integration
- tool execution pipeline
- safety gate + tool router integration
- logging and audit trace generation

## 4. End-to-end testing
- full text input to structured plan to safe execution
- local CLI task execution
- user-visible status flow

## 5. Security testing
- command validation rejection tests
- privilege escalation protection tests
- unsafe prompt handling tests
- audit log integrity tests

## 6. Permission testing
- missing sudo / root scenarios
- unprivileged execution attempts
- permission-denied fallback behavior

## 7. Failure testing
- missing model
- missing microphone
- missing GPU
- unsupported eBPF environment
- AT-SPI unavailable
- tool timeout scenarios

## 8. Model-output testing
- schema validation for planner outputs
- risk classification confidence levels
- refusal or revision behavior for unsafe tasks

## 9. GUI automation testing
- accessibility fallback tests
- require explicit confirmation for sensitive actions
- safe fallback to CLI when automation is not available

## 10. Resource Governor testing
- cgroup and resource threshold tests
- userspace fallback behavior
- no-LLM real-time enforcement tests

## 11. Packaging/install testing
- Debian install validation
- clean uninstall validation
- launcher integration tests
- first-run setup flow tests

## 12. First test priorities
1. planner output schema tests
2. risk classifier allow/deny tests
3. safe executor success/failure tests
4. local model provider setup tests
