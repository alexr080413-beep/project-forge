const pageTitle = document.querySelector("#page-title");
const dashboardPage = document.querySelector("#dashboard-page");
const contentPage = document.querySelector("#content-page");
const contentRoot = document.querySelector("#content-root");
const navList = document.querySelector("#nav-list");
const breadcrumbs = document.querySelector("#breadcrumbs");
const organizationSelector = document.querySelector("#organization-selector");
const exerciseSelector = document.querySelector("#exercise-selector");
const exerciseStatusPill = document.querySelector("#exercise-status-pill");
const appShell = document.querySelector("#app-shell");
const modalBackdrop = document.querySelector("#modal-backdrop");
const commandPalette = document.querySelector("#command-palette");
const commandResults = document.querySelector("#command-results");
const globalSearchModal = document.querySelector("#global-search-modal");
const globalSearchResults = document.querySelector("#global-search-results");
const UI = window.ForgeUI;
let workspaceData = null;
let currentPage = "mission-control";

const pageLabels = {
  "mission-control": "Mission Control",
  timeline: "Timeline",
  intelligence: "Intelligence",
  "inject-library": "Inject Library",
  "exercise-library": "Exercise Library",
  controllers: "Controllers",
  "review-queue": "Review Queue",
  reports: "Reports",
  analytics: "Analytics",
  administration: "Administration"
};

const commandPaletteItems = [
  "Create Exercise",
  "Create Inject",
  "Open Timeline",
  "Approve Review",
  "Search Products",
  "Search Controllers",
  "Open Mission Control",
  "Settings"
];

function formatLabel(value) {
  return UI.formatLabel(value);
}

function timeFromIso(value) {
  if (!value) {
    return "--";
  }
  const date = new Date(value);
  return date.toISOString().slice(11, 16).replace(":", "");
}

function statusClass(value) {
  return UI.statusClass(value);
}

function commandButton(label, action, payload = {}, variant = "") {
  return UI.commandButton(label, action, payload, variant || "secondary");
}

function formButton(label, action, formId) {
  return UI.formButton(label, action, formId, "primary");
}

function card(title, body, meta = "") {
  return UI.card({title, body, meta});
}

function escapeHtml(value) {
  return UI.escapeHtml(value);
}

function controllerOptions(selected = "") {
  return (workspaceData?.controllers || [])
    .filter((controller) => controller.user_id)
    .map((controller) => `<option value="${controller.user_id}" ${controller.user_id === selected ? "selected" : ""}>${controller.role} - ${controller.name}</option>`)
    .join("");
}

function collectForm(formId) {
  const form = document.querySelector(`#${formId}`);
  const data = {};
  for (const [key, value] of new FormData(form).entries()) {
    if (String(value).trim()) {
      data[key] = String(value).trim();
    }
  }
  return data;
}

async function postAction(action, payload = {}, page = currentPage) {
  const response = await fetch("/api/action", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({action, payload})
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || "Action failed");
  }
  workspaceData = await response.json();
  showPage(page);
}

function renderGlobalContext(data) {
  const platform = data.platform;
  const workspaceLabel = pageLabels[currentPage] || platform.workspace;
  pageTitle.textContent = workspaceLabel;
  exerciseStatusPill.textContent = formatLabel(data.active_exercise.status);
  const currentBreadcrumbs = [
    platform.breadcrumbs[0],
    platform.breadcrumbs[1],
    platform.breadcrumbs[2],
    {label: workspaceLabel, id: currentPage}
  ];
  breadcrumbs.innerHTML = currentBreadcrumbs
    .map((item) => `<span>${escapeHtml(item.label)}</span>`)
    .join("<span>/</span>");
  organizationSelector.innerHTML = data.organizations
    .map((organization) => `<option value="${organization.id}" ${organization.id === platform.organization.id ? "selected" : ""}>${escapeHtml(organization.name)}</option>`)
    .join("");
  exerciseSelector.innerHTML = data.organization_exercises
    .map((exercise) => `<option value="${exercise.id}" ${exercise.id === data.active_exercise.id ? "selected" : ""}>${escapeHtml(exercise.name)} - ${formatLabel(exercise.status).toUpperCase()}</option>`)
    .join("");
  navList.innerHTML = platform.workspaces.map((workspace) => `
    <button class="nav-item ${workspace.id === currentPage ? "active" : ""}" data-page="${workspace.id}" title="${escapeHtml(workspace.label)}">
      <span class="nav-icon">${escapeHtml(workspace.icon)}</span>
      <span class="nav-label">${escapeHtml(workspace.label)}</span>
    </button>
  `).join("");
  bindNavigation();
}

