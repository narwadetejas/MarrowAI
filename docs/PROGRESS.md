# MarrowAI Progress

## 1. Current status
- Repository audit complete
- Product requirements are documented under `docs/`
- The project has a working foundation with safe local-first execution, offline model awareness, and conversation support
- Ubuntu setup support and voice-runtime detection are now implemented

## 2. Completed
- Repository audit of the workspace
- PRD and architecture documentation created
- Feature registry and implementation plan created
- Safe planner and safety gate implemented
- Local CLI executor implemented
- Model provider abstraction implemented with fallback
- Offline voice abstraction implemented
- Offline voice engine and Ubuntu setup flow implemented
- Diagnostic/doctor command implemented
- Interactive assistant loop implemented
- Memory store implemented for recent context
- Project scaffolding and workspace automation implemented

## 3. Currently working on
- Richer spoken assistant narration and human-like responses
- More advanced project-aware context and onboarding flows
- Desktop packaging and installer polish

## 4. Next
- Add real OS-level voice capture and speech synthesis integration for Ubuntu
- Add file-generation and code-generation tasks for backend apps
- Add packaging and install flow improvements for end-user distribution

## 5. Blocked
- Full real-time OS audio capture and GUI automation remain intentionally deferred behind the safety-first architecture
- Real model performance depends on the target Ubuntu machine and installed runtime

## 6. Known bugs
- None in the current verified test suite

## 7. Technical debt
- Voice capture is still a lightweight local abstraction, not full microphone integration
- The app currently supports a small safe MVP command set
- Project memory is intentionally minimal and local

## 8. Architecture changes
- Added a memory subsystem to support context retention across chat steps
- Added a setup subsystem to support Ubuntu install preparation
- Kept the architecture safety-first and model-provider-abstracted

## 9. Tests
- Verified test suite passes for planner, safety, execution, model, voice, diagnostics, interactive loop, memory, scaffold, and Ubuntu setup flows

## 10. Performance
- Baseline behavior is stable for the current MVP and local-first workflow
- No heavy model workload is required for the default path
