# Forge Studio Design System

The Forge Studio Design System is the shared visual and interaction language for every Forge Studio application. It defines reusable components, semantic tokens, accessibility requirements, and usage patterns for the current local MVP and future React desktop implementation.

Forge Studio should feel like a modern command center: dense, calm, operational, auditable, and built for repeated controller work. It should not feel like a consumer app, marketing page, or decorative dashboard.

## Foundations

### Typography

| Token | Value | Use |
| --- | --- | --- |
| `font-sans` | Inter, Segoe UI, Roboto, Arial, sans-serif | Interface text |
| `font-mono` | JetBrains Mono, SFMono-Regular, Consolas, monospace | Times, IDs, audit metadata |
| `text-xs` | 12px | Labels, badges, table metadata |
| `text-sm` | 13px | Dense cards, controls, table cells |
| `text-md` | 14px | Body text |
| `text-lg` | 16px | Panel headings |
| `text-xl` | 22-26px | Page titles |

Rules: keep letter spacing at `0`, avoid viewport-scaled type, reserve large headings for page titles, and use monospace for operational timestamps and identifiers.

### Spacing

Use an 8px base grid.

| Token | Value | Use |
| --- | --- | --- |
| `space-1` | 4px | Icon-label gaps |
| `space-2` | 8px | Compact control gaps |
| `space-3` | 12px | Card internals |
| `space-4` | 16px | Panel padding |
| `space-6` | 24px | Section spacing |
| `space-8` | 32px | Major workspace separation |

### Color Usage

| Token | Hex | Use |
| --- | --- | --- |
| Command Black | `#050608` | App background |
| Surface | `#0B0F14` | Nested controls, activity rows |
| Panel | `#111821` | Panels and cards |
| Steel | `#243140` | Borders |
| Strong Steel | `#3A4A5C` | Active borders |
| Ash | `#A9B6C3` | Secondary text |
| White | `#E6EDF3` | Primary text |
| Forge Orange | `#F6A86E` | Primary actions and active states |
| Ember | `#D9752B` | Warning and pending states |
| Success | `#54A36A` | Approved and completed states |
| Danger | `#D65A5A` | Rejected and destructive actions |
| Info | `#4EA1D3` | Informational states |

Color is never the only state indicator. Every status must include text.

## Components

The current static app exposes browser-native reusable helpers in:

```text
src/project_forge/forge_studio/static/design-system/components.js
```

The helpers are available as `window.ForgeUI`.

Shared design tokens are tracked in:

```text
design_system/tokens.json
```

### Buttons

Variants:

- Primary: dominant command.
- Secondary: routine command.
- Danger: destructive command.
- Success: approval command.
- Warning: caution or revision command.
- Ghost: low-emphasis table or card command.
- Icon: compact tool command with a symbolic label.

Usage:

```js
ForgeUI.commandButton("Approve", "review.approve", {review_id: "review-001"}, "success")
ForgeUI.formButton("Create Inject", "inject.create", "inject-form", "primary")
ForgeUI.iconButton("Archive", "product.archive", {product_id: "product-001"})
```

### Cards

Reusable card families:

- Information Card: general content with title, summary, and optional badge.
- Statistics Card: metric label and value.
- Controller Card: role, name, task, online state, product count, review count.
- Inject Card: title, status, category, controller, schedule, priority, actions.
- Timeline Event Card: time, title, description, status, tags, related object.
- Exercise Card: exercise name, status, phase, director, actions.
- Product Card: type, title, status, version, author, review status, updated time.
- Review Card: item title, decision, reviewer, timestamp, actions.

Usage:

```js
ForgeUI.card({title: "Current Weather", body: "Visibility improving.", meta: "weather"})
ForgeUI.statCard({label: "Pending Reviews", value: 3, icon: "RV"})
```

### Forms

Forms use compact field groups and visible labels or `aria-label` attributes. Required fields must be obvious in the future production UI. The current MVP uses inline forms for speed.

Usage:

```html
<form class="crud-form inline-form">
  <input name="title" aria-label="Inject title">
  <select name="assigned_controller" aria-label="Assigned controller"></select>
</form>
```

### Tables

Tables are used for audit, reviews, product library records, search results, and future entity registries.

Rules:

- Keep status columns near the left.
- Use monospace for timestamps and IDs.
- Keep actions in the rightmost column.
- Use sticky headers in future long-scroll tables.
- Support keyboard row navigation in the future React implementation.

### Navigation

The sidebar is the standard primary navigation. It supports:

- Active indicator.
- Hover and focus states.
- Future icons.
- Future collapsed mode.
- Keyboard navigation through native buttons.

