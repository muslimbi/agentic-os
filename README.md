# Agentic OS

> **Open-source, self-hosted AI agent platform for your company's AI teammates.**
> Build, run, and govern agents on your own servers and models.

Agentic OS is an early prototype toward a self-hosted platform for company AI
teammates. The product vision includes shared chat, retrieval-augmented
generation (RAG), skills, a real browser, broad MCP server integrations,
budgets, human approvals, and an audit trail. The current implementation is an
in-memory hierarchical orchestration prototype; these platform capabilities
are roadmap goals, not features available today.

The intended governance model is the human-led GOD AI OS hierarchy: Root User
→ Father → Mother → Children → Sub-Children → Specialized Workers. See the
[GOD AI OS foundational design](docs/GOD_AI_OS_DESIGN.md) for its principles,
subsystems, design review, and phased implementation sequence.

The proposed direction is to build on Pydantic AI and use an Apache-2.0
license. **The current repository is GPL-3.0-or-later and does not yet depend on
Pydantic AI.** The license and framework have not been changed.

The canonical design makes Father Root's only direct AI interface, with work
delegated down the hierarchy and reports returned through direct parents. The
current prototype uses a company-oriented variant: Father has a Mother CEO and
Child General Manager for each company, and the General Manager creates
Sub-child task managers for individual tasks. This is an implementation detail
that still needs reconciliation with the canonical hierarchy; it does not
change the intended Root authority or reporting rules.

```text
                         Father (Group of Companies)
                          /                  \
             Mother (CEO, Company A)   Mother (CEO, Company B)
                    |                         |
          Child (General Manager)    Child (General Manager)
                    |                         |
             Sub-child managers        Sub-child managers
```

## Product direction

The goal is to let teams build, run, and govern AI teammates using infrastructure
and models they control. Planned capabilities include:

- Shared team chat and RAG over company knowledge.
- A reusable skills hub and integrations with agent CLIs such as OpenCode,
  Hermes, and Antigravity.
- Browser and computer control, including vision-driven operation.
- MCP server discovery and integrations, targeting a catalog of 4,700+ servers.
- Budgets, cost analytics, human-in-the-loop approvals, and an audit trail.
- Multi-user RBAC, visual workflows, voice, knowledge-graph memory, scheduling,
  and backup.

Agent governance, data ownership, and self-hosting are product goals; the
prototype currently has no authentication, persistence, audit system, RAG, MCP
integration, or team chat. Agentic OS is intended as an open-source alternative
to hosted enterprise agent products such as ChatGPT Enterprise and Grok Bot;
this is a product-positioning statement, not a feature comparison.

## Platform architecture

The platform is organized into eight cooperating layers:

1. **Model layer** — AI models that reason and generate responses. Model
   provider integration is planned; no model is connected in this prototype.
2. **Memory layer** — Context, conversation history, and organizational
   knowledge. Long-term storage, RAG, and knowledge graphs are planned; current
   runtime state is in memory only.
3. **Tool/integration layer** — Agent capabilities such as skills, browser
   control, and MCP/CLI integrations. These integrations are planned, not
   connected today.
4. **Orchestration layer** — The hierarchical group/company agents, delegation
   policy, and report flow. A basic in-process version is implemented.
5. **Workflow layer** — Processes that chain tasks and approvals. The prototype
   accepts a supplied list of tasks; visual workflows and approval gates are
   planned.
6. **Interface layer** — Human-facing chat, controls, and monitoring. A basic
   browser dashboard for companies, goals, and agent reports is implemented;
   shared chat and multi-user access are planned.
7. **Governance, guardrails, and audit** — Policies, permission boundaries,
   approval gates, and traceable records that keep agent actions accountable.
   Basic delegation-policy checks and in-memory reports exist; approvals,
   identity/RBAC, and a durable, tamper-resistant audit trail are planned.
8. **Observability and continuous improvement** — Metrics, traces, evaluations,
   and feedback loops used to monitor agent quality and improve performance.
   Basic in-memory reports are available; metrics, tracing, evaluation, and
   automated improvement loops are planned.