function bindCommandActions() {
  for (const button of document.querySelectorAll(".command-action")) {
    button.addEventListener("click", () => {
      const payload = JSON.parse(decodeURIComponent(button.dataset.payload || "%7B%7D"));
      postAction(button.dataset.action, payload).catch((error) => {
        button.textContent = error.message;
      });
    });
  }
  for (const button of document.querySelectorAll(".form-action")) {
    button.addEventListener("click", () => {
      postAction(button.dataset.action, collectForm(button.dataset.form)).catch((error) => {
        button.textContent = error.message;
      });
    });
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
    container.insertAdjacentHTML(
      "beforeend",
      card(
        record.title || record.id,
        record.description || record.comments || record.item_id || "No additional details.",
        formatLabel(record[statusKey])
      )
    );
  }
}

function renderActivity(records) {
  const container = document.querySelector("#activity-list");
  container.innerHTML = "";
  for (const item of records) {
    container.insertAdjacentHTML("beforeend", UI.activityItem(item));
  }
}

function renderDashboard(data) {
  const exercise = data.workspace.exercise;
  const dashboardGrid = document.querySelector("#dashboard-grid");
  dashboardGrid.innerHTML = `
    ${UI.dashboardWidget({
      label: "Active Exercise",
      value: exercise.name,
      icon: "FX",
      body: `${exercise.exercise_control} | Director: ${exercise.exercise_director} | Start ${exercise.start}`,
      wide: true
    })}
    ${UI.dashboardWidget({label: "Exercise Status", value: data.metrics.exercise_status, icon: "ST"})}
    ${UI.dashboardWidget({label: "Exercise Phase", value: data.metrics.exercise_phase, icon: "PH"})}
    ${UI.dashboardWidget({label: "Exercise Health", value: data.metrics.exercise_health, icon: "HL"})}
    ${UI.dashboardWidget({label: "Controllers Online", value: data.metrics.controller_count, icon: "CT"})}
    ${UI.dashboardWidget({label: "Pending Reviews", value: data.metrics.pending_reviews, icon: "RV"})}
    ${UI.dashboardWidget({label: "Open Injects", value: data.metrics.open_injects, icon: "IN"})}
    ${UI.dashboardWidget({label: "Products Generated", value: data.metrics.products_generated, icon: "PR"})}
    ${UI.dashboardWidget({label: "Current Operational Time", value: data.metrics.current_operational_time, icon: "TM"})}
  `;
  renderActivity(data.activity);
  renderRecords("#timeline-list", data.timeline_events.slice(-5), "No timeline events yet.");
}

function renderMissionControl(data) {
  renderDashboard(data);
}

