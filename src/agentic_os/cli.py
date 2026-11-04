from __future__ import annotations

import argparse
import json

from .core import HierarchicalAgentOS, boot_agentic_os


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the Agentic OS hierarchical agent prototype."
    )
    parser.add_argument(
        "--agent-name", default="agent", help="Name of the agent to boot."
    )
    parser.add_argument(
        "--capability",
        action="append",
        default=None,
        help="Capability to add to the runtime. Repeat as needed.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output.",
    )
    parser.add_argument("--goal", help="Submit a goal to the father agent.")
    parser.add_argument(
        "--task",
        action="append",
        default=None,
        help="Task for a child-created sub-child agent. Repeat to add tasks.",
    )
    parser.add_argument(
        "--dashboard",
        nargs="?",
        const="all",
        choices=["all", "father", "mother", "child"],
        help="Show the full hierarchy or an individual agent dashboard.",
    )
    args = parser.parse_args(argv)

    if args.task and not args.goal:
        parser.error("--task requires --goal.")
    if args.goal is not None or args.dashboard:
        system = HierarchicalAgentOS()
        run = (
            system.submit_goal(args.goal, args.task)
            if args.goal is not None
            else None
        )
        dashboard_id = (
            args.dashboard if args.dashboard in {"father", "mother", "child"} else None
        )
        dashboard = system.dashboard(dashboard_id) if args.dashboard else None
        if args.json:
            payload: dict[str, object] = {}
            if run is not None:
                payload["run"] = run.summarize()
            if dashboard is not None:
                payload["dashboard"] = dashboard
            print(json.dumps(payload, indent=2))
        else:
            if run is not None:
                print(f"{run.goal_id}: {run.status} - {run.goal}")
                for task in run.tasks:
                    print(
                        f"  {task['agent_id']}: {task['status']} - {task['task']}"
                    )
            if dashboard is not None:
                print(json.dumps(dashboard, indent=2))
        return 0

    runtime = boot_agentic_os(args.agent_name, args.capability)
    if args.json:
        print(json.dumps(runtime.summarize(), indent=2))
    else:
        print(runtime.boot())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