Current usage:

```html
<button class="nav-item active" data-page="dashboard">Dashboard</button>
```

### Badges And Status Chips

Status chips use consistent labels and colors:

| Status | Class | Color |
| --- | --- | --- |
| Draft | `status-draft` | Neutral |
| Pending Review | `status-pending-review` | Ember |
| Approved | `status-approved` | Success |
| Scheduled | `status-scheduled` | Forge Orange |
| Active | `status-active` | Info |
| Completed | `status-completed` | Success |
| Archived | `status-archived` | Neutral |
| Rejected | `status-rejected` | Danger |

Usage:

```js
ForgeUI.statusBadge("pending_review")
```

### Alerts And Notifications

Notification variants:

- Success: action completed.
- Warning: action needs attention.
- Info: neutral system update.
- Error: failed or blocked action.

Usage:

```js
ForgeUI.notification({type: "success", title: "Inject approved", body: "Audit entry recorded."})
```

### Dialogs

Dialogs are future components. They should be used for destructive confirmation, metadata detail, version history, and complex forms. Dialogs must trap focus, close on Escape, expose accessible names, and return focus to the opening control.

### Timeline Components

Timeline cards support:

- Icon or short code.
- Time.
- Status.
- Tags.
- Related inject, product, or audit target.

Usage:

```js
ForgeUI.timelineCard({
  event: {
    title: "Weather Updated",
    description: "Visibility improving.",
    event_type: "completed"
  },
  time: "0945"
})
```

### Dashboard Widgets

Reusable dashboard widgets:

- Exercise Health.
- Controllers Online.
- Timeline.
- Pending Reviews.
- Latest Activity.
- Statistics.

Usage:

```js
ForgeUI.statCard({label: "Controllers Online", value: 6, icon: "CT"})
```

### Icons

Use short operational icon labels in the static MVP and lucide outline icons in future React surfaces. Icons should be 16px in tables, 20px in navigation and cards, and never decorative without purpose.

### Search

Search uses a compact input, filter controls, and a result table or card list. It must preserve keyboard access and support future scoped filters such as products, injects, entities, timeline, and audit.

### Command Palette

Future command palette:

- Trigger: `Ctrl+K` / `Cmd+K`.
- Scope: current exercise first.
- Actions: create inject, add timeline event, open product, assign controller, search audit.
- Must show keyboard focus, action category, and target object.
- No command executes without explicit selection.

### Empty States

Empty states should be operational, not decorative. They include a short title, a direct explanation, and one clear action.

Usage:

```js
ForgeUI.emptyState({title: "No pending reviews", body: "All review items are complete."})
```

### Loading States And Skeleton Loaders

Loading states should preserve layout dimensions to prevent page shift. Skeleton loaders use muted steel surfaces and should not animate aggressively.

Usage:

```js
ForgeUI.skeleton("card")
```

### Charts

Charts are future components. Use restrained colors, visible legends, accessible labels, and tabular fallback data. Avoid decorative gradients and overloaded dashboards.

### Maps

Maps are future components. Use dark tactical styling, clear layer controls, source labels, scale, timestamp, and keyboard-accessible layer toggles.

## Accessibility

### Color Contrast

Text and controls must meet WCAG AA contrast. Status must use text labels in addition to color.

### Keyboard Navigation

All controls must be reachable by keyboard. Native buttons and inputs are preferred in the MVP. Future dialogs and command palettes must implement focus management.

### Screen Reader Support

Use semantic headings, buttons, forms, `aria-label` where labels are visually compact, and readable status text.

### Focus States

Focus states must be visible. Forge uses high-contrast orange or steel focus borders and avoids removing outlines without replacement.

## Responsive Layout

Desktop is primary. Tablet and mobile should remain usable:

- Sidebar stacks or collapses.
- Dashboards collapse to one column.
- Tables can horizontally scroll.
- Forms wrap controls without overlap.
- Action rows wrap instead of truncating text.

## Implementation Contract

Every future Forge Studio application should reuse these primitives or their React equivalents:

- `ForgeUI.button`
- `ForgeUI.commandButton`
- `ForgeUI.formButton`
- `ForgeUI.statusBadge`
- `ForgeUI.card`
- `ForgeUI.statCard`
- `ForgeUI.dashboardWidget`
- `ForgeUI.controllerCard`
- `ForgeUI.timelineCard`
- `ForgeUI.productRow`
- `ForgeUI.notification`
- `ForgeUI.emptyState`
- `ForgeUI.skeleton`

The current MVP intentionally keeps the implementation small, static, and dependency-free.
