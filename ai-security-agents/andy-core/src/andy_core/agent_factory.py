"""Construct built-in workers from explicit environment configuration."""
import os

from .agents import PlanningAgent
from .llm import OllamaChatModel
from .llm_agent import LLMResearchAgent
from .research_agent import SourceBackedAndroidResearchAgent
from .security_agents import BlueTeamAgent, PurpleTeamAgent, RedTeamAgent


def build_agents():
    agents = [PlanningAgent()]
    provider = os.getenv("ANDY_LLM_PROVIDER", "").strip().lower()

    if provider == "ollama":
        model = OllamaChatModel()
        # Evidence-backed Android research takes precedence for its capability.
        agents.append(SourceBackedAndroidResearchAgent(model))
        agents.append(RedTeamAgent(model))
        agents.append(BlueTeamAgent(model))
        agents.append(PurpleTeamAgent(model))
        agents.append(LLMResearchAgent(model))
    elif provider:
        raise ValueError(
            f"Unsupported ANDY_LLM_PROVIDER={provider!r}. "
            "Supported provider: ollama."
        )

    return agents
