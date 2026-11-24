"""Construct the built-in workers from explicit environment configuration."""
import os

from .agents import PlanningAgent
from .llm import OllamaChatModel
from .llm_agent import LLMResearchAgent
from .research_agent import SourceBackedAndroidResearchAgent


def build_agents():
    agents = [PlanningAgent()]
    provider = os.getenv("ANDY_LLM_PROVIDER", "").strip().lower()

    if provider == "ollama":
        model = OllamaChatModel()
        # Android security tasks prefer the evidence-backed worker.
        agents.append(SourceBackedAndroidResearchAgent(model))
        agents.append(LLMResearchAgent(model))
    elif provider:
        raise ValueError(
            f"Unsupported ANDY_LLM_PROVIDER={provider!r}. "
            "Supported provider: ollama."
        )

    return agents
