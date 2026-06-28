const pageTitle = document.querySelector("#page-title");
const dashboardPage = document.querySelector("#dashboard-page");
const placeholderPage = document.querySelector("#placeholder-page");
const placeholderTitle = document.querySelector("#placeholder-title");
const placeholderCopy = document.querySelector("#placeholder-copy");

const pageCopy = {
  exercises: "Exercise workspace management will connect to the Forge Studio Exercise model.",
  timeline: "The operational timeline will show phase changes, injects, review activity, and audit-ready records.",
  "inject-library": "The inject library will organize draft, reviewed, approved, and scheduled injects.",
  controllers: "Controller workspaces will show assignments, roles, workload, and review authority.",
  reports: "Reports will surface controlled products, assessment snapshots, and after-action material.",
  settings: "Settings will expose profiles, role policy, plugins, and local configuration."
};

function formatLabel(value) {
  return String(value || "--").replaceAll("_", " ");
}

function setText(id, value) {
  const element = document.querySelector(id);
  if (element) {
    element.textContent = value;
  }
}

function renderRecords(containerId, records, emptyText, statusKey = "event_type") {
  const container = document.querySelector(containerId);
  container.innerHTML = "";
  if (!records.length) {
    const empty = document.createElement("p");
    empty.textContent = emptyText;
    container.append(empty);
    return;
  }
  for (const record of records) {
    const item = document.createElement("article");
    item.className = "record";
    const title = document.createElement("div");
    title.className = "record-title";
    title.innerHTML = `<strong>${record.title || record.id}</strong><span class="badge">${formatLabel(record[statusKey])}</span>`;
    const description = document.createElement("p");
    description.textContent = record.description || record.comments || record.item_id || "No additional details.";
    item.append(title, description);
    container.append(item);
  }
}

async function loadDashboard() {
  const response = await fetch("/api/dashboard");
  if (!response.ok) {
    throw new Error("Dashboard request failed");
  }
  const data = await response.json();
  const exercise = data.active_exercise;
  setText("#active-exercise", exercise?.name || "No active exercise");
  setText("#active-exercise-description", exercise?.description || "No exercise selected.");
  setText("#exercise-status", formatLabel(data.metrics.exercise_status));
  setText("#exercise-phase", formatLabel(data.metrics.exercise_phase));
  setText("#pending-reviews", data.metrics.pending_reviews);
  setText("#active-injects", data.metrics.active_injects);
  setText("#timeline-count", data.metrics.timeline_events);
  setText("#controller-count", data.metrics.controller_count);
  renderRecords("#timeline-list", data.timeline_summary, "No timeline events yet.");
  renderRecords("#review-list", data.pending_reviews, "No pending review items.", "status");
}

function showPage(page) {
  for (const item of document.querySelectorAll(".nav-item")) {
    item.classList.toggle("active", item.dataset.page === page);
  }
  const label = document.querySelector(`.nav-item[data-page="${page}"]`)?.textContent || "Dashboard";
  pageTitle.textContent = label;
  if (page === "dashboard") {
    dashboardPage.classList.add("active-page");
    placeholderPage.classList.remove("active-page");
    return;
  }
  dashboardPage.classList.remove("active-page");
  placeholderPage.classList.add("active-page");
  placeholderTitle.textContent = label;
  placeholderCopy.textContent = pageCopy[page] || "This section is scaffolded for a future Forge Studio sprint.";
}

for (const item of document.querySelectorAll(".nav-item")) {
  item.addEventListener("click", () => showPage(item.dataset.page));
}

loadDashboard().catch((error) => {
  setText("#active-exercise", "Dashboard unavailable");
  setText("#active-exercise-description", error.message);
});
