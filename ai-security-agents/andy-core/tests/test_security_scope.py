import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from andy_core.security_scope import (
    AuthorisationScope, ScopeDenied, ScopeRegistry,
)


class ScopeRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.registry = ScopeRegistry(Path(self.temp.name) / "andy.db")
        self.scope = AuthorisationScope(
            scope_id="lab-001",
            owner="Muddasir",
            target="https://lab.example.test",
            allowed_operations=("http-read-only-review",),
            starts_at="2026-01-01T00:00:00+00:00",
            expires_at="2027-01-01T00:00:00+00:00",
            approval_reference="OWNER-APPROVAL-001",
        )
        self.registry.register(self.scope)

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_target_and_operation_are_authorised(self):
        result = self.registry.require_authorised(
            "lab-001", "https://lab.example.test", "http-read-only-review",
            datetime(2026, 6, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(result.scope_id, "lab-001")

    def test_unknown_scope_wrong_target_and_operation_fail_closed(self):
        cases = [
            ("missing", "https://lab.example.test", "http-read-only-review"),
            ("lab-001", "https://other.example.test", "http-read-only-review"),
            ("lab-001", "https://lab.example.test", "active-exploitation"),
        ]
        for scope_id, target, operation in cases:
            with self.subTest(scope_id=scope_id, target=target, operation=operation):
                with self.assertRaises(ScopeDenied):
                    self.registry.require_authorised(
                        scope_id, target, operation,
                        datetime(2026, 6, 1, tzinfo=timezone.utc),
                    )

    def test_expired_scope_is_denied(self):
        with self.assertRaises(ScopeDenied):
            self.registry.require_authorised(
                "lab-001", "https://lab.example.test", "http-read-only-review",
                datetime(2027, 1, 1, tzinfo=timezone.utc),
            )

    def test_duplicate_scope_id_cannot_overwrite_approval(self):
        with self.assertRaises(Exception):
            self.registry.register(self.scope)

    def test_naive_timestamps_are_rejected(self):
        invalid = AuthorisationScope(
            "bad", "owner", "target", ("read",),
            "2026-01-01T00:00:00", "2027-01-01T00:00:00+00:00", "approval",
        )
        with self.assertRaises(ValueError):
            self.registry.register(invalid)


if __name__ == "__main__":
    unittest.main()
