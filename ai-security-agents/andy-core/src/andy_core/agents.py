from abc import ABC, abstractmethod
from .models import AgentResult, AgentSpec, Task


class Agent(ABC):
    spec: AgentSpec

    @abstractmethod
    def execute(self, task: Task) -> AgentResult:
        """Execute one bounded task and return an auditable result."""


class PlanningAgent(Agent):
    """Safe starter worker. Produces a plan, never performs external actions."""

    spec = AgentSpec(
        agent_id="research-planner",
        name="Research Planning Specialist",
        capabilities=("research-planning", "general"),
        description="Turns a request into a bounded plan with questions and evidence needs.",
    )

    def execute(self, task: Task) -> AgentResult:
        steps = [
            "Restate the objective and define what a successful answer must contain.",
            "Identify authoritative sources and distinguish facts from assumptions.",
            "Collect evidence with source dates and preserve citations.",
            "Cross-check important claims independently.",
            "Summarise findings, uncertainties, and recommended next steps.",
        ]
        summary = (
            f"Research plan for: {task.title}\n\n"
            f"Context: {task.description or 'No additional context supplied.'}\n\n"
            + "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))
            + "\n\nNo external systems were contacted and no actions were taken."
        )
        return AgentResult(task.task_id, self.spec.agent_id, "completed", summary,
                           evidence=[], limitations=[
                               "Planning-only demonstration worker.",
                               "No live web, repository, device, or third-party tool access.",
                               "A human must approve any future consequential action.",
                           ])
