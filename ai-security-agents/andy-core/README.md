# Andy Core

Andy Core is the executable foundation of the Andy multi-agent research organisation.

## Current capabilities

- Persistent SQLite task ledger and specialist registry
- Central orchestrator that assigns work by declared capability
- Deterministic planning specialist
- Optional Ollama-backed LLM research analyst
- Allowlisted Android Developers and OWASP source retrieval for Android security tasks
- Evidence records with source IDs, URLs, retrieval timestamps, and bounded excerpts
- Evidence-constrained synthesis followed by a separate reviewer pass
- Dedicated Red, Blue, and Purple Team LLM specialists with separate prompts and capabilities
- Persistent, fail-closed authorisation scope registry for future tool adapters
- Auditable task results and execution events
- Unit tests that exercise agents with a fake model, without requiring a downloaded LLM

The general LLM analyst reasons from model knowledge and does not browse. Android security tasks are routed first to a source-backed specialist that retrieves a fixed allowlist of Android Developers and OWASP pages, stores bounded excerpts and retrieval timestamps, and asks the model to cite source IDs. A second model pass reviews the draft against those excerpts. This is an evidence-alignment check, not a human audit or a guarantee of completeness. The source specialist does not access APKs, repositories, devices, or arbitrary URLs.

### Security divisions

When Ollama is enabled, Andy registers three distinct workers:

| Capability | Specialist | Primary responsibility |
|---|---|---|
| `red-team-analysis` | Red Team | Threat modelling, attack-surface review, weakness hypotheses, and safe lab validation plans |
| `blue-team-defense` | Blue Team | Secure architecture, hardening, detection, incident analysis, and remediation |
| `purple-team-validation` | Purple Team | Correlating findings with controls, designing safe validation, and defining retest evidence |

Example task routing:

```bash
andy submit "Review this Android manifest for exported-component risks" \
  --capability red-team-analysis \
  --description "Owned demo app. Manifest excerpt: ..."
andy submit "Design defensive controls for exported Android components" \
  --capability blue-team-defense \
  --description "Review the supplied manifest and recommend mitigations."
andy submit "Map these findings to detection and regression controls" \
  --capability purple-team-validation \
  --description "Finding: ... Existing controls: ... Available test evidence: ..."
andy run
andy tasks
```

These are functional LLM analysis workers, not autonomous penetration-testing or production-defence tools. They have no shell, network, browser, repository, APK, emulator, or device access. They cannot scan, exploit, or modify a target. The scope registry records exact targets, allowed operations, time windows, and approval references; future tool adapters must call its fail-closed authorisation check before any operation. Registering a scope does not itself create or enable a tool. Agent prompts are not a security boundary.

## Requirements

- Python 3.11+
- No third-party Python runtime dependencies
- Ollama only if you enable the local LLM specialists

## Install and initialise

From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
andy init
andy agents
```

## Run the deterministic planner

```bash
andy submit "Prepare a safe research plan for Android exported components" --capability research-planning
andy run
andy tasks
```

## Enable the local LLM specialists

1. Install and start Ollama: https://ollama.com
2. Download a model in Ollama, for example:

```bash
ollama pull qwen3:8b
```

3. Enable the provider in the same terminal where you run Andy:

```bash
export ANDY_LLM_PROVIDER=ollama
export ANDY_OLLAMA_MODEL=qwen3:8b
# Optional when Ollama uses a non-default local endpoint:
# export ANDY_OLLAMA_URL=http://127.0.0.1:11434
```

4. Restart the CLI command and confirm the specialists are registered:

```bash
andy agents
```

5. Submit an LLM analysis task:

```bash
andy submit "Analyse Android exported component security risks" \
  --capability android-security-analysis \
  --description "Explain common manifest mistakes, attack surfaces, and defensive mitigations. Flag version-specific claims for verification."
andy run
andy tasks
```

The LLM specialists use Ollama's local chat API at `/api/chat`. The default URL is `http://127.0.0.1:11434`; override it with `ANDY_OLLAMA_URL`. The default model is `qwen3:8b`; override it with `ANDY_OLLAMA_MODEL`.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `ANDY_HOME` | Local database directory | `.andy` |
| `ANDY_LLM_PROVIDER` | Enable model provider | unset (LLM disabled) |
| `ANDY_OLLAMA_URL` | Ollama local API base URL | `http://127.0.0.1:11434` |
| `ANDY_OLLAMA_MODEL` | Model tag installed in Ollama | `qwen3:8b` |
| `ANDY_OLLAMA_TIMEOUT` | Request timeout in seconds | `600` |
| `ANDY_OLLAMA_THINK` | Enable model thinking (`true`/`false`) | `false` |
| `ANDY_OLLAMA_NUM_CTX` | Context window | `8192` |
| `ANDY_OLLAMA_NUM_PREDICT` | Maximum generated tokens | `1200` |

## Safety and design

Andy is the orchestrator, not an omniscient model. Workers have explicit capabilities. Security specialists are analysis-only. The persistent scope registry is a policy primitive for future tool adapters, not an action system; enforcement must happen in the adapter immediately before the operation. Model output is untrusted and must be verified before consequential use. Human approval remains required for consequential actions.

See [the build roadmap](ROADMAP.md), [architecture](ARCHITECTURE.md), and [safety policy](SAFETY.md).