function renderExercises(data) {
  const exercise = data.workspace.exercise;
  contentRoot.innerHTML = `
    <section class="workspace-grid">
      <article class="workspace-hero">
        <p class="eyebrow">Exercise Workspace</p>
        <h2>${exercise.name}</h2>
        <p>${exercise.exercise_control} is running the active Exercise Control workspace for ${exercise.training_audience}.</p>
        <form id="exercise-form" class="crud-form">
          <input name="name" value="${exercise.name}" aria-label="Exercise name">
          <input name="description" value="${data.active_exercise.description || ""}" aria-label="Exercise description">
          <input name="exercise_control" value="${exercise.exercise_control}" aria-label="Exercise control">
          <input name="training_audience" value="${exercise.training_audience}" aria-label="Training audience">
        </form>
        <div class="action-row">
          ${formButton("Create Exercise", "exercise.create", "exercise-form")}
          ${formButton("Edit Exercise", "exercise.edit", "exercise-form")}
          ${commandButton("Duplicate", "exercise.duplicate")}
          ${commandButton("Archive", "exercise.archive", {}, "warning")}
          ${commandButton("Delete", "exercise.delete", {}, "danger")}
        </div>
      </article>
      <article class="panel compact">
        <h2>Exercise Overview</h2>
        <dl class="detail-list">
          <dt>Status</dt><dd>${exercise.status}</dd>
          <dt>Current Phase</dt><dd>${exercise.phase}</dd>
          <dt>Exercise Director</dt><dd>${exercise.exercise_director}</dd>
          <dt>Training Audience</dt><dd>${exercise.training_audience}</dd>
          <dt>Timeline Status</dt><dd>${exercise.timeline_status}</dd>
        </dl>
      </article>
      <article class="panel">
        <h2>Objectives</h2>
        <div class="record-list">${exercise.objectives.map((item) => card(item, "Tracked for after-action review.", "objective")).join("")}</div>
      </article>
      <article class="panel">
        <h2>Participating Units</h2>
        <div class="tag-grid">${exercise.participating_units.map((item) => `<span class="tag">${item}</span>`).join("")}</div>
      </article>
      <article class="panel wide-panel">
        <h2>Exercise Statistics</h2>
        <div class="mini-metric-grid">${exercise.statistics.map((item) => `<div class="mini-metric"><span>${item.label}</span><strong>${item.value}</strong></div>`).join("")}</div>
      </article>
    </section>
  `;
  bindCommandActions();
}

function renderTimeline(data) {
  contentRoot.innerHTML = `
    <section class="panel">
      <div class="panel-header">
        <h2>Operational Timeline</h2>
        <span>${data.workspace.exercise.name}</span>
      </div>
      <form id="timeline-form" class="crud-form inline-form">
        <input name="title" placeholder="Timeline title" aria-label="Timeline title">
        <input name="description" placeholder="Timeline description" aria-label="Timeline description">
        <input name="timestamp" placeholder="0945 or ISO time" aria-label="Timeline timestamp">
        ${formButton("Add Timeline Event", "timeline.create", "timeline-form")}
      </form>
      <div class="timeline-column">
        ${data.timeline_events.map((event) => UI.timelineCard({
          event,
          time: timeFromIso(event.timestamp),
          actions: `
            <div class="action-row compact-actions">
              ${commandButton("Edit", "timeline.edit", {event_id: event.id, title: `${event.title} Updated`})}
              ${commandButton("Delete", "timeline.delete", {event_id: event.id}, "danger")}
            </div>
          `
        })).join("")}
      </div>
    </section>
  `;
  bindCommandActions();
}

function renderInjectLibrary(data) {
  contentRoot.innerHTML = `
    <section class="panel">
      <div class="panel-header">
        <h2>Inject Library</h2>
        <span>Human review controls release</span>
      </div>
      <form id="inject-form" class="crud-form inline-form">
        <input name="title" placeholder="Inject title" aria-label="Inject title">
        <input name="description" placeholder="Inject description" aria-label="Inject description">
        <select name="assigned_controller" aria-label="Assigned controller">${controllerOptions("user-controller")}</select>
        ${formButton("Create Inject", "inject.create", "inject-form")}
      </form>
      <div class="inject-grid">
        ${data.injects.map((inject) => `
          <article class="inject-card ${statusClass(inject.status)}">
            <div class="record-title">
              <strong>${inject.title}</strong>
              ${UI.statusBadge(inject.status)}
            </div>
            <dl class="detail-list compact-list">
              <dt>Category</dt><dd>${formatLabel(inject.inject_type)}</dd>
              <dt>Scheduled Time</dt><dd>${timeFromIso(inject.scheduled_time)}</dd>
              <dt>Controller</dt><dd>${inject.assigned_controller_name || "Unassigned"}</dd>
              <dt>Priority</dt><dd>${formatLabel(inject.priority)}</dd>
            </dl>
            <div class="action-row compact-actions">
              ${commandButton("Edit", "inject.edit", {inject_id: inject.id, title: `${inject.title} Updated`})}
              ${commandButton("Approve", "inject.approve", {inject_id: inject.id}, "success")}
              ${commandButton("Reject", "inject.reject", {inject_id: inject.id}, "danger")}
              ${commandButton("Assign", "inject.assign", {inject_id: inject.id, assigned_controller: "user-intel-chief"})}
              ${commandButton("Schedule", "inject.schedule", {inject_id: inject.id, scheduled_time: "2027-03-27T09:50:00+00:00"}, "warning")}
              ${commandButton("Delete", "inject.delete", {inject_id: inject.id}, "danger")}
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
  bindCommandActions();
}

