"""Provider adapters for local language models.

The first adapter talks to Ollama's local HTTP API using only the Python
standard library. It deliberately exposes text generation only: no tools,
shell access, or autonomous external actions.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ModelError(RuntimeError):
    """Raised when a configured model cannot return a usable response."""


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ModelError(f"{name} must be an integer; received {raw!r}.") from exc
    if value < minimum:
        raise ModelError(f"{name} must be at least {minimum}.")
    return value


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ModelError(f"{name} must be true or false; received {raw!r}.")


class OllamaChatModel:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ):
        self.model = model or os.getenv("ANDY_OLLAMA_MODEL", "qwen3:8b")
        self.base_url = (
            base_url or os.getenv("ANDY_OLLAMA_URL", "http://127.0.0.1:11434")
        ).rstrip("/")
        if timeout is None:
            try:
                timeout = float(os.getenv("ANDY_OLLAMA_TIMEOUT", "600"))
            except ValueError as exc:
                raise ModelError("ANDY_OLLAMA_TIMEOUT must be a number of seconds.") from exc
        if timeout <= 0:
            raise ModelError("Ollama timeout must be greater than zero.")
        self.timeout = timeout
        self.think = _env_bool("ANDY_OLLAMA_THINK", False)
        self.num_ctx = _env_int("ANDY_OLLAMA_NUM_CTX", 8192)
        self.num_predict = _env_int("ANDY_OLLAMA_NUM_PREDICT", 1200)

    def chat(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "think": self.think,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": 0.2,
                "num_ctx": self.num_ctx,
                "num_predict": self.num_predict,
            },
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            raise ModelError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ModelError(
                f"Ollama request to {self.base_url} failed or timed out after "
                f"{self.timeout:g} seconds. Check that Ollama is running and the "
                f"model is available. Details: {exc}"
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ModelError("Ollama returned an invalid JSON response.") from exc

        message = data.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            thinking = message.get("thinking")
            if thinking:
                raise ModelError(
                    "Ollama returned thinking but no final message content. "
                    "For Qwen3, set ANDY_OLLAMA_THINK=false and retry."
                )
            raise ModelError("Ollama response did not contain message.content.")
        return content.strip()
