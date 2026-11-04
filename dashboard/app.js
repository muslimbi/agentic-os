import { api } from "./api.js";

const pages = [
  ["dashboard", "Overview"],
  ["skills", "Skills"],
  ["memory", "Memory"],
  ["chat", "Chat"],
  ["history", "History"],
  ["scheduler", "Scheduler"],
  ["audit", "Audit"],
  ["cost", "Cost analytics"],
  ["plugins", "Plugins"],
  ["backups", "Backups"],
  ["prompts", "Prompts"],
  ["standards", "Standards"],
  ["settings", "Settings"],
  ["setup-wizard", "Setup wizard"],
  ["kanban", "Kanban"],
  ["goals", "Goals"],
  ["journal", "Journal"],
  ["agent-health", "Agent health"],
  ["smart-router", "Smart router"],
  ["learning-analytics", "Learning analytics"],
  ["session-replay", "Session replay"],
  ["errors", "Errors"],
];

const navigation = document.querySelector("#navigation");
const content = document.querySelector("#page-content");
const title = document.querySelector("#page-title");
const sidebar = document.querySelector("#sidebar");

navigation.innerHTML = pages
  .map(([id, label]) => `<a class="nav-link" href="#${id}" data-page="${id}"><span class="nav-icon">${label.slice(0, 1)}</span>${label}</a>`)
  .join("");

async function renderRoute() {
  const requested = location.hash.slice(1) || "dashboard";
  const pageId = pages.some(([id]) => id === requested) ? requested : "dashboard";
  const label = pages.find(([id]) => id === pageId)[1];
  title.textContent = label;
  navigation.querySelectorAll(".nav-link").forEach((link) => {
    const active = link.dataset.page === pageId;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  sidebar.classList.remove("open");
  document.querySelector("#sidebar-backdrop").classList.remove("visible");

  try {
    const module = await import(`./pages/${pageId}.js`);
    content.innerHTML = await module.render();
  } catch (error) {
    content.innerHTML = `<section class="panel error-panel"><h1>Page unavailable</h1><p>${error.message}</p></section>`;
  }
}

async function updateApiStatus() {
  const indicator = document.querySelector("#api-status");
  try {
    await api.health();
    indicator.innerHTML = "<i></i>API online";
    indicator.classList.add("online");
  } catch {
    indicator.innerHTML = "<i></i>API unavailable";
    indicator.classList.remove("online");
  }
}

document.querySelector("#theme-toggle").addEventListener("click", () => {
  const root = document.documentElement;
  root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("god-ai-os-theme", root.dataset.theme);
});
document.querySelector("#menu-toggle").addEventListener("click", () => {
  sidebar.classList.toggle("open");
  document.querySelector("#sidebar-backdrop").classList.toggle("visible");
});
document.querySelector("#sidebar-backdrop").addEventListener("click", () => {
  sidebar.classList.remove("open");
  document.querySelector("#sidebar-backdrop").classList.remove("visible");
});
window.addEventListener("hashchange", renderRoute);
document.documentElement.dataset.theme = localStorage.getItem("god-ai-os-theme") || "dark";
renderRoute();
updateApiStatus();