function renderControllers(data) {
  contentRoot.innerHTML = `
    <section class="controller-grid">
      ${data.controllers.map((controller) => UI.controllerCard(controller)).join("")}
    </section>
  `;
}

function renderIntelligence(data) {
  contentRoot.innerHTML = `
    <section class="workspace-grid">
      <article class="workspace-hero">
        <p class="eyebrow">Intelligence Workspace</p>
        <h2>${data.workspace.exercise.name}</h2>
        <p>Scenario translation, source traceability, and product recommendations for the selected exercise.</p>
      </article>
      <article class="panel">
        <h2>Current Intelligence Picture</h2>
        <div class="record-list">
          ${card("Priority Requirement", "Track route disruption, civilian activity, and weather effects against current objectives.", "intel")}
          ${card("Knowledge Lookup", "Mountain terrain, local infrastructure, and notional actors are scoped to this exercise.", "knowledge")}
        </div>
      </article>
      <article class="panel">
        <h2>Recommended Products</h2>
        <div class="record-list">
          ${data.products.slice(0, 3).map((product) => card(product.title, `${product.product_type} | ${product.review_status}`, product.status)).join("")}
        </div>
      </article>
      <article class="panel wide-panel">
        <h2>Incoming Exercise Signals</h2>
        <div class="timeline-column">
          ${data.timeline_events.slice(0, 4).map((event) => UI.timelineCard({event, time: timeFromIso(event.timestamp)})).join("")}
        </div>
      </article>
    </section>
  `;
}

function renderReviewQueue(data) {
  contentRoot.innerHTML = `
    <section class="panel wide-panel">
      <div class="panel-header">
        <h2>Human Review Queue</h2>
        <span>Approval is required before release</span>
      </div>
      <div class="data-table review-table">
        <div class="table-row table-head"><span>Item</span><span>Status</span><span>Decision</span><span>Reviewed By</span><span>Timestamp</span><span>Action</span></div>
        ${data.review_queue.map((item) => {
          const canReview = item.status === "pending" || item.status === "in_review";
          return `
            <div class="table-row">
              <span>${item.title}</span>
              <span>${UI.statusBadge(item.status)}</span>
              <span>${UI.statusBadge(item.decision || "Pending")}</span>
              <span>${item.reviewed_by || "Unassigned"}</span>
              <span>${timeFromIso(item.timestamp)}</span>
              <span class="review-actions">
                ${canReview ? `${commandButton("Approve", "review.approve", {review_id: item.id}, "success")}${commandButton("Reject", "review.reject", {review_id: item.id}, "danger")}${commandButton("Return for Revision", "review.revision", {review_id: item.id}, "warning")}` : "Complete"}
              </span>
            </div>
          `;
        }).join("")}
      </div>
    </section>
  `;
  bindCommandActions();
}

function renderExerciseLibrary(data) {
  contentRoot.innerHTML = `
    <section class="workspace-grid">
      <article class="workspace-hero">
        <p class="eyebrow">Historical Repository</p>
        <h2>Exercise Library</h2>
        <p>The Exercise Library is the archive for every product generated during ${data.workspace.exercise.name}.</p>
      </article>
      <article class="panel wide-panel">
        <h2>Folders</h2>
        <div class="folder-grid">${data.workspace.library_folders.map((folder) => `<div class="folder-card"><span class="folder-icon">FD</span>${folder}</div>`).join("")}</div>
      </article>
      <article class="panel wide-panel">
        <h2>Generated Products</h2>
        <div class="data-table product-table">
          <div class="table-row table-head"><span>Product Type</span><span>Title</span><span>Status</span><span>Version</span><span>Last Updated</span><span>Author</span><span>Review Status</span><span>Action</span></div>
          ${data.products.map((product) => UI.productRow(
            product,
            `
              ${commandButton("Open", "product.open", {product_id: product.id}, "ghost")}
              ${commandButton("Metadata", "product.metadata", {product_id: product.id}, "ghost")}
              ${commandButton("Versions", "product.version_history", {product_id: product.id}, "ghost")}
              ${commandButton("Archive", "product.archive", {product_id: product.id}, "warning")}
              ${commandButton("Delete", "product.delete", {product_id: product.id}, "danger")}
            `
          )).join("")}
        </div>
      </article>
    </section>
  `;
  bindCommandActions();
}

