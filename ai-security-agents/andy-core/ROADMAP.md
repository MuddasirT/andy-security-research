# Andy Core Roadmap

## Milestone 1: Executable orchestration foundation

- [x] SQLite task ledger and event log
- [x] Specialist registry and capability-based routing
- [x] Deterministic planning worker
- [x] CLI for task submission and execution
- [x] Unit tests for routing and persistence
- [x] Fix worker identity lookup in the orchestrator

## Milestone 2: Local model reasoning

- [x] Provider boundary for local model chat
- [x] Ollama adapter using Python standard library
- [x] LLM research analyst with bounded instructions
- [x] Explicit limitation reporting and no-tool safety boundary
- [x] Mock-based unit test that does not require Ollama
- [ ] Verify test suite on the user's Mac
- [ ] Verify a real Ollama model response on the user's Mac

## Milestone 3: Evidence-backed research

- [ ] Add approved web-search connector behind a narrow interface
- [ ] Store source URLs, retrieval timestamps, and quoted evidence
- [ ] Require evidence for current/version-sensitive claims
- [ ] Add independent reviewer agent and disagreement handling

## Milestone 4: Specialist organisation

- [ ] Android/Kotlin specialist
- [ ] AI/ML specialist
- [ ] Defensive security specialist
- [ ] Research librarian and knowledge curator
- [ ] Specialist-specific evaluation suites and versioned knowledge

## Milestone 5: Reliable operations

- [ ] Background worker service and scheduler
- [ ] Retry policy, timeouts, cancellation, and concurrency limits
- [ ] Monitoring, health checks, backups, and recovery
- [ ] Human approval gates for consequential actions

Items are marked complete when implemented and verified, not merely planned.
