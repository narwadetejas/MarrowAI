# MarrowAI Security

## 1. Threat model
MarrowAI operates on a local Linux workstation and may execute file operations, package installs, CLI tools, and optional GUI automation. The main threats are:
- prompt injection via user input
- unsafe shell execution
- privacy leakage
- model misuse
- privileged command abuse
- unsafe automation actions
- resource exhaustion

## 2. Trust boundaries
- User input boundary
- Planner boundary
- Safety layer boundary
- Executor boundary
- Linux OS boundary
- Model runtime boundary
- GUI automation boundary

## 3. Permission model
- Default to least privilege
- Require explicit approval for privileged operations
- Separate command validation from execution when possible
- Do not assume sudo is available or safe

## 4. sudo/capability model
The application must not rely on unrestricted root execution for ordinary tasks. Commands that require elevated permissions must be treated as high-risk and validated before execution.

## 5. Command validation
- Registered tool allowlists only
- Structured arguments, not raw shell fragments
- Parameter validation before execution
- Explicit timeouts and bounded execution
- Safe working directory restrictions

## 6. Risk classification
Risk levels should include:
- low: safe file reads or local metadata queries
- medium: document edits or local generation tasks
- high: package installation, privileged operations, system changes, network access, GUI automation

## 7. Confirmation policy
The user should be asked to confirm before actions that:
- modify system configuration
- install packages
- affect system resources
- perform destructive file operations
- trigger GUI automation on user-facing apps

## 8. Speaker verification
For voice interactions, the app should treat speaker identity as an optional feature and avoid assuming trust from voice alone. Voice input should be treated as input data and not as an elevated permission.

## 9. Audit logging
The app must record:
- user request
- plan summary
- safety decision
- chosen tool
- result status
- error details
- timestamps

Secrets must never be logged.

## 10. Secret handling
- Store secrets securely
- Avoid echoing secrets in logs
- Mask credentials in user-visible output
- No hardcoded credentials in code

## 11. Model security
- Local models are preferred by default
- Model outputs must be constrained to typed schemas
- The LLM is not a trusted execution authority
- Model provider configuration must be explicit and user-controlled

## 12. Prompt injection considerations
- Treat user input as untrusted
- Constrain actions to tool schema and policy
- Keep tool execution separate from model reasoning
- Avoid exposing privileged system information unnecessarily

## 13. GUI automation security
- Only use GUI automation when API/CLI alternatives are unavailable
- Require explicit consent for interactions with sensitive or user-facing workflows
- Keep actions scoped and bounded

## 14. eBPF safety
- Keep eBPF logic minimal and verified
- Require graceful fallback when unsupported
- Avoid privilege escalation through unvetted kernel hooks

## 15. Kill switch
The application should support a clear operational kill switch to stop or pause actions when safety concerns arise.

## 16. Failure behavior
If a subsystem fails, the application must:
- detect the failure
- log it
- explain the issue to the user
- recover if possible
- stop safely if recovery is not possible