## What this prototype does today

- Enforces father-only user goal intake and the group-to-CEO-to-General
  Manager-to-task-manager delegation policy.
- Gives each company its own CEO and General Manager branch. The browser
  dashboard can add companies and route goals to a selected company.
- Splits work into the tasks supplied with a goal. If no tasks are supplied,
  the goal is passed through as one task; no language model currently decomposes
  it.
- Creates one sub-child worker per task and records handoffs, reports, and
  per-agent dashboards in memory.
- Supports an optional Python task executor through the `HierarchicalAgentOS`
  API.

Without a configured executor, tasks are reported as `awaiting_executor`. The
CLI does not run arbitrary task descriptions or connect to language models,
hardware schedulers, persistent memory, or a bootable operating-system kernel.
This project is an orchestration foundation, not an AGI/ASI system.
Improving sub-agent capabilities is a long-term direction; evaluation,
learning, and autonomous improvement loops are not implemented yet.

## Usage

Install the package in editable mode:

```bash
python -m pip install -e .
```

Then submit a goal:

```bash
agentic-os --goal "Prepare a project proposal" \
  --task "Collect requirements" \
  --task "Draft the proposal" \
  --json
```

The browser dashboard starts with a default company. Use its **Add a company**
form to create more company branches, then select the target company when
submitting a goal.

Show all agent dashboards or an individual role dashboard:

```bash
agentic-os --goal "Prepare a project proposal" --dashboard
agentic-os --goal "Prepare a project proposal" --dashboard mother --json
```

Launch the visual browser dashboards for Father, Mother, and Child:

```bash
agentic-os-web
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). The local dashboard lets
you inspect each agent's role, policy, reports, and assigned goals, and submit
goals through the hierarchy. State is in memory and resets when the server
stops. Tasks remain `awaiting_executor` unless an executor is configured in
code.

Use the API to provide an executor:

```python
from agentic_os import HierarchicalAgentOS

system = HierarchicalAgentOS(executor=lambda task: f"Completed: {task}")
run = system.submit_goal("Prepare a proposal", ["Collect requirements", "Draft it"])
print(run.summarize())
print(system.dashboard("child"))
```

The executor is application-supplied; this prototype does not implement an
LLM-powered executor or automatic agent self-improvement.

## GOD AI OS dashboard scaffold

The expanded layout adds a local FastAPI server and a 22-page vanilla-JavaScript
dashboard shell. The overview reads the existing in-memory orchestration
prototype; other pages, skills, prompts, adapters, search, backup, and restore
are explicitly marked as scaffolds and do not perform those functions.

On Linux or macOS, install and start the dashboard:

```bash
./install.sh
./start.sh
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). The former in-memory
dashboard is available at `/prototype/` when served by this FastAPI app; the
existing `agentic-os-web` command also remains available as a separate server.
Do not run both servers on the same port. The FastAPI scaffold has no
authentication or durable storage; keep it bound to loopback and do not expose
it to an untrusted network. `HOST` and `PORT` can be set to change the bind
address and port, but changing the host does not add authentication.

`backup.sh` and `restore.sh` intentionally exit with an explicit
not-implemented status; they do not read or modify data. Runtime files under
`data/`, `audit/`, and `backups/` are ignored by Git, while
`data/agent-routes.json` is a tracked empty scaffold.

## Development

Install the package and run the test suite:

```bash
python -m pip install --editable ".[test]"
python -m unittest discover -s tests
```

GitHub Actions runs the test suite on Python 3.10, 3.12, and 3.14 for pushes
to `main`, pull requests, and version tags (`v*`). After tests pass, it builds
and uploads a wheel artifact. This provides a reproducible release artifact;
publishing or deploying to a package registry or runtime is not configured.

To build a wheel locally:

```bash
python -m pip wheel --no-deps --wheel-dir dist .
```

## License

GPL-3.0-or-later. See [LICENSE](./LICENSE).
