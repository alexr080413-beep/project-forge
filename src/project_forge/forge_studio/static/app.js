const pageTitle = document.querySelector("#page-title");
const dashboardPage = document.querySelector("#dashboard-page");
const contentPage = document.querySelector("#content-page");
const contentRoot = document.querySelector("#content-root");
let workspaceData = null;

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

function actionButton(label) {
  return `<button class="action-button" type="button">${label}</button>`;
}

function reviewActionButton(reviewId, action, label) {
  return `<button class="action-button review-action" type="button" data-review-id="${reviewId}" data-action="${action}">${label}</button>`;
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
      card(record.title || record.id, record.description || record.comments || record.item_id || "No additional details.", formatLabel(record[statusKey]))
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
  setText("#active-exercise-description", `${exercise.exercise_control} | Director: ${exercise.exercise_director} | Start ${exercise.start}`);
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
        <div class="action-row">
          ${actionButton("Open")}
          ${actionButton("Duplicate")}
          ${actionButton("Archive")}
          ${actionButton("Create Exercise")}
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
}

function renderTimeline(data) {
  contentRoot.innerHTML = `
    <section class="panel">
      <div class="panel-header">
        <h2>Operational Timeline</h2>
        <span>${data.workspace.exercise.name}</span>
      </div>
      <div class="timeline-column">
        ${data.timeline_events.map((event) => `
          <article class="timeline-card">
            <time>${timeFromIso(event.timestamp)}</time>
            <div>
              <strong>${event.title}</strong>
              <p>${event.description}</p>
              <span class="badge">${formatLabel(event.event_type)}</span>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function renderInjectLibrary(data) {
  contentRoot.innerHTML = `
    <section class="panel">
      <div class="panel-header">
        <h2>Inject Library</h2>
        <span>Human review controls release</span>
      </div>
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
              <dt>Controller</dt><dd>${inject.assigned_controller_name || inject.assigned_controller || "Unassigned"}</dd>
              <dt>Priority</dt><dd>${formatLabel(inject.priority)}</dd>
            </dl>
          </article>
        `).join("")}
      </div>
    </section>
  `;
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
                ${canReview ? `${reviewActionButton(item.id, "approve", "Approve")}${reviewActionButton(item.id, "reject", "Reject")}` : "Complete"}
              </span>
            </div>
          `;
        }).join("")}
      </div>
    </section>
  `;
  bindReviewActions();
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
        <div class="data-table">
          <div class="table-row table-head"><span>Product Type</span><span>Title</span><span>Status</span><span>Version</span><span>Last Updated</span><span>Author</span><span>Review Status</span></div>
          ${data.products.map((product) => `
            <div class="table-row">
              <span>${product.product_type}</span>
              <span>${product.title}</span>
              <span>${product.status}</span>
              <span>${product.version}</span>
              <span>${product.last_updated}</span>
              <span>${product.author}</span>
              <span>${product.review_status}</span>
            </div>
          `).join("")}
        </div>
      </article>
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

async function submitReviewDecision(reviewId, action) {
  const response = await fetch(`/api/review/${action}`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({review_id: reviewId})
  });
  if (!response.ok) {
    throw new Error("Review request failed");
  }
  workspaceData = await response.json();
  showPage("review-queue");
}

function bindReviewActions() {
  for (const button of document.querySelectorAll(".review-action")) {
    button.addEventListener("click", () => {
      submitReviewDecision(button.dataset.reviewId, button.dataset.action).catch((error) => {
        button.textContent = error.message;
      });
    });
  }
}

function showPage(page) {
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
