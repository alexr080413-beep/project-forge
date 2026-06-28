# Cards

Forge cards are bounded operational objects, not decorative content blocks.

## Card Types

| Card | Purpose |
| --- | --- |
| Controller Card | Shows role, cell, assignments, availability, and recent decisions. |
| Event Card | Summarizes exercise event status, severity, entities, timeline position, and source references. |
| Entity Card | Shows unit, organization, location, platform, relationship, or actor details. |
| Product Card | Shows product type, owner, status, QA state, review state, and source traceability. |
| Workflow Card | Shows workflow stage, last run, failure state, retry status, and audit link. |
| Review Card | Shows assignment, reviewer, QA findings, decision state, and due time. |
| Metric Card | Shows one metric with trend, timestamp, and scope. |
| Timeline Card | Shows event, inject, product, or phase marker in sequence. |
| Activity Feed Card | Shows auditable activity with actor, action, object, and timestamp. |

## Anatomy

Recommended structure:

```text
+------------------------------------------------+
| Type / ID                    Status Badge       |
| Title                                          |
| Key metadata row                              |
| Summary or operational fields                 |
| Footer: owner, timestamp, audit link, action  |
+------------------------------------------------+
```

## Visual Rules

- Use Graphite or Steel surfaces.
- Keep border radius restrained, 8px or less.
- Use a subtle border rather than heavy shadow.
- Use orange for active, selected, or attention states only.
- Keep cards compact. Use tables when users need comparison across many records.
- Do not nest cards inside cards.

## Content Rules

- Every card should answer: what is it, what state is it in, who owns it, what happens next?
- Include IDs and timestamps when traceability matters.
- Use status badges with labels, not color alone.
- Keep action buttons in predictable positions.
- Surface audit links or metadata drawers for controlled artifacts.

## Empty State

Empty card regions should state the operational condition, not teach the feature.

Use:

```text
No products awaiting review.
```

Avoid:

```text
This is where your review products will appear when you start using Forge.
```
