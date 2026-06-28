# UI Brand Guidance

Forge UI should resemble a modern exercise control room: dense, calm, operational, and auditable.

This guidance supports Forge Studio, GitHub Pages visuals, demo mockups, and future product surfaces. It does not implement a frontend.

## Visual Style

| Area | Direction |
| --- | --- |
| Surfaces | Dark graphite and steel panels on black base backgrounds. |
| Accent | Forge Orange for selected, active, and high-value states. |
| Density | Information-dense but structured, with clear hierarchy. |
| Controls | Compact, predictable, keyboard-friendly. |
| Data | Tables, timelines, queues, metrics, and audit records should be first-class. |
| Tone | Command-center, military-enterprise, not consumer SaaS. |

## Components Covered

- [Buttons](buttons.md)
- [Cards](cards.md)
- [Dashboards](dashboard.md)

## Required UI Patterns

- Buttons
- Cards
- Dashboards
- Timelines
- Tables
- Status badges
- Notifications
- Review queues

## Shared Rules

- Never rely on color alone for status.
- Keep action labels explicit: Approve, Reject, Request Revision, Assign, Archive.
- Surface exercise context: exercise name, day, phase, profile, tempo, and review pressure.
- Keep audit metadata reachable from product, event, workflow, and review views.
- Avoid decorative UI that competes with operational data.
- Do not place cards inside other cards.
- Use tables for comparison and repeated operational records.
- Use timeline layouts for exercise phase, event, inject, and product sequencing.

## Status Language

| State | Label Examples | Visual Direction |
| --- | --- | --- |
| Active | Active, Running, In Progress | Orange border or icon, clear label. |
| Pending | Pending Review, Awaiting Approval | Ember or Ash, clock icon, queue position. |
| Approved | Approved, Ready | High-contrast label and check icon. |
| Rejected | Rejected, Returned | Strong label and reason visible. |
| Draft | Draft, Staged | Neutral Ash label. |
| Critical | Critical, Blocking | Strong status treatment, icon, and text. |

## Notification Categories

| Category | Use |
| --- | --- |
| Review | Assignment, approval request, rejection, revision request. |
| Timeline | Phase change, event update, inject scheduled, execution pause. |
| QA | Missing metadata, source traceability gap, fiction boundary warning. |
| System | Workflow completed, dry-run failed, service health issue. |
| Audit | Configuration change, profile activation, role decision, distribution action. |
