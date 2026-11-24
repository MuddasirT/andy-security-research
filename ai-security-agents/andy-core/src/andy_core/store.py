from pathlib import Path
import json
import os
import sqlite3
from .models import AgentSpec, Task, utc_now


def data_dir() -> Path:
    path = Path(os.environ.get("ANDY_HOME", ".andy")).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


class Store:
    def __init__(self, path: Path | None = None):
        self.path = path or data_dir() / "andy.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY, name TEXT NOT NULL,
                    capabilities TEXT NOT NULL, description TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY, title TEXT NOT NULL,
                    capability TEXT NOT NULL, description TEXT NOT NULL,
                    status TEXT NOT NULL, assigned_agent TEXT, result TEXT,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT, event_type TEXT NOT NULL,
                    detail TEXT NOT NULL, created_at TEXT NOT NULL
                );
            """)

    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def register_agent(self, spec: AgentSpec) -> None:
        with self.connect() as db:
            db.execute("""INSERT OR REPLACE INTO agents
                (agent_id,name,capabilities,description,enabled)
                VALUES (?,?,?,?,?)""",
                (spec.agent_id, spec.name, json.dumps(spec.capabilities),
                 spec.description, int(spec.enabled)))

    def agents(self) -> list[AgentSpec]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM agents ORDER BY agent_id").fetchall()
        return [AgentSpec(r["agent_id"], r["name"], tuple(json.loads(r["capabilities"])),
                          r["description"], bool(r["enabled"])) for r in rows]

    def add_task(self, task: Task) -> None:
        with self.connect() as db:
            db.execute("""INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?)""",
                (task.task_id, task.title, task.capability, task.description,
                 task.status, task.assigned_agent, task.result,
                 task.created_at, task.updated_at))
            self.event(task.task_id, "task_created", task.title, db)

    def event(self, task_id: str | None, kind: str, detail: str, db=None) -> None:
        if db is not None:
            db.execute("INSERT INTO events(task_id,event_type,detail,created_at) VALUES (?,?,?,?)",
                       (task_id, kind, detail, utc_now()))
            return
        with self.connect() as conn:
            conn.execute("INSERT INTO events(task_id,event_type,detail,created_at) VALUES (?,?,?,?)",
                         (task_id, kind, detail, utc_now()))

    def queued_tasks(self) -> list[Task]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM tasks WHERE status='queued' ORDER BY created_at").fetchall()
        return [self._task(r) for r in rows]

    def tasks(self, limit: int = 30) -> list[Task]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._task(r) for r in rows]

    def update_task(self, task_id: str, **fields) -> None:
        allowed = {"status", "assigned_agent", "result"}
        values = {k: v for k, v in fields.items() if k in allowed}
        values["updated_at"] = utc_now()
        assignments = ", ".join(f"{k}=?" for k in values)
        with self.connect() as db:
            db.execute(f"UPDATE tasks SET {assignments} WHERE task_id=?",
                       (*values.values(), task_id))

    @staticmethod
    def _task(row) -> Task:
        return Task(title=row["title"], capability=row["capability"],
                    description=row["description"], task_id=row["task_id"],
                    status=row["status"], assigned_agent=row["assigned_agent"],
                    result=row["result"], created_at=row["created_at"],
                    updated_at=row["updated_at"])
