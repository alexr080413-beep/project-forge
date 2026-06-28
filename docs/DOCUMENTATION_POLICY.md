# Documentation Policy

Forge documentation is part of the product, not a release afterthought.

## Required Updates

- Every feature that changes a user workflow must update Forge Academy.
- Every feature that changes setup, deployment, or configuration must update administrator or troubleshooting documentation.
- Every feature that changes APIs, plugins, data models, or architecture must update developer or reference documentation.
- Codex tickets should include a documentation update requirement.
- Pull requests should not be considered complete unless relevant documentation is updated.
- Documentation should be role-based, task-based, and scenario-based.

## Documentation Model

Forge documentation should answer three questions:

| Question | Documentation Type |
| --- | --- |
| Who needs to understand this? | Role-based learning paths. |
| What task are they trying to complete? | Task guides and walkthroughs. |
| What concept or term do they need to look up? | Reference documentation. |

## Pull Request Checklist

Every pull request should consider:

- Does this change alter a user workflow?
- Does this change alter setup, startup, configuration, or deployment?
- Does this change alter models, APIs, plugins, permissions, or architecture?
- Does Forge Academy need a new lesson, walkthrough step, task guide, or troubleshooting entry?
- Does the reference section need a new glossary term or relationship definition?

If the answer is yes, update the relevant documentation in the same change.

## Writing Standard

Forge documentation should be:

- Operational.
- Concise.
- Scenario-based.
- Human-review centered.
- Clear about current implementation boundaries.
- Explicit about mock, future, and not-yet-implemented behavior.
