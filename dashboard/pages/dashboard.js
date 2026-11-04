import { api } from "../api.js";
import { renderPlaceholder } from "../utils.js";

export async function render() {
  try {
    const [data, capabilities] = await Promise.all([api.dashboard(), api.features()]);
    const agents = data.agents?.length ?? 0;
    const companies = data.companies?.length ?? 0;
    const planned = capabilities.features.filter((feature) => feature.status === "not_implemented").length;
    return `
      <div class="page-heading">
        <div><div class="eyebrow">GOD AI OS · MISSION CONTROL</div><h1>System overview</h1>
        <p>A starting point for the human-governed agent operating system.</p></div>
        <span class="badge badge-planned">Foundation scaffold</span>
      </div>
      <div class="notice">This dashboard is not an operational control plane. Most modules are placeholders; there is no authentication, durable storage, or AI provider connected.</div>
      <div class="overview-grid">
        <article class="panel stat-card"><div class="stat-label">Prototype agents</div><div class="stat-value">${agents}</div><div class="stat-note">In-memory hierarchy</div></article>
        <article class="panel stat-card"><div class="stat-label">Prototype companies</div><div class="stat-value">${companies}</div><div class="stat-note">Resets when the process stops</div></article>
        <article class="panel stat-card"><div class="stat-label">Planned modules</div><div class="stat-value">${planned}</div><div class="stat-note">Scaffolded, not implemented</div></article>
      </div>
      <article class="panel hierarchy-box"><h2>Governance direction</h2>
        <div class="hierarchy-chain">Root User → Father → Mother → Children → Sub-Children → Specialized Workers</div>
        <p class="stat-note">Instructions flow down; reports flow up. The current prototype's company hierarchy is not yet reconciled with this target.</p>
      </article>`;
  } catch {
    return renderPlaceholder("System overview", "The dashboard API is currently unavailable.", ["Start the local FastAPI server to view in-memory prototype status."]);
  }
}
