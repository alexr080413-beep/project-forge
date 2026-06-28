# Buttons

Forge buttons should be compact, clear, and operational. They should support fast controller action without hiding the consequence of the action.

## Button Types

| Type | Use | Visual Direction |
| --- | --- | --- |
| Primary | Main constructive action on a screen. | Forge Orange fill or strong orange outline on dark surfaces. |
| Secondary | Common non-destructive actions. | Steel surface, Ash text, subtle border. |
| Tertiary | Low-emphasis actions in dense toolbars. | Text or icon button with visible hover/focus state. |
| Critical | Destructive, rejecting, blocking, or escalation actions. | Strong label, icon, confirmation where appropriate. |
| Icon | Common tools such as search, filter, refresh, assign, archive. | Outline icon, tooltip, stable square hit area. |

## Label Rules

Use direct verbs:

- Approve
- Reject
- Request Revision
- Assign
- Start Dry-Run
- Open Timeline
- Add Event
- Create Product
- Archive Exercise

Avoid vague labels:

- Go
- Submit
- Magic
- Process
- Next

## Interaction States

| State | Requirement |
| --- | --- |
| Default | Clear label, sufficient contrast, stable width. |
| Hover | Slight border or surface change. Do not animate dramatically. |
| Focus | Visible keyboard focus ring. |
| Disabled | Lower contrast, explanation available when action is gated. |
| Loading | Preserve button size and show progress label or spinner. |
| Confirming | Use explicit confirmation for release, archive, rejection, or phase transition. |

## Accessibility

- Minimum hit target: 36px for dense desktop UI, 44px for touch surfaces.
- Do not use orange text on Graphite for long labels unless contrast is verified.
- Pair icon-only buttons with accessible labels and tooltips.
- Keep destructive actions visually distinct from primary constructive actions.
