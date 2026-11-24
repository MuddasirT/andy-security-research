import unittest

from andy_core.models import Task
from andy_core.research_agent import SourceBackedAndroidResearchAgent


class FakeModel:
    def __init__(self):
        self.calls = []

    def chat(self, system, user):
        self.calls.append((system, user))
        return "Evidence-based draft [android-exported-risk]." if len(self.calls) == 1 else "Review Verdict: ACCEPT"


class FakeFetcher:
    def fetch_all(self):
        return [{
            "source_id": "android-exported-risk",
            "title": "Android Developers: android:exported",
            "publisher": "Android Developers",
            "url": "https://developer.android.com/privacy-and-security/risks/android-exported",
            "retrieved_at": "2026-01-01T00:00:00+00:00",
            "excerpt": "Explicitly set android:exported.",
        }]


class SourceBackedResearchTests(unittest.TestCase):
    def test_fetches_evidence_then_runs_research_and_review(self):
        model = FakeModel()
        agent = SourceBackedAndroidResearchAgent(model, FakeFetcher())
        task = Task(
            title="Review exported Android activities",
            capability="source-backed-research",
        )

        result = agent.execute(task)

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.agent_id, "android-source-researcher")
        self.assertEqual(len(model.calls), 2)
        self.assertIn("android-exported-risk", model.calls[0][1])
        self.assertIn("Independent Evidence Review", result.summary)
        self.assertEqual(result.evidence[0]["url"], FakeFetcher().fetch_all()[0]["url"])
        self.assertTrue(any("No APK" in item for item in result.limitations))


if __name__ == "__main__":
    unittest.main()
