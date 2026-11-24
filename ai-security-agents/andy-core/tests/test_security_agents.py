import unittest

from andy_core.models import Task
from andy_core.security_agents import BlueTeamAgent, PurpleTeamAgent, RedTeamAgent


class FakeModel:
    def __init__(self):
        self.calls = []

    def chat(self, system, user):
        self.calls.append((system, user))
        return "Specialist report generated for test."


class SecurityAgentTests(unittest.TestCase):
    def test_three_distinct_specialists_have_separate_capabilities_and_prompts(self):
        model = FakeModel()
        agents = [RedTeamAgent(model), BlueTeamAgent(model), PurpleTeamAgent(model)]
        self.assertEqual(
            [agent.spec.agent_id for agent in agents],
            ["red-team-specialist", "blue-team-specialist", "purple-team-specialist"],
        )
        self.assertEqual(len({agent.system_prompt for agent in agents}), 3)
        self.assertEqual(len({agent.spec.capabilities for agent in agents}), 3)

        for agent in agents:
            task = Task("Assess supplied security material", agent.spec.capabilities[0],
                        "Only analyse this authorised lab context.")
            result = agent.execute(task)
            self.assertEqual(result.status, "completed")
            self.assertEqual(result.agent_id, agent.spec.agent_id)
            self.assertTrue(any("no shell" in item.lower() for item in result.limitations))
        self.assertEqual(len(model.calls), 3)


if __name__ == "__main__":
    unittest.main()
