# Andy Empire Build Roadmap

## Phase 0: Foundation (this commit series)
- [x] Confirm the GitHub project and write access
- [x] Define command hierarchy and safety boundaries
- [x] Add local persistent task ledger and capability-based routing
- [x] Add a planning specialist and CLI
- [ ] Run local tests on the owner's machine

## Phase 1: Working local command centre
- Add automated tests and structured event inspection
- Add configuration, health checks, backups, and database migrations
- Add a provider-neutral LLM interface (local model first, hosted provider optional)
- Add explicit tool permissions and per-task budgets

## Phase 2: Real specialist workforce
- Research analyst, Android/Kotlin engineer, AI/ML analyst, cybersecurity analyst, and verifier
- Specialist playbooks, curated knowledge, benchmark tasks, and versioning
- Reviewer workflow: draft -> critique -> revision -> accepted/rejected

## Phase 3: Persistent operations
- Separate worker processes and durable queue
- Scheduled research jobs and notification digests
- Monitoring, retry policy, failure quarantine, and manual pause/resume
- Encrypted secrets management and tested backups

## Phase 4: Expand carefully
- Add specialists only when a repeatable task and evaluation set justify them
- Scale concurrency based on hardware, latency, and budget
- Optional cloud workers while keeping the home-hosted control plane portable

## Release gate

A phase is complete only when its tests pass, documentation is updated, permissions are reviewed, and the result can be reproduced. A checked box means code or documentation exists, not that a service is running in production.
