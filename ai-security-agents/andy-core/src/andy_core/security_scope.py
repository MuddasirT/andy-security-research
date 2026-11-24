"""Persistent, fail-closed authorisation scopes for future security tool adapters.

This registry does not execute tools. Every future tool adapter must call
require_authorised() immediately before an operation and must not trust an LLM
or agent-supplied claim that approval exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import sqlite3


class ScopeDenied(PermissionError):
    """Raised when an operation is outside an explicit authorisation scope."""


@dataclass(frozen=True, slots=True)
class AuthorisationScope:
    scope_id: str
    owner: str
    target: str
    allowed_operations: tuple[str, ...]
    starts_at: str
    expires_at: str
    approval_reference: str


class ScopeRegistry:
    def __init__(self, path: Path | None = None):
        if path is None:
            home = Path(os.environ.get("ANDY_HOME", ".andy")).expanduser()
            home.mkdir(parents=True, exist_ok=True)
            path = home / "andy.db"
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS authorisation_scopes (
                    scope_id TEXT PRIMARY KEY,
                    owner TEXT NOT NULL,
                    target TEXT NOT NULL,
                    allowed_operations TEXT NOT NULL,
                    starts_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    approval_reference TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    def _connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def _parse_time(value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Scope timestamps must be ISO-8601.") from exc
        if parsed.tzinfo is None:
            raise ValueError("Scope timestamps must include a timezone.")
        return parsed.astimezone(timezone.utc)

    def register(self, scope: AuthorisationScope) -> None:
        if not all((scope.scope_id.strip(), scope.owner.strip(), scope.target.strip(),
                    scope.approval_reference.strip())):
            raise ValueError("Scope ID, owner, target, and approval reference are required.")
        if not scope.allowed_operations or any(not item.strip() for item in scope.allowed_operations):
            raise ValueError("At least one non-empty allowed operation is required.")
        start = self._parse_time(scope.starts_at)
        expiry = self._parse_time(scope.expires_at)
        if expiry <= start:
            raise ValueError("Scope expiry must be later than its start time.")
        with self._connect() as db:
            db.execute(
                """INSERT INTO authorisation_scopes
                (scope_id,owner,target,allowed_operations,starts_at,expires_at,
                 approval_reference,created_at) VALUES (?,?,?,?,?,?,?,?)""",
                (scope.scope_id, scope.owner, scope.target,
                 json.dumps(sorted(set(scope.allowed_operations))),
                 start.isoformat(), expiry.isoformat(), scope.approval_reference,
                 datetime.now(timezone.utc).isoformat()),
            )

    def list_scopes(self) -> list[AuthorisationScope]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM authorisation_scopes ORDER BY created_at DESC"
            ).fetchall()
        return [
            AuthorisationScope(
                row["scope_id"], row["owner"], row["target"],
                tuple(json.loads(row["allowed_operations"])), row["starts_at"],
                row["expires_at"], row["approval_reference"],
            )
            for row in rows
        ]

    def require_authorised(
        self, scope_id: str, target: str, operation: str,
        now: datetime | None = None,
    ) -> AuthorisationScope:
        with self._connect() as db:
            row = db.execute(
                "SELECT * FROM authorisation_scopes WHERE scope_id=?",
                (scope_id,),
            ).fetchone()
        if row is None:
            raise ScopeDenied("No registered authorisation scope; operation denied.")
        scope = AuthorisationScope(
            row["scope_id"], row["owner"], row["target"],
            tuple(json.loads(row["allowed_operations"])), row["starts_at"],
            row["expires_at"], row["approval_reference"],
        )
        current = (now or datetime.now(timezone.utc))
        if current.tzinfo is None:
            raise ValueError("Current time must be timezone-aware.")
        current = current.astimezone(timezone.utc)
        if current < self._parse_time(scope.starts_at):
            raise ScopeDenied("Authorisation scope is not active yet.")
        if current >= self._parse_time(scope.expires_at):
            raise ScopeDenied("Authorisation scope has expired.")
        if target != scope.target:
            raise ScopeDenied("Target does not exactly match the authorised target.")
        if operation not in scope.allowed_operations:
            raise ScopeDenied("Operation is not listed in the authorised scope.")
        if not scope.approval_reference.strip():
            raise ScopeDenied("Scope has no approval reference; operation denied.")
        return scope
