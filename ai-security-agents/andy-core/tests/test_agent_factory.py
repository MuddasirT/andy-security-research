import os
import unittest
from unittest.mock import patch

from andy_core.agent_factory import build_agents


class AgentFactoryTests(unittest.TestCase):
    def test_planner_is_always_available_when_model_is_disabled(self):
        with patch.dict(os.environ, {}, clear=True):
            agents = build_agents()
        self.assertEqual([agent.spec.agent_id for agent in agents], ["research-planner"])

    def test_ollama_worker_is_opt_in(self):
        with patch.dict(os.environ, {"ANDY_LLM_PROVIDER": "ollama"}, clear=True):
            agents = build_agents()
        self.assertEqual(
            [agent.spec.agent_id for agent in agents],
            ["research-planner", "android-source-researcher", "llm-researcher"],
        )
        self.assertEqual(agents[1].model.model, "qwen3:8b")
        self.assertIs(agents[1].model, agents[2].model)

    def test_unknown_provider_fails_fast(self):
        with patch.dict(os.environ, {"ANDY_LLM_PROVIDER": "unknown"}, clear=True):
            with self.assertRaises(ValueError):
                build_agents()


if __name__ == "__main__":
    unittest.main()
