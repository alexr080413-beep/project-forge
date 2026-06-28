const pageTitle = document.querySelector("#page-title");
const dashboardPage = document.querySelector("#dashboard-page");
const contentPage = document.querySelector("#content-page");
const contentRoot = document.querySelector("#content-root");
let workspaceData = null;
let currentPage = "dashboard";

const pageLabels = {
  dashboard: "Dashboard",
  exercises: "Exercises",
  timeline: "Timeline",
  "inject-library": "Inject Library",
  controllers: "Controllers",
  "review-queue": "Review Queue",
  "exercise-library": "Exercise Library",
  audit: "Audit",
  settings: "Settings"
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

function timeFromIso(value) {
  if (!value) {
    return "--";
  }
  const date = new Date(value);
  return date.toISOString().slice(11, 16).replace(":", "");
}

function statusClass(value) {
  return `status-${String(value || "neutral").replaceAll("_", "-").toLowerCase()}`;
}

function payloadAttr(payload) {
  return encodeURIComponent(JSON.stringify(payload));
}

function commandButton(label, action, payload = {}, variant = "") {
  return `<button class="action-button command-action ${variant}" type="button" data-action="${action}" data-payload="${payloadAttr(payload)}">${label}</button>`;
}

function formButton(label, action, formId) {
  return `<button class="action-button form-action" type="button" data-action="${action}" data-form="${formId}">${label}</button>`;
}

function card(title, body, meta = "") {
  return `
    <article class="record">
      <div class="record-title">
        <strong>${title}</strong>
        ${meta ? `<span class="badge">${meta}</span>` : ""}
      </div>
      <p>${body}</p>
    </article>
  `;
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
    container.insertAdjacentHTML(
      "beforeend",
      `<div class="activity-item"><span>${item.time}</span><strong>${item.title}</strong></div>`
    );
  }
}

function renderDashboard(data) {
  const exercise = data.workspace.exercise;
  setText("#active-exercise", exercise.name);
  setText(
    "#active-exercise-description",
    `${exercise.exercise_control} | Director: ${exercise.exercise_director} | Start ${exercise.start}`
  );
  setText("#exercise-status", data.metrics.exercise_status);
  setText("#exercise-phase", data.metrics.exercise_phase);
  setText("#exercise-health", data.metrics.exercise_health);
  setText("#controller-count", data.metrics.controller_count);
  setText("#pending-reviews", data.metrics.pending_reviews);
  setText("#open-injects", data.metrics.open_injects);
  setText("#products-generated", data.metrics.products_generated);
  setText("#current-time", data.metrics.current_operational_time);
  renderActivity(data.activity);
  renderRecords("#timeline-list", data.timeline_events.slice(-5), "No timeline events yet.");
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
          ${commandButton("Archive", "exercise.archive")}
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
        ${data.timeline_events.map((event) => `
          <article class="timeline-card">
            <time>${timeFromIso(event.timestamp)}</time>
            <div>
              <strong>${event.title}</strong>
              <p>${event.description}</p>
              <span class="badge">${formatLabel(event.event_type)}</span>
              <div class="action-row compact-actions">
                ${commandButton("Edit", "timeline.edit", {event_id: event.id, title: `${event.title} Updated`})}
                ${commandButton("Delete", "timeline.delete", {event_id: event.id}, "danger")}
              </div>
            </div>
          </article>
        `).join("")}
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
              <span class="status-badge">${formatLabel(inject.status)}</span>
            </div>
            <dl class="detail-list compact-list">
              <dt>Category</dt><dd>${formatLabel(inject.inject_type)}</dd>
              <dt>Scheduled Time</dt><dd>${timeFromIso(inject.scheduled_time)}</dd>
              <dt>Controller</dt><dd>${inject.assigned_controller_name || "Unassigned"}</dd>
              <dt>Priority</dt><dd>${formatLabel(inject.priority)}</dd>
            </dl>
            <div class="action-row compact-actions">
              ${commandButton("Edit", "inject.edit", {inject_id: inject.id, title: `${inject.title} Updated`})}
              ${commandButton("Approve", "inject.approve", {inject_id: inject.id})}
              ${commandButton("Reject", "inject.reject", {inject_id: inject.id})}
              ${commandButton("Assign", "inject.assign", {inject_id: inject.id, assigned_controller: "user-intel-chief"})}
              ${commandButton("Schedule", "inject.schedule", {inject_id: inject.id, scheduled_time: "2027-03-27T09:50:00+00:00"})}
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
      ${data.controllers.map((controller) => `
        <article class="controller-card">
          <div class="controller-avatar">${controller.role.slice(0, 2).toUpperCase()}</div>
          <div>
            <span class="card-label">${controller.role}</span>
            <h2>${controller.name}</h2>
          </div>
          <dl class="detail-list compact-list">
            <dt>Current Task</dt><dd>${controller.task}</dd>
            <dt>Current Status</dt><dd>${controller.status}</dd>
            <dt>Products Today</dt><dd>${controller.products_today}</dd>
            <dt>Pending Reviews</dt><dd>${controller.pending_reviews}</dd>
          </dl>
        </article>
      `).join("")}
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
              <span>${formatLabel(item.status)}</span>
              <span>${formatLabel(item.decision || "Pending")}</span>
              <span>${item.reviewed_by || "Unassigned"}</span>
              <span>${timeFromIso(item.timestamp)}</span>
              <span class="review-actions">
                ${canReview ? `${commandButton("Approve", "review.approve", {review_id: item.id})}${commandButton("Reject", "review.reject", {review_id: item.id})}${commandButton("Return for Revision", "review.revision", {review_id: item.id})}` : "Complete"}
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
          ${data.products.map((product) => `
            <div class="table-row">
              <span>${product.product_type}</span>
              <span>${product.title}</span>
              <span>${product.status}</span>
              <span>${product.version}</span>
              <span>${product.last_updated}</span>
              <span>${product.author}</span>
              <span>${product.review_status}</span>
              <span class="review-actions">
                ${commandButton("Open", "product.open", {product_id: product.id})}
                ${commandButton("Metadata", "product.metadata", {product_id: product.id})}
                ${commandButton("Versions", "product.version_history", {product_id: product.id})}
                ${commandButton("Archive", "product.archive", {product_id: product.id})}
                ${commandButton("Delete", "product.delete", {product_id: product.id}, "danger")}
              </span>
            </div>
          `).join("")}
        </div>
      </article>
    </section>
  `;
  bindCommandActions();
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
  if (page === "dashboard") {
    renderDashboard(workspaceData);
    return;
  }
  const renderers = {
    exercises: renderExercises,
    timeline: renderTimeline,
    "inject-library": renderInjectLibrary,
    controllers: renderControllers,
    "review-queue": renderReviewQueue,
    "exercise-library": renderExerciseLibrary,
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
  renderDashboard(workspaceData);
}

function showPage(page) {
  currentPage = page;
  for (const item of document.querySelectorAll(".nav-item")) {
    item.classList.toggle("active", item.dataset.page === page);
  }
  pageTitle.textContent = pageLabels[page] || "Dashboard";
  dashboardPage.classList.toggle("active-page", page === "dashboard");
  contentPage.classList.toggle("active-page", page !== "dashboard");
  renderPage(page);
}

for (const item of document.querySelectorAll(".nav-item")) {
  item.addEventListener("click", () => showPage(item.dataset.page));
}

loadDashboard().catch((error) => {
  setText("#active-exercise", "Dashboard unavailable");
  setText("#active-exercise-description", error.message);
});
