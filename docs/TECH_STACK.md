# MarrowAI Technology Stack

The application target is Ubuntu desktop. The durable database choice is fixed to SQLite; other versions and final selections marked below require approval.

| Area | Technology/candidate | Purpose | Version | Decision |
|---|---|---|---|---|
| Wake word/VAD | openWakeWord or Porcupine; Silero VAD | Voice activation and speech boundary detection | [DECISION REQUIRED] | Select one wake-word path and license |
| STT | Whisper or whisper.cpp | Speech-to-text | [DECISION REQUIRED] | Local-first candidate |
| Speaker verification | Local speaker-embedding model | Gate voice-sensitive actions | [DECISION REQUIRED] | Define threshold/enrollment |
| Planning | Offline model through a replaceable local runtime adapter; Astra only if its runtime/model is identified and approved | Structured task planning | [DECISION REQUIRED] | No hosted model in normal operation |
| Retrieval | Vector database + BERT-based semantic/intent encoders | Similar-request retrieval | [DECISION REQUIRED] | Rebuildable derived index |
| Risk classifier | scikit-learn logistic regression or fine-tuned BERT/PyTorch | Risk tier prediction | [DECISION REQUIRED] | Deterministic policy remains mandatory |
| CLI/API | Python subprocess and explicit API adapters | Preferred execution | [DECISION REQUIRED] | No shell-string interpolation |
| GUI automation | pyatspi/dogtail; UI-TARS; xdotool/ydotool candidates | Accessibility-first GUI fallback | [DECISION REQUIRED] | Select supported desktop/display stack |
| Governor daemon | C or Rust; libbpf/bcc/BPF CO-RE | Load/manage eBPF and policy | [DECISION REQUIRED] | Choose one language/toolchain |
| Kernel hooks | Restricted C eBPF bytecode | Verified fast telemetry/enforcement | Kernel-dependent | No custom module |
| TTS | Piper | Local speech output | [DECISION REQUIRED] | Local-first candidate |
| GUI shell | Electron or PyQt | Chat/voice/activity interface | [DECISION REQUIRED] | Select one |
| Database | SQLite | Durable plans/actions/audit in a portable `.db` file | [DECISION REQUIRED] | Database family is fixed; version/driver/migration tool remain to be selected |
| Startup | systemd user service / XDG autostart fallback | Start with Ubuntu graphical session | Ubuntu-dependent | Must not run as root by default |

## Required dependencies

Only dependencies needed by the selected rows above may be added. Exact package names, versions, licenses, and platform requirements must be recorded in the implementation repository after the applicable decisions are resolved. SQLite must remain readable through a documented migration path on every supported Ubuntu release.

## Development dependencies

A test runner, type/lint tooling, API contract validation, eBPF verifier/test tooling, and browser/GUI test tooling may be selected when implementation language and shell are resolved. [DECISION REQUIRED]

## Prohibited without approval

- Custom kernel modules or kernel patches.
- An LLM in kernel space.
- Blanket root execution.
- A second ORM, vector database, GUI framework, or model provider introduced for convenience.
- Remote telemetry, cloud audio storage, or hosted model calls without an explicit privacy decision.
- A remote-only model or an offline model/runtime that has not passed the local adapter and privacy tests.
- Shell execution that concatenates untrusted input.
