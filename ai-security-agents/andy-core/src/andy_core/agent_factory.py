"""Construct the built-in workers from explicit environment configuration."""
import os

from .agents import PlanningAgent
from .llm import OllamaChatModel
from .llm_agent import LLMResearchAgent


def build_agents():
    agents = [PlanningAgent()]
    provider = os.getenv("ANDY_LLM_PROVIDER", "").strip().lower()

    if provider == "ollama":
        agents.append(LLMResearchAgent(OllamaChatModel()))
    elif provider:
        raise ValueError(
            f"Unsupported ANDY_LLM_PROVIDER={provider!r}. "
            "Supported provider: ollama."
        )

    return agents