function renderReports(data) {
  contentRoot.innerHTML = `
    <section class="panel wide-panel">
      <div class="panel-header">
        <h2>Reports</h2>
        <span>Exercise reporting framework</span>
      </div>
      <div class="mini-metric-grid">
        ${UI.statCard({label: "Products Generated", value: data.metrics.products_generated, icon: "PR"})}
        ${UI.statCard({label: "Pending Reviews", value: data.metrics.pending_reviews, icon: "RV"})}
        ${UI.statCard({label: "Timeline Events", value: data.metrics.timeline_events, icon: "TL"})}
      </div>
      <div class="record-list report-list">
        ${card("Daily Controller Summary", "Draft reporting surface for EXCON daily update material.", "report")}
        ${card("After Action Export", "Future package for objective coverage, review latency, and product history.", "future")}
      </div>
    </section>
  `;
}

function renderAnalytics(data) {
  contentRoot.innerHTML = `
    <section class="workspace-grid">
      <article class="workspace-hero">
        <p class="eyebrow">Analytics</p>
        <h2>Exercise Metrics</h2>
        <p>Operational analytics for ${data.workspace.exercise.name}, calculated from the shared Exercise Data Engine.</p>
      </article>
      <article class="panel wide-panel">
        <h2>Metrics Snapshot</h2>
        <div class="mini-metric-grid">
          ${Object.entries(data.statistics).map(([label, value]) => `<div class="mini-metric"><span>${formatLabel(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}
        </div>
      </article>
      <article class="panel">
        <h2>Review Pressure</h2>
        ${UI.notification({type: data.metrics.pending_reviews ? "warning" : "success", title: `${data.metrics.pending_reviews} pending reviews`, body: "Human review remains the release gate."})}
      </article>
      <article class="panel">
        <h2>Controller Health</h2>
        ${UI.notification({type: "info", title: `${data.metrics.controller_count} controllers online`, body: "Controller status is scoped to the selected exercise."})}
      </article>
    </section>
  `;
}

function renderAdministration(data) {
  contentRoot.innerHTML = `
    <section class="settings-grid">
      <article class="settings-card">
        <span class="card-icon">OR</span>
        <h2>Organization</h2>
        <p>${data.platform.organization.name}</p>
      </article>
      ${data.workspace.settings.map((item) => `
        <article class="settings-card">
          <span class="card-icon">${item.title.slice(0, 2).toUpperCase()}</span>
          <h2>${item.title}</h2>
          <p>${item.description}</p>
        </article>
      `).join("")}
    </section>
  `;
}

function renderAudit(data) {
  contentRoot.innerHTML = `
    <section class="panel wide-panel">
      <div class="panel-header">
        <h2>Audit History</h2>
        <span>Every mock operation records a trace</span>
      </div>
      <div class="data-table audit-table">
        <div class="table-row table-head"><span>Timestamp</span><span>Actor</span><span>Action</span><span>Target</span><span>Result</span></div>
        ${data.audit_log.map((item) => `
          <div class="table-row">
            <span>${timeFromIso(item.timestamp)}</span>
            <span>${item.actor}</span>
            <span>${item.action}</span>
            <span>${item.target}</span>
            <span>${formatLabel(item.result)}</span>
          </div>
        `).join("")}
      </div>
    </section>
  `;
}

function renderSettings(data) {
  contentRoot.innerHTML = `
    <section class="settings-grid">
      ${data.workspace.settings.map((item) => `
        <article class="settings-card">
          <span class="card-icon">${item.title.slice(0, 2).toUpperCase()}</span>
          <h2>${item.title}</h2>
          <p>${item.description}</p>
        </article>
      `).join("")}
    </section>
  `;
}

function renderPage(page) {
  if (!workspaceData) {
    return;
  }
  renderGlobalContext(workspaceData);
  if (page === "mission-control") {
    renderMissionControl(workspaceData);
    return;
  }
  const renderers = {
    timeline: renderTimeline,
    intelligence: renderIntelligence,
    "inject-library": renderInjectLibrary,
    "exercise-library": renderExerciseLibrary,
    controllers: renderControllers,
    "review-queue": renderReviewQueue,
    reports: renderReports,
    analytics: renderAnalytics,
    administration: renderAdministration,
    exercises: renderExercises,
    audit: renderAudit,
    settings: renderSettings
  };
  (renderers[page] || renderDashboard)(workspaceData);
}

async function loadDashboard() {
  const response = await fetch("/api/exercise");
  if (!response.ok) {
    throw new Error("Dashboard request failed");
  }
  workspaceData = await response.json();
  showPage(currentPage);
}

function showPage(page) {
  currentPage = page;
  renderGlobalContext(workspaceData);
  dashboardPage.classList.toggle("active-page", page === "mission-control");
  contentPage.classList.toggle("active-page", page !== "mission-control");
  renderPage(page);
}

function bindNavigation() {
  for (const item of document.querySelectorAll(".nav-item")) {
    item.addEventListener("click", () => showPage(item.dataset.page));
  }
}

function renderCommandPalette(filter = "") {
  const normalized = filter.toLowerCase();
  commandResults.innerHTML = commandPaletteItems
    .filter((item) => item.toLowerCase().includes(normalized))
    .map((item) => `<button class="modal-result" type="button">${escapeHtml(item)}</button>`)
    .join("");
}

function renderGlobalSearch(filter = "") {
  const normalized = filter.toLowerCase();
  globalSearchResults.innerHTML = (workspaceData?.search_results || [])
    .filter((item) => `${item.type} ${item.title} ${item.context}`.toLowerCase().includes(normalized))
    .map((item) => `
      <button class="modal-result" type="button">
        <span>${escapeHtml(item.type)}</span>
        <strong>${escapeHtml(item.title)}</strong>
        <small>${escapeHtml(item.context)}</small>
      </button>
    `)
    .join("");
}

function openModal(modal) {
  modalBackdrop.hidden = false;
  commandPalette.hidden = modal !== commandPalette;
  globalSearchModal.hidden = modal !== globalSearchModal;
  if (modal === commandPalette) {
    renderCommandPalette();
    document.querySelector("#command-input").focus();
  } else {
    renderGlobalSearch();
    document.querySelector("#global-search-input").focus();
  }
}

function closeModal() {
  modalBackdrop.hidden = true;
  commandPalette.hidden = true;
  globalSearchModal.hidden = true;
}

organizationSelector.addEventListener("change", () => {
  postAction("context.switch_organization", {organization_id: organizationSelector.value});
});

exerciseSelector.addEventListener("change", () => {
  postAction("context.switch_exercise", {exercise_id: exerciseSelector.value});
});

document.querySelector("#sidebar-toggle").addEventListener("click", () => {
  appShell.classList.toggle("sidebar-collapsed");
});

document.querySelector("#global-search-button").addEventListener("click", () => {
  openModal(globalSearchModal);
});

document.querySelector("#command-input").addEventListener("input", (event) => {
  renderCommandPalette(event.target.value);
});

document.querySelector("#global-search-input").addEventListener("input", (event) => {
  renderGlobalSearch(event.target.value);
});

for (const item of document.querySelectorAll("[data-close-modal]")) {
  item.addEventListener("click", closeModal);
}

document.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    openModal(commandPalette);
  }
  if (event.key === "Escape" && !modalBackdrop.hidden) {
    closeModal();
  }
});

loadDashboard().catch((error) => {
  const dashboardGrid = document.querySelector("#dashboard-grid");
  dashboardGrid.innerHTML = UI.notification({
    type: "error",
    title: "Dashboard unavailable",
    body: error.message
  });
});
