# Dashboards

Forge dashboards should look like operations-center work surfaces, not business analytics pages.

## Dashboard Principles

- Lead with exercise status, timeline, review pressure, active events, and controller health.
- Keep widgets dense, readable, and role-aware.
- Use tables, queues, and timelines for operational work.
- Use metrics to support decisions, not to decorate the page.
- Make refresh state and data recency visible.
- Keep audit and drill-down paths close to the data.

## Mission Control Layout

```text
+--------------------------------------------------------------------------------+
| Forge | Exercise | Day | Phase | Profile | Search | Alerts | User              |
+--------------------------------------------------------------------------------+
| Exercise Status | Timeline | Active Controllers | Review Queue | Alerts        |
+--------------------------------------------------------------------------------+
| Active Events                 | Products Today              | Metrics Snapshot |
+--------------------------------------------------------------------------------+
| AI Activity | Controller Health | Recent Activity Feed                       |
+--------------------------------------------------------------------------------+
```

## Required Dashboard Widgets

| Widget | Purpose |
| --- | --- |
| Exercise Status | Current day, phase, tempo, escalation, readiness, and operating status. |
| Operational Timeline | Current phase, active events, upcoming injects, and major milestones. |
| Active Controllers | Controller availability, assigned work, and cell status. |
| Review Queue | Pending approvals, overdue reviews, QA findings, and assignment state. |
| Products Generated Today | Draft, QA, review, approved, rejected, and distribution counts. |
| Pending Approvals | Items requiring human authority. |
| Active Events | Event severity, status, entities, and timeline position. |
| AI Activity | Stub or provider activity, bounded reasoning requests, and confidence metadata. |
| Controller Health | Workload, queue pressure, latency, and blocked items. |
| Alerts | Critical issues, failed dry-runs, denied actions, and scenario risk. |
| Metrics | Throughput, QA pass rate, review latency, search requests, distribution activity. |
| Recent Activity Feed | Audit-ready actions by controllers and system actors. |

## Timeline Guidance

- Show exercise day, phase, and event sequence.
- Distinguish planned, active, paused, completed, and assessed items.
- Link timeline items to events, products, decisions, and reviews.
- Use orange sparingly for current time, active event, or selected phase.

## Table Guidance

- Use tables for queues, products, events, review items, entities, and audit records.
- Keep columns stable.
- Include status, owner, updated time, and action column when applicable.
- Support filtering by exercise phase, controller, status, product type, severity, and review state.

## Status Badge Guidance

Status badges should include text and a visual cue.

Examples:

- Active
- Pending Review
- QA Failed
- Approved
- Rejected
- Distribution Staged
- Archived

## Notification Guidance

- Notifications should be tied to objects: event, product, review item, workflow, profile, or exercise phase.
- Critical notifications should include the reason and next action.
- Routine notifications should not interrupt controller flow.
- Notification history should be searchable through audit or activity feed.

## Review Queue Guidance

Review queues should prioritize:

- Critical scenario risk
- Due time
- Product type
- Assigned reviewer
- QA failure count
- Exercise objective relevance

Each review item should expose source traceability, scenario context, QA findings, comments, decision history, and audit metadata.
