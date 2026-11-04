from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Sequence


@dataclass
class AgentRuntime:
    """A small runtime definition for an agent operating in Agentic OS."""

    agent_name: str = "agent"
    capabilities: list[str] = field(
        default_factory=lambda: ["planning", "memory", "execution"]
    )
    gpu_enabled: bool = True
    offline_mode: bool = True

    def boot(self) -> str:
        status = "online" if self.gpu_enabled and self.offline_mode else "degraded"
        capabilities = ", ".join(self.capabilities) if self.capabilities else "none"
        return (
            f"Booting {self.agent_name} on Agentic OS ({status}) with capabilities: "
            f"{capabilities}."
        )

    def summarize(self) -> dict[str, object]:
        return {
            "agent_name": self.agent_name,
            "capabilities": self.capabilities,
            "gpu_enabled": self.gpu_enabled,
            "offline_mode": self.offline_mode,
            "status": "online" if self.gpu_enabled and self.offline_mode else "degraded",
        }


class AgentRole(str, Enum):
    FATHER = "father"
    MOTHER = "mother"
    CHILD = "child"
    SUBCHILD = "subchild"


@dataclass
class Agent:
    agent_id: str
    role: AgentRole
    parent_id: str | None
    capabilities: list[str]
    company_id: str | None = None
    company_name: str | None = None
    children: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    reports: list[dict[str, str]] = field(default_factory=list)

    def dashboard(self) -> dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "title": {
                AgentRole.FATHER: "Group of Companies",
                AgentRole.MOTHER: "CEO",
                AgentRole.CHILD: "General Manager",
                AgentRole.SUBCHILD: "Manager",
            }[self.role],
            "company_id": self.company_id,
            "company_name": self.company_name,
            "parent_id": self.parent_id,
            "children": list(self.children),
            "capabilities": list(self.capabilities),
            "goals": list(self.goals),
            "reports": [dict(report) for report in self.reports],
        }


class PolicyEngine:
    """Enforces the fixed delegation chain and father-only user intake."""

    _allowed_handoffs = {
        AgentRole.FATHER: AgentRole.MOTHER,
        AgentRole.MOTHER: AgentRole.CHILD,
        AgentRole.CHILD: AgentRole.SUBCHILD,
    }

    def authorize_user_input(self, agent: Agent) -> None:
        if agent.role is not AgentRole.FATHER or agent.parent_id is not None:
            raise PermissionError("Only the root father agent can receive user goals.")

    def authorize_handoff(self, source: Agent, target: Agent) -> None:
        expected_role = self._allowed_handoffs.get(source.role)
        if (
            expected_role is None
            or target.role is not expected_role
            or target.parent_id != source.agent_id
            or (
                source.role is not AgentRole.FATHER
                and target.company_id != source.company_id
            )
        ):
            raise PermissionError(
                f"Policy forbids delegation from {source.role.value} "
                f"to {target.role.value}."
            )

    def describe_agent(self, agent: Agent) -> dict[str, object]:
        next_role = self._allowed_handoffs.get(agent.role)
        return {
            "can_receive_user_goals": (
                agent.role is AgentRole.FATHER and agent.parent_id is None
            ),
            "can_delegate_to": [
                {
                    AgentRole.MOTHER: "CEO",
                    AgentRole.CHILD: "General Manager",
                    AgentRole.SUBCHILD: "Manager",
                }[next_role]
            ] if next_role else [],
            "reports_to": agent.parent_id,
        }


@dataclass
class GoalRun:
    goal_id: str
    goal: str
    status: str
    company_id: str
    company_name: str
    tasks: list[dict[str, str]]
    handoffs: list[dict[str, str]]
    reports: list[dict[str, str]]

    def summarize(self) -> dict[str, object]:
        return {
            "goal_id": self.goal_id,
            "goal": self.goal,
            "status": self.status,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "tasks": [dict(task) for task in self.tasks],
            "handoffs": [dict(handoff) for handoff in self.handoffs],
            "reports": [dict(report) for report in self.reports],
        }


