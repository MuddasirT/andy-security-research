# Andy Core

Andy Core is the first executable foundation of the Andy multi-agent research organisation.

## Current scope

- A persistent SQLite task ledger
- A specialist-agent registry
- A central orchestrator that assigns work by capability
- A safe, deterministic demonstration agent
- A command-line interface for registering agents, submitting tasks, and running the queue

This is an intentionally small, inspectable MVP. It does **not** claim that background agents, autonomous web research, or an always-on service are deployed. Those require a configured model provider, tools, a host process, and operational monitoring.

## Requirements

- Python 3.11+
- No third-party runtime dependencies

## Run locally

From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
andy init
andy agents
andy submit "Prepare a safe research plan for Android exported components" --capability research-planning
andy run
andy tasks
```

The database defaults to `.andy/andy.db`. Set `ANDY_HOME` to change the data directory.

## Design rule

Andy is the orchestrator, not an omniscient model. Specialist agents are explicit workers with declared capabilities. Model-backed reasoning and external tools will be added behind narrow interfaces, with permission checks and evidence requirements.

## Next milestones

See [the build roadmap](ROADMAP.md), [architecture](ARCHITECTURE.md), and [safety policy](SAFETY.md).
