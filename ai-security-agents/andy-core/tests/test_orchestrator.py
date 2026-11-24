import json
import tempfile
import unittest
from pathlib import Path

from andy_core.orchestrator import Andy
from andy_core.store import Store


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
        self.assertIn("Research plan", json.loads(saved.result)["summary"])

    def test_unknown_capability_is_not_silently_discarded(self):
        task = self.andy.submit("Needs a specialist", "not-yet-installed")
        self.assertEqual(self.andy.run_once(), 0)
        saved = self.store.tasks()[0]
        self.assertEqual(saved.task_id, task.task_id)
        self.assertEqual(saved.status, "queued")


if __name__ == "__main__":
    unittest.main()