class HierarchicalAgentOS:
    """Group and company agent hierarchy with optional task execution."""

    def __init__(
        self,
        executor: Callable[[str], str] | None = None,
        companies: Sequence[str] | None = None,
    ) -> None:
        self.policy = PolicyEngine()
        self.executor = executor
        self.agents: dict[str, Agent] = {
            "father": Agent(
                "father", AgentRole.FATHER, None, ["group-oversight", "goal-routing"]
            )
        }
        self.companies: list[dict[str, str]] = []
        self._company_counter = 0
        self._goal_counter = 0
        for company in companies if companies is not None else ["Company 1"]:
            self.add_company(company)

    def add_company(self, name: str) -> dict[str, str]:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Company name must be a non-empty string.")
        normalized_name = name.strip()
        if any(
            company["name"].casefold() == normalized_name.casefold()
            for company in self.companies
        ):
            raise ValueError(f"Company already exists: {normalized_name}")

        self._company_counter += 1
        company_id = f"company-{self._company_counter}"
        ceo_id = "mother" if self._company_counter == 1 else f"mother-{company_id}"
        gm_id = "child" if self._company_counter == 1 else f"child-{company_id}"
        company = {
            "company_id": company_id,
            "name": normalized_name,
            "ceo_id": ceo_id,
            "gm_id": gm_id,
        }
        self.companies.append(company)
        self.agents["father"].children.append(ceo_id)
        self.agents[ceo_id] = Agent(
            ceo_id,
            AgentRole.MOTHER,
            "father",
            ["company-planning", "coordination"],
            company_id=company_id,
            company_name=normalized_name,
        )
        self.agents[ceo_id].children.append(gm_id)
        self.agents[gm_id] = Agent(
            gm_id,
            AgentRole.CHILD,
            ceo_id,
            ["operations", "task-delegation", "reporting"],
            company_id=company_id,
            company_name=normalized_name,
        )
        return dict(company)

    def submit_goal(
        self,
        goal: str,
        tasks: Sequence[str] | None = None,
        company: str | None = None,
    ) -> GoalRun:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("Goal must be a non-empty string.")
        if isinstance(tasks, str):
            raise TypeError("Tasks must be a sequence of strings, not a string.")

        work_items = list(tasks) if tasks is not None else [goal.strip()]
        if not work_items or any(
            not isinstance(task, str) or not task.strip() for task in work_items
        ):
            raise ValueError("Tasks must contain at least one non-empty string.")
        work_items = [task.strip() for task in work_items]

        father = self.agents["father"]
        if not self.companies:
            raise ValueError("Add a company before submitting a goal.")
        if company is not None and not isinstance(company, str):
            raise TypeError("Company must be a company name or company ID.")
        selected_company = next(
            (
                item
                for item in self.companies
                if company is None
                or item["company_id"] == company
                or item["name"].casefold() == company.casefold()
            ),
            None,
        )
        if selected_company is None:
            raise ValueError(f"Unknown company: {company}")
        mother = self.agents[selected_company["ceo_id"]]
        child = self.agents[selected_company["gm_id"]]
        self.policy.authorize_user_input(father)

        self._goal_counter += 1
        goal_id = f"goal-{self._goal_counter}"
        normalized_goal = goal.strip()
        for agent in (father, mother, child):
            agent.goals.append(goal_id)

        handoffs = [
            self._handoff(father, mother, goal_id),
            self._handoff(mother, child, goal_id),
        ]
        tasks_result: list[dict[str, str]] = []
        reports: list[dict[str, str]] = [
            {
                "agent_id": "father",
                "goal_id": goal_id,
                "company_name": selected_company["name"],
                "message": f"Received user goal: {normalized_goal}",
            },
            {
                "agent_id": mother.agent_id,
                "goal_id": goal_id,
                "company_name": selected_company["name"],
                "message": f"Prepared {len(work_items)} task(s) for child agent.",
            },
        ]

        for index, task in enumerate(work_items, start=1):
            worker_id = f"manager-{self._goal_counter}-{index}"
            worker = Agent(
                worker_id,
                AgentRole.SUBCHILD,
                child.agent_id,
                ["task-management", "task-execution"],
                company_id=selected_company["company_id"],
                company_name=selected_company["name"],
            )
            self.agents[worker_id] = worker
            child.children.append(worker_id)
            worker.goals.append(goal_id)
            handoffs.append(self._handoff(child, worker, goal_id))

            if self.executor is None:
                status = "awaiting_executor"
                message = "Task queued; no executor is configured."
            else:
                result = self.executor(task)
                status = "completed"
                message = result

            task_report = {
                "agent_id": worker_id,
                "task": task,
                "status": status,
                "message": message,
            }
            tasks_result.append(task_report)
            reports.append(
                {
                    "agent_id": worker_id,
                    "goal_id": goal_id,
                    "company_name": selected_company["name"],
                    "task": task,
                    "status": status,
                    "message": f"Reported task status: {status}.",
                }
            )

        final_status = (
            "completed"
            if all(task["status"] == "completed" for task in tasks_result)
            else "awaiting_executor"
        )
        upward_reports = [
            {
                "agent_id": child.agent_id,
                "goal_id": goal_id,
                "company_name": selected_company["name"],
                "message": f"Received {len(tasks_result)} sub-child report(s); "
                f"overall status: {final_status}.",
            },
            {
                "agent_id": mother.agent_id,
                "goal_id": goal_id,
                "company_name": selected_company["name"],
                "message": f"Child report received; overall status: {final_status}.",
            },
            {
                "agent_id": "father",
                "goal_id": goal_id,
                "company_name": selected_company["name"],
                "message": f"Mother report received; overall status: {final_status}.",
            },
        ]
        reports.extend(upward_reports)
        for report in reports:
            agent_report = {
                key: value
                for key, value in report.items()
                if key not in {"agent_id", "goal_id"}
            }
            self.agents[report["agent_id"]].reports.append(
                {"goal_id": goal_id, **agent_report}
            )

        return GoalRun(
            goal_id=goal_id,
            goal=normalized_goal,
            status=final_status,
            company_id=selected_company["company_id"],
            company_name=selected_company["name"],
            tasks=tasks_result,
            handoffs=handoffs,
            reports=reports,
        )

    def dashboard(self, agent_id: str | None = None) -> dict[str, object]:
        if agent_id is not None:
            try:
                agent = self.agents[agent_id]
            except KeyError as error:
                raise ValueError(f"Unknown agent: {agent_id}") from error
            return self._agent_dashboard(agent)
        return {
            "agents": [
                self._agent_dashboard(agent) for agent in self.agents.values()
            ],
            "companies": [dict(company) for company in self.companies],
            "policy": {
                "user_goal_receiver": "father",
                "delegation_chain": [
                    "Group of Companies",
                    "CEO",
                    "General Manager",
                    "Manager",
                ],
            },
        }

    def _agent_dashboard(self, agent: Agent) -> dict[str, object]:
        dashboard = agent.dashboard()
        dashboard["policy"] = self.policy.describe_agent(agent)
        return dashboard

    def _handoff(self, source: Agent, target: Agent, goal_id: str) -> dict[str, str]:
        self.policy.authorize_handoff(source, target)
        return {
            "from": source.agent_id,
            "to": target.agent_id,
            "goal_id": goal_id,
        }


def boot_agentic_os(
    agent_name: str = "agent", capabilities: Sequence[str] | None = None
) -> AgentRuntime:
    """Create and initialize an AgentRuntime instance."""

    runtime = AgentRuntime(
        agent_name=agent_name,
        capabilities=(
            list(capabilities)
            if capabilities
            else ["planning", "memory", "execution"]
        ),
    )
    return runtime
