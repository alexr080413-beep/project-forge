(function () {
  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function formatLabel(value) {
    return String(value || "--").replaceAll("_", " ");
  }

  function statusClass(value) {
    return `status-${String(value || "neutral").replaceAll("_", "-").toLowerCase()}`;
  }

  function payloadAttr(payload) {
    return encodeURIComponent(JSON.stringify(payload || {}));
  }

  function button({label, variant = "secondary", classes = "", attributes = ""}) {
    return `<button class="fs-button fs-button--${variant} ${classes}" type="button" ${attributes}>${escapeHtml(label)}</button>`;
  }

  function commandButton(label, action, payload = {}, variant = "secondary") {
    return button({
      label,
      variant,
      classes: "command-action",
      attributes: `data-action="${escapeHtml(action)}" data-payload="${payloadAttr(payload)}"`
    });
  }

  function formButton(label, action, formId, variant = "primary") {
    return button({
      label,
      variant,
      classes: "form-action",
      attributes: `data-action="${escapeHtml(action)}" data-form="${escapeHtml(formId)}"`
    });
  }

  function iconButton(label, action, payload = {}, icon = label.slice(0, 2), variant = "icon") {
    return button({
      label: `${icon} ${label}`,
      variant,
      classes: "command-action",
      attributes: `data-action="${escapeHtml(action)}" data-payload="${payloadAttr(payload)}"`
    });
  }

  function statusBadge(status) {
    return `<span class="status-badge ${statusClass(status)}">${escapeHtml(formatLabel(status))}</span>`;
  }

  function card({title, body, meta = "", kind = "information"}) {
    return `
      <article class="record fs-card fs-card--${escapeHtml(kind)}">
        <div class="record-title">
          <strong>${escapeHtml(title)}</strong>
          ${meta ? `<span class="badge">${escapeHtml(formatLabel(meta))}</span>` : ""}
        </div>
        <p>${escapeHtml(body)}</p>
      </article>
    `;
  }

  function statCard({label, value, icon = "ST", wide = false}) {
    return `
      <article class="summary-card fs-widget ${wide ? "wide" : ""}">
        <span class="card-icon">${escapeHtml(icon)}</span>
        <span class="card-label">${escapeHtml(label)}</span>
        <strong>${escapeHtml(value)}</strong>
      </article>
    `;
  }

  function dashboardWidget({label, value, icon = "ST", body = "", wide = false}) {
    return `
      <article class="summary-card fs-widget ${wide ? "wide" : ""}">
        <span class="card-icon">${escapeHtml(icon)}</span>
        <span class="card-label">${escapeHtml(label)}</span>
        ${body ? `<h2>${escapeHtml(value)}</h2><p>${escapeHtml(body)}</p>` : `<strong>${escapeHtml(value)}</strong>`}
      </article>
    `;
  }

  function activityItem({time, title}) {
    return `<div class="activity-item"><span>${escapeHtml(time)}</span><strong>${escapeHtml(title)}</strong></div>`;
  }

  function controllerCard(controller) {
    return `
      <article class="controller-card fs-card fs-card--controller">
        <div class="controller-avatar">${escapeHtml(controller.role.slice(0, 2).toUpperCase())}</div>
        <div>
          <span class="card-label">${escapeHtml(controller.role)}</span>
          <h2>${escapeHtml(controller.name)}</h2>
        </div>
        <dl class="detail-list compact-list">
          <dt>Current Task</dt><dd>${escapeHtml(controller.task)}</dd>
          <dt>Current Status</dt><dd>${escapeHtml(controller.status)}</dd>
          <dt>Products Today</dt><dd>${escapeHtml(controller.products_today)}</dd>
          <dt>Pending Reviews</dt><dd>${escapeHtml(controller.pending_reviews)}</dd>
        </dl>
      </article>
    `;
  }

  function timelineCard({event, time, actions = ""}) {
    return `
      <article class="timeline-card fs-card fs-card--timeline ${statusClass(event.event_type)}">
        <time>${escapeHtml(time)}</time>
        <div>
          <strong>${escapeHtml(event.title)}</strong>
          <p>${escapeHtml(event.description)}</p>
          ${statusBadge(event.event_type)}
          ${event.related_inject_id ? `<span class="badge">rel ${escapeHtml(event.related_inject_id)}</span>` : ""}
          ${actions}
        </div>
      </article>
    `;
  }

  function notification({type = "info", title, body}) {
    return `
      <div class="fs-notification fs-notification--${escapeHtml(type)}" role="status">
        <strong>${escapeHtml(title)}</strong>
        <span>${escapeHtml(body)}</span>
      </div>
    `;
  }

  function emptyState({title, body, action = ""}) {
    return `
      <section class="fs-empty">
        <h2>${escapeHtml(title)}</h2>
        <p>${escapeHtml(body)}</p>
        ${action}
      </section>
    `;
  }

  function skeleton(kind = "card") {
    return `<div class="fs-skeleton fs-skeleton--${escapeHtml(kind)}" aria-hidden="true"></div>`;
  }

  function productRow(product, actions = "") {
    return `
      <div class="table-row">
        <span>${escapeHtml(product.product_type)}</span>
        <span>${escapeHtml(product.title)}</span>
        <span>${statusBadge(product.status)}</span>
        <span>${escapeHtml(product.version)}</span>
        <span>${escapeHtml(product.last_updated)}</span>
        <span>${escapeHtml(product.author)}</span>
        <span>${statusBadge(product.review_status)}</span>
        <span class="review-actions">${actions}</span>
      </div>
    `;
  }

  window.ForgeUI = {
    activityItem,
    button,
    card,
    commandButton,
    controllerCard,
    dashboardWidget,
    emptyState,
    escapeHtml,
    formButton,
    formatLabel,
    iconButton,
    notification,
    payloadAttr,
    productRow,
    skeleton,
    statCard,
    statusBadge,
    statusClass,
    timelineCard
  };
})();
