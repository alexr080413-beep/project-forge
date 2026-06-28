# Architecture Decision Records

Architecture Decision Records, or ADRs, document significant technical and product architecture decisions for Forge.

## Purpose

ADRs explain why Forge chose a design, not only what was built. They preserve context for future contributors, reviewers, and exercise stakeholders.

Use an ADR when a change affects:

- Platform architecture.
- Data ownership.
- Service boundaries.
- Workflow authority.
- Security or audit posture.
- Persistence or integration strategy.
- Long-term extension points.

## Naming Convention

Use this file pattern:

```text
ADR-0001-short-title.md
```

The title inside the file should use:

```text
# ADR-0001: Short Title
```

## Numbering

- Numbers are four digits.
- Numbers are assigned in order.
- Do not renumber accepted ADRs.
- Superseded ADRs remain in the history.

## Lifecycle

| Status | Meaning |
| --- | --- |
| Proposed | Draft decision under discussion. |
| Accepted | Approved and current. |
| Superseded | Replaced by a later ADR. |
| Deprecated | No longer recommended, but not directly replaced. |
| Rejected | Considered and intentionally not adopted. |

## Template

```markdown
# ADR-0000: Title

## Status

Proposed | Accepted | Superseded | Deprecated | Rejected

## Date

YYYY-MM-DD

## Context

What problem, constraint, or opportunity required a decision?

## Decision

What did Forge decide?

## Consequences

What becomes easier, harder, constrained, or enabled?

## Alternatives Considered

What options were considered and why were they not selected?

## Documentation Impact

What Forge Academy, reference, architecture, or troubleshooting docs changed?
```

## Current Decision Register

| ADR | Title | Status | Summary |
| --- | --- | --- | --- |
| ADR-0001 | Exercise Data Engine | Accepted | Forge Studio uses the Exercise Data Engine as the single source of truth for local workspace state. |
| ADR-0002 | Exercise Workspace Framework | Accepted | Forge Studio uses the hierarchy `Forge -> Organization -> Exercise -> Workspace`. |
| ADR-0003 | Operational Knowledge Graph | Accepted | Operational assets become graph nodes and relationships become graph edges. |

## Example ADR Summaries

### ADR-0001: Exercise Data Engine

Forge Studio workspaces should read from one exercise snapshot instead of maintaining independent page-level mock data. This keeps dashboard metrics, review state, injects, products, controllers, audit records, and activity synchronized.

### ADR-0002: Exercise Workspace Framework

Forge Studio should always operate inside a selected Organization, Exercise, and Workspace. This establishes the permanent navigation and context model for multi-exercise operations.

### ADR-0003: Operational Knowledge Graph

Forge should treat operational assets as connected graph nodes with typed relationship edges. This prepares Forge for future Mission Replay, operational analytics, and bounded AI-assisted planning.
