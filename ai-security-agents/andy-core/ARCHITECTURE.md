# Andy Core Architecture

## Command hierarchy

- **Owner:** Muddasir. Owns the infrastructure, credentials, data, and approval policy.
- **Chief orchestrator:** Andy. Decomposes objectives, routes tasks, tracks outcomes, and escalates uncertainty.
- **Specialists:** Narrow workers with explicit capabilities, tools, instructions, and evaluation suites.
- **Reviewers:** Independent agents that challenge evidence and check quality before publication or action.

## MVP flow

1. A task is submitted to the SQLite ledger.
2. Andy matches the task capability to an enabled worker.
3. The worker returns a structured result with evidence and limitations.
4. The ledger records assignment, completion, and failure events.
5. Unmatched tasks remain queued for a future specialist rather than being silently discarded.

## Planned production evolution

- Provider-neutral LLM adapter with model and cost policies
- Tool registry with per-agent allowlists
- Durable queue and worker processes
- Retrieval-backed, versioned specialist knowledge
- Independent verifier and evaluator passes
- Human approval gates for external writes and consequential actions
- Scheduler, health checks, structured logs, metrics, backups, and recovery

## Non-goals

The MVP does not spawn thousands of agents, run continuously, or claim to be sentient. Scale comes later through measured worker pools, quotas, observability, and evaluation.
