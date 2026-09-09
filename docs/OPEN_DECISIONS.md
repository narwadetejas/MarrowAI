# MarrowAI Open Decisions

Only decisions not resolved by the supplied PRD are listed here. Resolve each before dependent implementation begins and record the decision date/owner.

- DEC-001: What is the project name displayed in product/UI metadata? The source document uses MarrowAI; the prompt placeholder says `[PROJECT NAME]`.
- DEC-002: Which local LLM, hosted provider, or selectable provider policy is supported for the MVP?
- DEC-003: Which vector database and embedding/intent encoder are approved?
- DEC-004: Which GUI shell is selected: Electron, PyQt, or another approved option?
- DEC-005: Which language owns the Resource Governor daemon: C or Rust? Which eBPF toolchain and kernel versions are supported?
- DEC-006: What exact structured task-plan JSON schema and versioning policy are required?
- DEC-007: What concrete command taxonomy and initial supported command/API allowlist define MVP scope?
- DEC-008: What confirmation mechanism is allowed when voice is unavailable: typed confirmation, UI control, or refusal?
- DEC-009: What exact speaker-verification model, enrollment flow, threshold, and retry policy are used?
- DEC-010: What audit-log retention duration, storage format, encryption mechanism, and deletion behavior apply?
- DEC-011: Does an audit/logging failure block execution or permit execution with a visible degraded state?
- DEC-012: What authentication model applies to local operators and administrators, if more than the OS account is needed?
- DEC-013: What authorization roles and exact scoped sudoers/capability rules are shipped?
- DEC-014: Which Ubuntu releases, desktop environments, display servers, and minimum kernel versions are supported? The product target is Ubuntu desktop, not all Linux distributions.
- DEC-015: What packaging and deployment format is required: source, package, container, VM image, or service units?
- DEC-016: What vision model and input-simulation mechanism are approved for GUI fallback?
- DEC-017: What concurrency policy applies to simultaneous requests and resource-governor interventions?
- DEC-018: What data may be sent to a hosted LLM, and what provider retention/consent wording is required?
- DEC-019: What measurable risk-classifier dataset, thresholds, and model are accepted for release?
- DEC-020: What exact manual kill-switch interface and cancellation guarantees are required?
- DEC-021: What exactly is “Astra”: model name, model file, local runtime, license, hardware requirements, and supported context size? Until answered, implement only the offline model adapter interface and a deterministic test stub, not a guessed Astra integration.
- DEC-022: Which SQLite driver/migration approach and database location are approved? The database family is fixed to SQLite and the artifact must be a portable `.db` file.
- DEC-023: Which Ubuntu startup mechanism is shipped: systemd user service only, or systemd plus XDG autostart fallback? Define enable/disable behavior and startup failure reporting.
- DEC-024: What exact Ubuntu user display-name source is used for the greeting, and what is the configured local TTS voice/language?

## Conflicts or qualifications in the source

- The source calls the Resource Governor both “small in-kernel model via eBPF” and a split where heavier classification is in user space. The implementation must keep only verifier- and latency-appropriate small logic in eBPF; model placement and exact model remain DEC-005/DEC-019.
- The source names 2026 industry analyses as a literature category but provides no complete bibliographic sources. The evidence should not be treated as a reproducible dependency until references are supplied.
- The source describes “one brief confirmation” for Moderate/Destructive actions but does not define typed confirmation behavior when voice is unavailable. See DEC-008.
- The source lists “hosted API (Claude, GPT)” and local models without selecting one. The provider contract and privacy behavior are unresolved.
- The new project direction requires offline operation. Hosted providers are therefore excluded from normal operation; any optional remote provider would require a later explicit decision and consent flow.
- “Astra” is ambiguous and cannot be selected safely without an exact model/runtime reference.
