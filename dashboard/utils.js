export function renderPlaceholder(title, description, plannedItems = []) {
  const items = plannedItems.length
    ? `<ul class="planned-list">${plannedItems.map((item) => `<li>${item}</li>`).join("")}</ul>`
    : "";
  return `
    <div class="page-heading">
      <div>
        <div class="eyebrow">GOD AI OS · FOUNDATION SCAFFOLD</div>
        <h1>${title}</h1>
        <p>${description}</p>
      </div>
      <span class="badge badge-planned">Not implemented</span>
    </div>
    <article class="panel placeholder-panel">
      <div class="placeholder-icon" aria-hidden="true">⌁</div>
      <div>
        <h2>This module is a scaffold</h2>
        <p>The page and navigation are in place, but this feature does not yet store data or perform actions.</p>
        ${items}
      </div>
    </article>`;
}
