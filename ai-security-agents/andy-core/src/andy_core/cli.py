import argparse
import json
from .orchestrator import Andy
from .store import Store


def main():
    parser = argparse.ArgumentParser(prog="andy", description="Andy local-first agent command centre")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialise the local ledger and built-in agents")
    sub.add_parser("agents", help="List registered specialist agents")
    submit = sub.add_parser("submit", help="Queue a task")
    submit.add_argument("title")
    submit.add_argument("--capability", default="general")
    submit.add_argument("--description", default="")
    sub.add_parser("run", help="Run queued tasks once")
    tasks = sub.add_parser("tasks", help="List recent tasks")
    tasks.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    andy = Andy(Store())

    if args.command == "init":
        print(f"Andy initialised. Database: {andy.store.path}")
    elif args.command == "agents":
        for a in andy.store.agents():
            print(f"{a.agent_id}: {a.name} [{', '.join(a.capabilities)}]")
    elif args.command == "submit":
        task = andy.submit(args.title, args.capability, args.description)
        print(f"Queued {task.task_id}: {task.title}")
    elif args.command == "run":
        print(f"Completed {andy.run_once()} task(s).")
    elif args.command == "tasks":
        for t in andy.store.tasks(args.limit):
            print(f"{t.status:10} {t.task_id} [{t.capability}] {t.title}")
            if t.result:
                try:
                    payload = json.loads(t.result)
                    print(payload.get("summary", ""))
                    evidence = payload.get("evidence", [])
                    if evidence:
                        print("\nSources:")
                        for item in evidence:
                            print(
                                f"- [{item.get('source_id', 'source')}] "
                                f"{item.get('title', 'Untitled')} "
                                f"({item.get('publisher', 'Unknown publisher')})"
                            )
                            print(f"  URL: {item.get('url', '')}")
                            print(f"  Retrieved: {item.get('retrieved_at', 'unknown')}")
                except (ValueError, KeyError, TypeError):
                    print(t.result)


if __name__ == "__main__":
    main()
