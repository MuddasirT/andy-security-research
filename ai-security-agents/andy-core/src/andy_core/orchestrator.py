import json
from collections.abc import Mapping
from .agent_factory import build_agents
from .agents import Agent
from .models import Task, utc_now
from .quality_gate import validate_report
from .store import Store


def _normalise_evidence(agent_id: str, items: list[dict]) -> list[dict]:
    """Create contract evidence records without upgrading evidence confidence."""
    normalised = []
    used_ids: set[str] = set()
    for index, item in enumerate(items):
        item = item if isinstance(item, Mapping) else {"raw": str(item)}
        raw_id = item.get("evidence_id") or item.get("source_id") or f"evidence-{index + 1}"
        evidence_id = str(raw_id).strip() or f"evidence-{index + 1}"
        base_id = evidence_id
        suffix = 2
        while evidence_id in used_ids:
            evidence_id = f"{base_id}-{suffix}"
            suffix += 1
        used_ids.add(evidence_id)

        locator = item.get("locator") or item.get("url") or item.get("path")
        if not isinstance(locator, str) or not locator.strip():
            locator = f"agent-evidence://{agent_id}/{evidence_id}"
        evidence_type = item.get("evidence_type")
        if not isinstance(evidence_type, str) or evidence_type not in {
            "source", "artifact", "observation", "test_result", "log", "other"
        }:
            evidence_type = "source" if item.get("url") or item.get("source_id") else "other"
        captured_at = item.get("captured_at") or item.get("retrieved_at") or utc_now()
        if not isinstance(captured_at, str):
            captured_at = utc_now()
        summary = item.get("content_summary") or item.get("excerpt") or item.get("title") or item.get("raw")
        if not isinstance(summary, str) or not summary.strip():
            summary = "Evidence metadata supplied by the specialist; content requires review."
        normalised.append({
            "evidence_id": evidence_id,
            "evidence_type": evidence_type,
            "locator": locator,
            "captured_at": captured_at,
            "content_summary": summary[:1200],
        })
    return normalised


def _build_quality_report(task: Task, agent_id: str, summary: str,
                          evidence: list[dict], limitations: list[str]) -> dict:
    """Wrap legacy agent output as inference, never as a verified finding."""
    report_limitations = list(limitations) if isinstance(limitations, list) else [
        "Specialist returned limitations in an unsupported format."
    ]
    report_limitations.extend([
        "The quality gate checks report structure and evidence linkage, not factual truth or source authority.",
        "Task text does not grant testing permission. Authorisation must be checked separately by the scope gateway.",
        "The agent summary is classified as inference until each factual claim is independently evidenced and reviewed.",
    ])
    evidence = evidence if isinstance(evidence, list) else []
    return {
        "schema_version": "1.0",
        "report_id": task.task_id,
        "task_id": task.task_id,
        "agent_id": agent_id,
        "domain": task.capability,
        "report_type": "agent_analysis",
        "objective": task.title,
        "scope": {
            "summary": "No execution authority is inferred. This task result is analysis-only unless a separate scope check authorises an operation.",
            "authorization_status": "unknown",
            "targets": [],
        },
        "claims": [{
            "claim_id": f"{task.task_id}:summary",
            "text": summary or "The specialist returned an empty summary.",
            "classification": "inference",
            "evidence_refs": [],
        }],
        "evidence": _normalise_evidence(agent_id, evidence),
        "tests": [],
        "limitations": report_limitations,
    }


class Andy:
    """Central coordinator: routes work to enabled specialists by capability."""

    def __init__(self, store: Store | None = None, agents: list[Agent] | None = None):
        self.store = store or Store()
        self.workers = agents if agents is not None else build_agents()
        for worker in self.workers:
            self.store.register_agent(worker.spec)

    def submit(self, title: str, capability: str = "general", description: str = "") -> Task:
        task = Task(title=title, capability=capability, description=description)
        self.store.add_task(task)
        return task

    def run_once(self) -> int:
        completed = 0
        enabled = {
            worker.spec.agent_id: worker
            for worker in self.workers
            if worker.spec.enabled
        }
        for task in self.store.queued_tasks():
            match = next(
                (worker for worker in enabled.values()
                 if task.capability in worker.spec.capabilities),
                None,
            )
            if match is None:
                self.store.event(
                    task.task_id,
                    "unassigned",
                    f"No enabled worker for capability: {task.capability}",
                )
                continue

            self.store.update_task(
                task.task_id,
                status="running",
                assigned_agent=match.spec.agent_id,
            )
            self.store.event(task.task_id, "assigned", match.spec.agent_id)
            try:
                result = match.execute(task)
                report = _build_quality_report(
                    task, result.agent_id, result.summary,
                    result.evidence, result.limitations,
                )
                gate = validate_report(report)
                final_status = result.status
                if result.status == "completed":
                    if gate.status == "revise":
                        final_status = "needs_review"
                    elif gate.status == "rejected":
                        final_status = "quality_rejected"

                payload = json.dumps(
                    {
                        "summary": result.summary,
                        "evidence": result.evidence,
                        "limitations": result.limitations,
                        "report": report,
                        "quality_gate": gate.to_dict(),
                    },
                    ensure_ascii=False,
                    default=str,
                )
                self.store.update_task(
                    task.task_id,
                    status=final_status,
                    result=payload,
                )
                self.store.event(
                    task.task_id,
                    "quality_gate",
                    f"{gate.status}: {len(gate.issues)} issue(s)",
                )
                self.store.event(task.task_id, final_status, result.summary[:500])
                if final_status == "completed":
                    completed += 1
            except Exception as exc:
                self.store.update_task(
                    task.task_id,
                    status="failed",
                    result=str(exc),
                )
                self.store.event(task.task_id, "failed", type(exc).__name__)
        return completed
