import unittest

from andy_core.llm_agent import LLMResearchAgent
from andy_core.models import Task


class FakeModel:
    def __init__(self, response="A verified-by-test analysis."):
        self.response = response
        self.calls = []

    def chat(self, system, user):
        self.calls.append((system, user))
        return self.response


class LLMResearchAgentTests(unittest.TestCase):
    def test_uses_model_and_returns_explicit_limitations(self):
        model = FakeModel()
        agent = LLMResearchAgent(model)
        task = Task(
            title="Review Android exported components",
            capability="android-security-analysis",
            description="Focus on defensive review and remediation.",
        )

        result = agent.execute(task)

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.agent_id, "llm-researcher")
        self.assertEqual(result.summary, "A verified-by-test analysis.")
        self.assertEqual(len(model.calls), 1)
        self.assertIn("Android exported components", model.calls[0][1])
        self.assertTrue(any("No web search" in item for item in result.limitations))
        self.assertEqual(result.evidence, [])


if __name__ == "__main__":
    unittest.main()
