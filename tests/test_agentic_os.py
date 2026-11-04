import io
import json
import subprocess
import sys
import threading
import unittest
from contextlib import redirect_stdout
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agentic_os.cli import main
from agentic_os.core import (
    Agent,
    AgentRole,
    AgentRuntime,
    HierarchicalAgentOS,
    PolicyEngine,
    boot_agentic_os,
)
from agentic_os.web import create_handler


class AgenticOsTests(unittest.TestCase):
    def test_runtime_boot_message(self):
        runtime = boot_agentic_os("research-agent", ["planning", "memory"])
        self.assertEqual(runtime.agent_name, "research-agent")
        self.assertIn("research-agent", runtime.boot())
        self.assertIn("planning", runtime.boot())

    def test_runtime_summary(self):
        runtime = AgentRuntime(agent_name="orchestrator", capabilities=["planning"])
        summary = runtime.summarize()
        self.assertEqual(summary["agent_name"], "orchestrator")
        self.assertEqual(summary["capabilities"], ["planning"])
        self.assertTrue(summary["offline_mode"])

    def test_cli_json_output(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                ["--agent-name", "demo-agent", "--capability", "planning", "--json"]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["agent_name"], "demo-agent")
        self.assertIn("planning", payload["capabilities"])

    def test_goal_follows_hierarchy_and_reports_upward(self):
        system = HierarchicalAgentOS()
        run = system.submit_goal("Build a plan", ["Research", "Summarize"])

        self.assertEqual(run.status, "awaiting_executor")
        self.assertEqual(
            [(handoff["from"], handoff["to"]) for handoff in run.handoffs],
            [
                ("father", "mother"),
                ("mother", "child"),
                ("child", "manager-1-1"),
                ("child", "manager-1-2"),
            ],
        )
        self.assertEqual(
            [task["status"] for task in run.tasks],
            ["awaiting_executor", "awaiting_executor"],
        )
        self.assertEqual(
            [report["agent_id"] for report in run.reports[-3:]],
            ["child", "mother", "father"],
        )

    def test_executor_runs_each_child_task_and_completes_goal(self):
        executed = []
        system = HierarchicalAgentOS(
            executor=lambda task: executed.append(task) or f"Done: {task}"
        )
        run = system.submit_goal("Ship feature", ["Implement", "Test"])

        self.assertEqual(executed, ["Implement", "Test"])
        self.assertEqual(run.status, "completed")
        self.assertEqual([task["status"] for task in run.tasks], ["completed"] * 2)

    def test_dashboard_exposes_individual_agent_and_workers(self):
        system = HierarchicalAgentOS()
        system.submit_goal("Do work", ["One task"])

        dashboard = system.dashboard("child")
        self.assertEqual(dashboard["role"], "child")
        self.assertEqual(dashboard["title"], "General Manager")
        self.assertEqual(dashboard["children"], ["manager-1-1"])
        self.assertEqual(dashboard["policy"]["can_delegate_to"], ["Manager"])
        self.assertEqual(system.dashboard()["policy"]["user_goal_receiver"], "father")

    def test_policy_rejects_skipping_a_hierarchy_level(self):
        policy = PolicyEngine()
        father = Agent("father", AgentRole.FATHER, None, [])
        child = Agent("child", AgentRole.CHILD, "father", [])

        with self.assertRaises(PermissionError):
            policy.authorize_handoff(father, child)

    def test_invalid_goals_and_tasks_are_rejected(self):
        system = HierarchicalAgentOS()
        with self.assertRaises(ValueError):
            system.submit_goal("  ")
        with self.assertRaises(ValueError):
            system.submit_goal("Goal", [""])
        with self.assertRaises(TypeError):
            system.submit_goal("Goal", "not-a-task-sequence")

    def test_cli_goal_json_includes_run_and_dashboard(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                [
                    "--goal",
                    "Prepare report",
                    "--task",
                    "Gather facts",
                    "--dashboard",
                    "--json",
                ]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["run"]["status"], "awaiting_executor")
        self.assertEqual(
            payload["dashboard"]["policy"]["delegation_chain"][-1], "Manager"
        )

    def test_company_branches_have_separate_ceo_and_general_manager(self):
        system = HierarchicalAgentOS(companies=["North", "South"])
        run = system.submit_goal("Prepare launch", ["Research"], company="South")
        dashboard = system.dashboard()
        agents = {agent["agent_id"]: agent for agent in dashboard["agents"]}

        self.assertEqual(run.company_name, "South")
        self.assertEqual(agents["father"]["children"], ["mother", "mother-company-2"])
        self.assertEqual(agents["mother-company-2"]["title"], "CEO")
        self.assertEqual(agents["mother-company-2"]["company_name"], "South")
        self.assertEqual(agents["child-company-2"]["title"], "General Manager")
        self.assertEqual(agents["child-company-2"]["goals"], ["goal-1"])
        self.assertEqual(agents["mother"]["goals"], [])

    def test_company_names_must_be_unique(self):
        system = HierarchicalAgentOS()
        with self.assertRaises(ValueError):
            system.add_company("  COMPANY 1 ")

    def test_web_dashboard_and_goal_api(self):
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), create_handler(HierarchicalAgentOS())
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            with urlopen(f"{base_url}/") as response:
                html = response.read().decode()
            self.assertIn("Build, run, and govern agents on your own infrastructure", html)
            self.assertIn("General Manager", html)
            for layer in (
                "Model layer",
                "Memory layer",
                "Tool/integration layer",
                "Orchestration layer",
                "Workflow layer",
                "Interface layer",
                "Governance, guardrails, and audit",
                "Observability and continuous improvement",
            ):
                self.assertIn(layer, html)
            self.assertIn("Eight-layer platform architecture", html)

            request = Request(
                f"{base_url}/api/goals",
                data=json.dumps(
                    {
                        "goal": "Prepare report",
                        "tasks": ["Gather facts"],
                        "company": "company-1",
                    }
                ).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request) as response:
                result = json.load(response)
                self.assertEqual(response.status, 201)
            self.assertEqual(result["status"], "awaiting_executor")
            self.assertEqual(result["company_name"], "Company 1")

            add_company = Request(
                f"{base_url}/api/companies",
                data=json.dumps({"name": "Northwind"}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(add_company) as response:
                company = json.load(response)
                self.assertEqual(response.status, 201)
            self.assertEqual(company["name"], "Northwind")

            with urlopen(f"{base_url}/api/dashboard") as response:
                dashboard = json.load(response)
            self.assertEqual(
                [agent["title"] for agent in dashboard["agents"][:3]],
                ["Group of Companies", "CEO", "General Manager"],
            )
            self.assertEqual(
                [company["name"] for company in dashboard["companies"]],
                ["Company 1", "Northwind"],
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_web_goal_api_reports_invalid_goals(self):
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), create_handler(HierarchicalAgentOS())
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        request = Request(
            f"http://127.0.0.1:{server.server_port}/api/goals",
            data=json.dumps({"goal": ""}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self.assertRaises(HTTPError) as error:
                urlopen(request)
            self.assertEqual(error.exception.code, 400)
            self.assertIn("non-empty", error.exception.read().decode())
            error.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_server_module_runs_with_python_m(self):
        result = subprocess.run(
            [sys.executable, "-m", "agentic_os.server", "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Run the local GOD AI OS dashboard.", result.stdout)


if __name__ == "__main__":
    unittest.main()
