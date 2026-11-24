# Operational Status

Last updated: 2026-11-24

| Component | State |
|---|---|
| Repository access | Verified |
| SQLite task ledger | Implemented; user confirmed local task execution |
| Capability-based orchestrator | Implemented; worker identity bug fixed |
| Deterministic planning specialist | Implemented; local execution confirmed by user |
| Ollama chat adapter | Committed; local connection not yet verified |
| LLM research analyst | Implemented; no external tools or action permissions |
| Agent factory | Ollama specialist is opt-in through environment configuration |
| Unit tests | Committed; latest local execution not yet confirmed |
| GitHub Actions CI | Main-branch quality-gate v1 CI passed; orchestrator integration CI pending |
| Web research and evidence collection | Not connected |
| Background workers / scheduler | Not deployed |
| Persistent specialist knowledge bases | Not deployed |\n| Universal security report contract v1 | Implemented and merged to main |\n| Deterministic quality validator | Implemented and merged to main |\n| Orchestrator quality-gate integration | Implemented on feature branch; awaiting CI and merge |\n| Security tool gateway | Not implemented |\n| Red/Blue/Purple execution tools | Not available; specialists remain analysis-only |

The first local task completed successfully on the user's Mac. The LLM integration is committed but still requires a local Ollama installation, model download, test-suite run, and real inference test.

Do not describe the organisation as always-on or its agents as independently online until deployment and health checks verify that state.


## Security lab boundary

The current six specialist identities do not have shell, browser, network, repository,
APK, device, scanner, or exploitation tools. The SQLite authorisation registry is
not yet connected to a policy-enforcing tool gateway. No active testing or defensive
system changes are performed by Andy at this stage.

The intended agentic security lab workflow and staged build plan are documented in
[AGENTIC_SECURITY_LAB_PLAN.md](AGENTIC_SECURITY_LAB_PLAN.md).
