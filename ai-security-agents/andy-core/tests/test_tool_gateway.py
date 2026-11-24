import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from andy_core.security_scope import AuthorisationScope, ScopeDenied, ScopeRegistry
from andy_core.tool_gateway import (
    HumanApprovalRequired, ToolAccessDenied, ToolGateway, ToolSpec,
)


class ToolGatewayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.registry = ScopeRegistry(Path(self.temp.name) / "andy.db")
        self.registry.register(AuthorisationScope(
            scope_id="lab-01",
            owner="owner",
            target="https://app.lab.test",
            allowed_operations=("http-read-only-review", "http-active-validation"),
            starts_at="2026-01-01T00:00:00+00:00",
            expires_at="2027-01-01T00:00:00+00:00",
            approval_reference="recorded-owner-approval",
        ))
        self.events = []
        self.calls = []
        self.digest = "a" * 64
        self.gateway = ToolGateway(
            self.registry,
            lambda kind, detail: self.events.append((kind, detail)),
            approval_checker=lambda approval, digest, scope, tool, target, operation: (
                approval == "owner-approved-001"
                and digest == self.digest
                and scope == "lab-01"
                and tool == "http-check"
                and target == "https://app.lab.test"
                and operation == "http-active-validation"
            ),
        )

    def tearDown(self):
        self.temp.cleanup()

    def _adapter(self, arguments):
        self.calls.append(dict(arguments))
        return {"ok": True}

    def test_read_only_operation_requires_registered_agent_and_scope(self):
        self.gateway.register(ToolSpec(
            "http-check", ("red-team-specialist",),
            ("http-read-only-review",), "read_only",
        ), self._adapter)
        result = self.gateway.execute(
            agent_id="red-team-specialist",
            tool_id="http-check",
            scope_id="lab-01",
            target="https://app.lab.test",
            operation="http-read-only-review",
            arguments={"path": "/"},
        )
        self.assertEqual(result, {"ok": True})
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.events[-1][0], "tool_completed")

    def test_unregistered_tool_and_unapproved_agent_are_denied(self):
        self.gateway.register(ToolSpec(
            "http-check", ("red-team-specialist",),
            ("http-read-only-review",), "read_only",
        ), self._adapter)
        with self.assertRaises(ToolAccessDenied):
            self.gateway.execute(
                agent_id="blue-team-specialist", tool_id="http-check",
                scope_id="lab-01", target="https://app.lab.test",
                operation="http-read-only-review", arguments={},
            )
        with self.assertRaises(ToolAccessDenied):
            self.gateway.execute(
                agent_id="red-team-specialist", tool_id="not-registered",
                scope_id="lab-01", target="https://app.lab.test",
                operation="http-read-only-review", arguments={},
            )
        self.assertEqual(self.calls, [])

    def test_scope_mismatch_fails_before_adapter(self):
        self.gateway.register(ToolSpec(
            "http-check", ("red-team-specialist",),
            ("http-read-only-review",), "read_only",
        ), self._adapter)
        with self.assertRaises(ScopeDenied):
            self.gateway.execute(
                agent_id="red-team-specialist", tool_id="http-check",
                scope_id="lab-01", target="https://wrong.lab.test",
                operation="http-read-only-review", arguments={},
            )
        self.assertEqual(self.calls, [])

    def test_active_operation_requires_exact_owner_approval(self):
        self.gateway.register(ToolSpec(
            "http-check", ("red-team-specialist",),
            ("http-active-validation",), "active",
        ), self._adapter)
        args = dict(
            agent_id="red-team-specialist", tool_id="http-check",
            scope_id="lab-01", target="https://app.lab.test",
            operation="http-active-validation", arguments={"check": "safe-probe"},
        )
        with self.assertRaises(HumanApprovalRequired):
            self.gateway.execute(**args)
        with self.assertRaises(HumanApprovalRequired):
            self.gateway.execute(**args, approval_id="owner-approved-001", plan_digest="bad")
        self.assertEqual(self.calls, [])
        result = self.gateway.execute(
            **args, approval_id="owner-approved-001", plan_digest=self.digest
        )
        self.assertEqual(result, {"ok": True})
        self.assertEqual(len(self.calls), 1)

    def test_missing_audit_writer_is_rejected(self):
        with self.assertRaises(ValueError):
            ToolGateway(self.registry, None)

    def test_duplicate_tool_registration_is_rejected(self):
        spec = ToolSpec(
            "http-check", ("red-team-specialist",),
            ("http-read-only-review",), "read_only",
        )
        self.gateway.register(spec, self._adapter)
        with self.assertRaises(ValueError):
            self.gateway.register(spec, self._adapter)


if __name__ == "__main__":
    unittest.main()
