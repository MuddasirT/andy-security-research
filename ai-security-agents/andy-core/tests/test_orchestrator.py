import json
import tempfile
import unittest
from pathlib import Path

from andy_core.orchestrator import Andy
from andy_core.models import AgentResult, AgentSpec
from andy_core.store import Store


class InvalidEvidenceAgent:
    spec = AgentSpec(
        agent_id="invalid-evidence-worker",
        name="Invalid Evidence Worker",
        capabilities=("quality-gate-test",),
        description="Returns intentionally malformed evidence metadata.",
    )

    def execute(self, task):
        return AgentResult(
            task_id=task.task_id,
            agent_id=self.spec.agent_id,
            status="completed",
            summary="A hypothetical issue needs verification.",
            evidence=[{
                "source_id": "source-1",
                "url": "https://example.test/advisory",
                "retrieved_at": "not-a-timestamp",
                "excerpt": "Test evidence excerpt.",
            }],
            limitations=["This is a validator test fixture."],
        )


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name) / "test.db")
        self.andy = Andy(self.store)

    def tearDown(self):
        self.temp.cleanup()

    def test_routes_and_persists_supported_task(self):
        task = self.andy.submit("Test research plan", "research-planning")
        self.assertEqual(self.andy.run_once(), 1)
        saved = self.store.tasks()[0]
        self.assertEqual(saved.task_id, task.task_id)
        self.assertEqual(saved.status, "completed")
        self.assertEqual(saved.assigned_agent, "research-planner")
        payload = json.loads(saved.result)
        self.assertIn("Research plan", payload["summary"])
        self.assertEqual(payload["quality_gate"]["status"], "approved")
        self.assertEqual(payload["report"]["scope"]["authorization_status"], "unknown")
        self.assertEqual(payload["report"]["claims"][0]["classification"], "inference")
        self.assertIn(
            "The agent summary is classified as inference",
            " ".join(payload["report"]["limitations"]),
        )

    def test_invalid_evidence_prevents_completed_status(self):
        andy = Andy(self.store, agents=[InvalidEvidenceAgent()])
        task = andy.submit("Check evidence handling", "quality-gate-test")
        self.assertEqual(andy.run_once(), 0)
        saved = next(item for item in self.store.tasks() if item.task_id == task.task_id)
        payload = json.loads(saved.result)
        self.assertEqual(saved.status, "needs_review")
        self.assertEqual(payload["quality_gate"]["status"], "revise")
        self.assertIn(
            "INVALID_EVIDENCE_TIMESTAMP",
            {item["code"] for item in payload["quality_gate"]["issues"]},
        )

    def test_unknown_capability_is_not_silently_discarded(self):
        task = self.andy.submit("Needs a specialist", "not-yet-installed")
        self.assertEqual(self.andy.run_once(), 0)
        saved = self.store.tasks()[0]
        self.assertEqual(saved.task_id, task.task_id)
        self.assertEqual(saved.status, "queued")


if __name__ == "__main__":
    unittest.main()
