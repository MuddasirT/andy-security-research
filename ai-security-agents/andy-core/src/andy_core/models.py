from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class Task:
    title: str
    capability: str
    description: str = ""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "queued"
    assigned_agent: str | None = None
    result: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class AgentSpec:
    agent_id: str
    name: str
    capabilities: tuple[str, ...]
    description: str
    enabled: bool = True


@dataclass(slots=True)
class AgentResult:
    task_id: str
    agent_id: str
    status: str
    summary: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
