import json
from .agents import Agent, PlanningAgent
from .models import Task
from .store import Store


class Andy:
    """Central coordinator: routes work to enabled specialists by capability."""

    def __init__(self, store: Store | None = None, agents: list[Agent] | None = None):
        self.store = store or Store()
        self.workers = agents or [PlanningAgent()]
        for worker in self.workers:
            self.store.register_agent(worker.spec)

    def submit(self, title: str, capability: str = "general", description: str = "") -> Task:
        task = Task(title=title, capability=capability, description=description)
        self.store.add_task(task)
        return task

    def run_once(self) -> int:
        completed = 0
        enabled = {a.agent_id: a for a in self.workers if a.spec.enabled}
        specs = {s.agent_id: s for s in self.store.agents() if s.enabled}
        for task in self.store.queued_tasks():
            match = next((a for a in enabled.values()
                          if task.capability in a.spec.capabilities), None)
            if match is None:
                self.store.event(task.task_id, "unassigned",
                                 f"No enabled worker for capability: {task.capability}")
                continue
            self.store.update_task(task.task_id, status="running",
                                   assigned_agent=match.spec.agent_id)
            self.store.event(task.task_id, "assigned", match.spec.agent_id)
            try:
                result = match.execute(task)
                payload = json.dumps({
                    "summary": result.summary,
                    "evidence": result.evidence,
                    "limitations": result.limitations,
                }, ensure_ascii=False)
                self.store.update_task(task.task_id, status=result.status, result=payload)
                self.store.event(task.task_id, result.status, result.summary[:500])
                completed += 1
            except Exception as exc:
                self.store.update_task(task.task_id, status="failed", result=str(exc))
                self.store.event(task.task_id, "failed", type(exc).__name__)
        return completed
