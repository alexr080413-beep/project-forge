# Request For Comments Process

RFCs are used for major Forge proposals before implementation.

## When To Use An RFC

Use an RFC for changes that affect:

- Platform direction.
- Major workflows.
- Service boundaries.
- Data models.
- Plugin architecture.
- Security or governance posture.
- User experience patterns.
- Release strategy.

## Proposal Lifecycle

| Status | Meaning |
| --- | --- |
| Draft | Proposal is being written and shaped. |
| Review | Proposal is ready for structured feedback. |
| Accepted | Proposal is approved for implementation. |
| Implemented | Accepted proposal has shipped or landed. |
| Rejected | Proposal will not move forward in its current form. |

## RFC Naming

Use this pattern:

```text
RFC-0001-short-title.md
```

## RFC Template

```markdown
# RFC-0000: Title

## Status

Draft | Review | Accepted | Implemented | Rejected

## Summary

One-paragraph proposal summary.

## Motivation

Why does Forge need this change?

## Goals

- Goal 1.
- Goal 2.

## Non-Goals

- Non-goal 1.
- Non-goal 2.

## Proposal

Describe the proposed behavior, architecture, workflow, or policy.

## User Impact

Which roles and workflows change?

## Technical Impact

Which services, models, APIs, plugins, or docs change?

## Human Review And Security

How are approval, audit, permissions, and safety preserved?

## Documentation Impact

Which Forge Academy, task guide, reference, troubleshooting, architecture, or release docs must change?

## Alternatives Considered

What else was considered?

## Acceptance Criteria

- Criterion 1.
- Criterion 2.
```

## Review Expectations

RFC review should focus on operational value, architecture clarity, human authority, security posture, implementation scope, and documentation impact.
