"""Fail-closed policy gateway for future, explicitly registered security tools.

No tools are registered by default. Agents must never receive raw adapter
references or arbitrary shell/network access. The orchestrator should expose
only a narrow callable bound to the agent identity.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Callable, Mapping

from .security_scope import ScopeDenied, ScopeRegistry


class ToolAccessDenied(PermissionError):
    """Raised when an agent is not permitted to invoke a registered tool."""


class HumanApprovalRequired(PermissionError):
    """Raised when an active or state-changing operation lacks owner approval."""


@dataclass(frozen=True, slots=True)
class ToolSpec:
    tool_id: str
    allowed_agents: tuple[str, ...]
    allowed_operations: tuple[str, ...]
    risk_level: str = "read_only"

    def __post_init__(self):
        if not self.tool_id.strip():
            raise ValueError("tool_id is required.")
        if not self.allowed_agents or any(not item.strip() for item in self.allowed_agents):
            raise ValueError("At least one allowed agent is required.")
        if not self.allowed_operations or any(not item.strip() for item in self.allowed_operations):
            raise ValueError("At least one allowed operation is required.")
        if self.risk_level not in {"read_only", "active", "state_changing"}:
            raise ValueError("risk_level must be read_only, active, or state_changing.")


ApprovalChecker = Callable[[str, str, str, str, str, str], bool]
AuditWriter = Callable[[str, str], None]
ToolAdapter = Callable[[Mapping[str, Any]], Any]


class ToolGateway:
    """Central policy enforcement point. Denies by default.

    Approval checker arguments:
      approval_id, plan_digest, scope_id, tool_id, target, operation

    The checker must verify an explicit owner action bound to all six values.
    A text approval reference stored in a scope record is not sufficient.
    """

    def __init__(
        self,
        scope_registry: ScopeRegistry,
        audit_writer: AuditWriter,
        approval_checker: ApprovalChecker | None = None,
    ):
        if audit_writer is None:
            raise ValueError("A durable audit writer is required.")
        self.scope_registry = scope_registry
        self.audit_writer = audit_writer
        self.approval_checker = approval_checker
        self._tools: dict[str, tuple[ToolSpec, ToolAdapter]] = {}

    def register(self, spec: ToolSpec, adapter: ToolAdapter) -> None:
        if spec.tool_id in self._tools:
            raise ValueError(f"Tool already registered: {spec.tool_id}")
        if not callable(adapter):
            raise TypeError("Tool adapter must be callable.")
        self._tools[spec.tool_id] = (spec, adapter)

    def registered_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    @staticmethod
    def _valid_plan_digest(value: str | None) -> bool:
        return isinstance(value, str) and re.fullmatch(r"[a-fA-F0-9]{64}", value) is not None

    def execute(
        self,
        *,
        agent_id: str,
        tool_id: str,
        scope_id: str,
        target: str,
        operation: str,
        arguments: Mapping[str, Any],
        approval_id: str | None = None,
        plan_digest: str | None = None,
    ) -> Any:
        if not isinstance(arguments, Mapping):
            raise ToolAccessDenied("Tool arguments must be a structured object.")
        registered = self._tools.get(tool_id)
        if registered is None:
            self.audit_writer("tool_denied", f"unregistered tool={tool_id!r}")
            raise ToolAccessDenied("Tool is not registered; operation denied.")
        spec, adapter = registered

        if agent_id not in spec.allowed_agents:
            self.audit_writer("tool_denied", f"agent={agent_id!r} tool={tool_id!r}")
            raise ToolAccessDenied("Agent is not allowlisted for this tool.")
        if operation not in spec.allowed_operations:
            self.audit_writer("tool_denied", f"operation={operation!r} tool={tool_id!r}")
            raise ToolAccessDenied("Operation is not allowlisted for this tool.")

        try:
            self.scope_registry.require_authorised(
                scope_id=scope_id,
                target=target,
                operation=operation,
            )
        except ScopeDenied as exc:
            self.audit_writer("tool_denied", f"scope={scope_id!r} tool={tool_id!r}: {exc}")
            raise

        if spec.risk_level != "read_only":
            if (
                not approval_id
                or not self._valid_plan_digest(plan_digest)
                or self.approval_checker is None
                or not self.approval_checker(
                    approval_id, plan_digest, scope_id, tool_id, target, operation
                )
            ):
                self.audit_writer(
                    "tool_denied",
                    f"human approval missing or invalid for {spec.risk_level} tool={tool_id!r}",
                )
                raise HumanApprovalRequired(
                    "This operation requires explicit owner approval bound to the exact plan."
                )

        self.audit_writer(
            "tool_started",
            f"agent={agent_id} tool={tool_id} target={target} operation={operation}",
        )
        try:
            result = adapter(arguments)
        except Exception as exc:
            self.audit_writer("tool_failed", f"tool={tool_id} error={type(exc).__name__}")
            raise
        self.audit_writer("tool_completed", f"agent={agent_id} tool={tool_id}")
        return result
