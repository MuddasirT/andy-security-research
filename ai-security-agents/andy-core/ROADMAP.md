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

- [x] Add a narrow source-fetching interface with a fixed Android Developers/OWASP allowlist
- [x] Store source URLs, retrieval timestamps, publisher/title, and bounded text excerpts in task evidence
- [x] Require source IDs for material factual claims in Android source-backed reports
- [x] Add a second model-pass reviewer that checks claims against supplied evidence
- [ ] Add a broader approved web-search connector with query-time source discovery
- [ ] Add citation-integrity checks and structured disagreement handling
- [ ] Run and verify the complete test suite on the user's Mac and CI

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
