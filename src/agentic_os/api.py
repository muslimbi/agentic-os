from __future__ import annotations

from pathlib import Path
import sysconfig

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .core import HierarchicalAgentOS

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SOURCE_DASHBOARD_ROOT = _PROJECT_ROOT / "dashboard"
_INSTALLED_DASHBOARD_ROOT = (
    Path(sysconfig.get_path("data")) / "share" / "agentic-os" / "dashboard"
)
_DASHBOARD_ROOT = (
    _SOURCE_DASHBOARD_ROOT
    if _SOURCE_DASHBOARD_ROOT.is_dir()
    else _INSTALLED_DASHBOARD_ROOT
)
_PROTOTYPE_PAGE = Path(__file__).parent / "static" / "dashboard.html"

FEATURES = {
    "dashboard": "Overview and system status",
    "skills": "Reusable agent skill catalog",
    "memory": "Shared brain files and knowledge graph",
    "chat": "Hierarchical multi-agent chat",
    "history": "Searchable conversation history",
    "scheduler": "Scheduled jobs",
    "audit": "Activity and decision trail",
    "cost": "Model and provider cost analytics",
    "plugins": "Plugin and integration registry",
    "backups": "Backup and restore management",
    "prompts": "Reusable prompt templates",
    "standards": "Organizational coding standards",
    "settings": "System configuration",
    "setup-wizard": "Guided system setup",
    "kanban": "Mission and task board",
    "goals": "Hierarchical goals",
    "journal": "Daily agent journal",
    "agent-health": "Agent status and health",
    "smart-router": "Model and agent routing",
    "learning-analytics": "Evaluation and learning metrics",
    "session-replay": "Execution session replay",
    "errors": "Error and failure reports",
}

app = FastAPI(
    title="GOD AI OS",
    description=(
        "Local development scaffold. Most product features are not implemented."
    ),
    version="0.1.0",
)
_orchestrator = HierarchicalAgentOS()


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(_DASHBOARD_ROOT / "index.html")


@app.get("/prototype/", include_in_schema=False)
def prototype_dashboard() -> FileResponse:
    return FileResponse(_PROTOTYPE_PAGE)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "implementation": "scaffold"}


@app.get("/api/dashboard")
def agent_dashboard() -> dict[str, object]:
    return _orchestrator.dashboard()


@app.get("/api/features")
def features() -> dict[str, object]:
    return {
        "features": [
            {
                "id": feature_id,
                "name": name,
                "status": "prototype" if feature_id == "dashboard" else "not_implemented",
            }
            for feature_id, name in FEATURES.items()
        ]
    }


@app.get("/api/features/{feature_id}")
def feature_status(feature_id: str) -> dict[str, str]:
    name = FEATURES.get(feature_id)
    if name is None:
        raise HTTPException(status_code=404, detail="Unknown feature.")
    if feature_id == "dashboard":
        return {
            "id": feature_id,
            "name": name,
            "status": "prototype",
            "detail": "Displays in-memory orchestration state; it is not a production control plane.",
        }
    return {
        "id": feature_id,
        "name": name,
        "status": "not_implemented",
        "detail": "This page is a scaffold; feature behavior is not available yet.",
    }


app.mount(
    "/",
    StaticFiles(directory=_DASHBOARD_ROOT, html=True),
    name="dashboard-assets",
)
