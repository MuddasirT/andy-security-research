"""Provider adapters for local language models.

The first adapter talks to Ollama's local HTTP API using only the Python
standard library. It deliberately exposes text generation only: no tools,
shell access, or autonomous external actions.
"""
from __future__ import annotations

import json
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


class ModelError(RuntimeError):
    """Raised when a configured model cannot return a usable response."""


class OllamaChatModel:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float = 120.0,
    ):
        self.model = model or os.getenv("ANDY_OLLAMA_MODEL", "qwen3:8b")
        self.base_url = (
            base_url or os.getenv("ANDY_OLLAMA_URL", "http://127.0.0.1:11434")
        ).rstrip("/")
        self.timeout = timeout

    def chat(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": 0.2},
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
                f"Cannot reach Ollama at {self.base_url}. Start Ollama and verify "
                f"the URL. Details: {exc}"
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ModelError("Ollama returned an invalid JSON response.") from exc

        message = data.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ModelError("Ollama response did not contain message.content.")
        return content.strip()
