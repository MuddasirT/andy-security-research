# Andy Core

Andy Core is the executable foundation of the Andy multi-agent research organisation.

## Current capabilities

- Persistent SQLite task ledger and specialist registry
- Central orchestrator that assigns work by declared capability
- Deterministic planning specialist
- Optional Ollama-backed LLM research analyst
- Auditable task results and execution events
- Unit tests that exercise the LLM agent with a fake model, without requiring a downloaded LLM

The LLM analyst reasons from its model's internal knowledge. It does **not** browse the web, access files or repositories, execute shell commands, or take external actions. It must flag current claims for independent verification.

## Requirements

- Python 3.11+
- No third-party Python runtime dependencies
- Ollama only if you enable the local LLM specialist

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

## Enable the local LLM specialist

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

4. Restart the CLI command and confirm the specialist is registered:

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

The LLM specialist uses Ollama's local chat API at `/api/chat`. The default URL is `http://127.0.0.1:11434`; override it with `ANDY_OLLAMA_URL`. The default model is `qwen3:8b`; override it with `ANDY_OLLAMA_MODEL`.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `ANDY_HOME` | Local database directory | `.andy` |
| `ANDY_LLM_PROVIDER` | Enable model provider | unset (LLM disabled) |
| `ANDY_OLLAMA_URL` | Ollama local API base URL | `http://127.0.0.1:11434` |
| `ANDY_OLLAMA_MODEL` | Model tag installed in Ollama | `qwen3:8b` |

## Safety and design

Andy is the orchestrator, not an omniscient model. Workers have explicit capabilities. The first LLM worker has no tools or external-action permissions. Model output is untrusted and must be verified before consequential use. Human approval remains required for future consequential actions.

See [the build roadmap](ROADMAP.md), [architecture](ARCHITECTURE.md), and [safety policy](SAFETY.md).
