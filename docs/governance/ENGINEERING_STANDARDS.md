# Engineering Standards

Forge engineering standards preserve long-term maintainability, operational trust, and human authority.

## Folder Organization

| Path | Purpose |
| --- | --- |
| `src/project_forge/` | Python package and service foundations. |
| `tests/` | Tests mirroring package structure. |
| `docs/academy/` | Training, walkthroughs, lessons, task guides, troubleshooting, and reference. |
| `docs/decisions/` | Architecture Decision Records. |
| `docs/rfcs/` | Request For Comments proposals. |
| `docs/governance/` | Project governance, standards, support, and security. |
| `examples/` | Safe sample exercise documentation. |
| `config/` | Safe example configuration. |
| `assets/` | Static project assets. |

## Naming Conventions

- Use clear domain names.
- Use lowercase hyphenated Markdown filenames.
- Use snake_case for Python modules, functions, and variables.
- Use PascalCase for Python classes.
- Use explicit service names and avoid ambiguous abbreviations.
- Use numbered ADRs and RFCs.

## Testing Expectations

- Add unit tests for new behavior.
- Add integration tests for cross-service workflows.
- Keep tests deterministic.
- Avoid external APIs in tests unless isolated and documented.
- Validate workflow, UI, graph, product, review, timeline, and archive changes against Project Sentinel when applicable.
- Run relevant test subsets and the full suite when feasible.

Canonical command:

```bash
python -m pytest
```

## Documentation Requirements

Every feature that changes a user workflow must update Forge Academy.

Every feature that changes setup, deployment, or configuration must update administrator or troubleshooting documentation.

Every feature that changes APIs, plugins, data models, or architecture must update developer or reference documentation.

Pull requests are not complete unless relevant documentation is updated.

## UI Consistency

Forge Studio UI changes should:

- Use the Forge Design System.
- Preserve the dark command-center visual language.
- Avoid consumer-app styling.
- Maintain workspace hierarchy and global context.
- Include screenshots or browser verification when UI changes.

## Accessibility

UI changes should preserve:

- Keyboard access.
- Visible focus states.
- Sufficient contrast.
- Clear labels.
- Layouts that work on narrow and wide viewports.

## Review Requirements

Pull requests should be reviewed for:

- Correctness.
- Tests.
- Documentation.
- Security.
- Human review gates.
- Architecture impact.
- Release note impact.

## Security Expectations

- Do not commit secrets.
- Do not introduce hidden external calls.
- Preserve audit-ready behavior.
- Document authentication and authorization assumptions.
- Keep real-world information and exercise fiction clearly separated.

## Human Review Principle

Forge assists; people decide.

No feature should silently publish, distribute, approve, or release controlled exercise material without explicit human approval.

## Permanent Codex Implementation Prompt Policy

Every future Codex implementation prompt shall include:

- Documentation updates.
- Forge Academy updates.
- Definition of Done validation.
- Architecture updates when applicable.
- Release notes when applicable.
- Screenshots when UI changes.
- Testing requirements.
- Project Sentinel validation when the change affects user workflows, UI demonstrations, operational assets, graph relationships, products, review, archive, or regression behavior.

Codex prompts should also state no-go constraints, human-in-the-loop considerations, and security considerations for the requested change.

## Project Sentinel Reference Exercise

Project Sentinel is the canonical Forge reference exercise. Future development should use Sentinel for:

- UI demonstrations.
- Screenshots.
- Forge Academy walkthroughs.
- Regression testing plans.
- Documentation examples.
- Conference demonstrations.
- Future automated test fixture design.

Do not create a new reference scenario when Sentinel can cover the workflow. Extend Sentinel documentation first, then add variants only when a feature requires a distinct exercise family.
