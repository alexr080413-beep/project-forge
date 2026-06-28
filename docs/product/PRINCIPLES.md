# Product Principles

These principles guide Forge product decisions.

| Principle | Product Standard |
| --- | --- |
| Humans remain in command. | Do not automate away operational authority. |
| Machine assistance never replaces operational judgment. | Assistance must be explainable and reviewable. |
| Every operational decision is auditable. | Decisions, approvals, rejections, and releases need records. |
| Everything belongs to an Exercise. | No orphan workflows or context-free objects. |
| Operational Assets are first-class citizens. | Assets need identifiers, metadata, relationships, and lifecycle state. |
| Relationships are as important as data. | Product experiences should expose operational context and dependency. |
| Documentation evolves with the software. | Documentation updates are part of feature completion. |
| Design for operators under pressure. | Prioritize scanability, clarity, and reliable action. |
| Reduce clicks. | High-frequency workflows should get shorter over time. |
| Reduce administrative burden. | Replace repeated manual tracking with shared exercise data. |
| Open architecture. | Keep service boundaries and extension points clear. |
| Modularity. | Build features as composable, testable capabilities. |
| Accessibility. | Support readable, keyboard-accessible, inclusive workflows. |
| Operational realism. | Use realistic but fictional examples and workflows. |

## Decision Rule

When a product tradeoff is unclear, choose the option that preserves human authority, auditability, exercise context, and operational clarity.
