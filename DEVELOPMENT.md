# Project Forge Development

## Development Philosophy

Project Forge should be developed as a disciplined platform for EXCON workflows. The codebase should remain modular, testable, explicit, and safe for future operational use.

Contributors should prefer small, well-documented changes that strengthen one service boundary at a time.

## Coding Standards

Project Forge uses Python package code under `src/project_forge/` and tests under `tests/`.

Standards:

- Use typed dataclasses and enums for domain models where practical.
- Keep service responsibilities narrow.
- Keep domain logic separate from I/O and orchestration.
- Prefer deterministic local behavior for foundations.
- Avoid hidden external calls.
- Keep configuration loading explicit.
- Validate inputs close to model construction or loading.
- Use registries for dynamically registered capabilities.
- Keep generated artifacts out of Git unless they are intentional fixtures.
- Do not commit secrets, credentials, tokens, private keys, personal paths, or private exercise data.

## Testing Standards

Tests should mirror the source package structure.

Recommended practices:

- Add focused unit tests for each new behavior.
- Add integration tests when workflows cross service boundaries.
- Test validation failures, duplicate identifiers, missing fields, and deterministic ordering.
- Keep tests free of external API dependencies unless explicitly isolated and documented.
- Use local fixtures and safe example configuration.
- Use Project Sentinel as the reference exercise for workflow, UI, graph, product, review, archive, and future regression scenarios when applicable.

Canonical test command:

```bash
python -m pytest
```

## Documentation Standards

Documentation should be updated when a change affects:

- Platform architecture
- Service responsibilities
- Configuration
- Workflows
- Product plugins
- Profiles
- Operations
- Contributor expectations

Documentation should be clear enough for both leadership and future developers. Avoid unexplained acronyms where a broader audience may need context.

Project Sentinel in `examples/sentinel/` is the canonical reference exercise for documentation, Academy, UI demonstrations, screenshots, conference demonstrations, development examples, and future automated testing.

## Milestone Naming

Project Forge milestones use alphabetic call signs to group related work.

Recommended pattern:

```text
Forge <Milestone Name> - Ticket <Number>: <Short Title>
```

Examples:

```text
Forge November - Ticket 001: Build Pipeline Orchestrator Foundation
Forge Oscar - Ticket 001: Create Platform Documentation
```

Guidelines:

- Use one milestone name for a coherent body of work.
- Use three-digit ticket numbers.
- Keep ticket titles action-oriented.
- Keep each ticket small enough to review.

## Commit Conventions

Use clear, imperative commit messages.

Recommended format:

```text
<type>: <short summary>
```

Recommended types:

- `docs`: Documentation-only changes
- `feat`: New user-visible or platform capability
- `fix`: Bug fix
- `test`: Test-only change
- `refactor`: Internal restructuring without behavior change
- `chore`: Tooling, housekeeping, or maintenance

Examples:

```text
docs: add platform documentation set
feat: add pipeline orchestrator foundation
test: cover product plugin validation failures
```

Commit bodies should explain why a change exists when the summary is not enough.

## Ticket Conventions

Tickets should include:

- Objective
- Context or problem statement
- Requirements
- Explicit non-goals
- Acceptance criteria
- Documentation expectations
- Testing expectations
- Project Sentinel validation expectations when applicable

Good tickets make boundaries clear. For example, a ticket may say "Do not implement code" or "No external APIs" to preserve scope.

## Contribution Workflow

Recommended workflow:

1. Read relevant repository documentation before making changes.
2. Inspect the existing package and test patterns.
3. Keep changes focused on the ticket.
4. Add or update tests for behavior changes.
5. Update documentation when platform behavior or conventions change.
6. Run the relevant test subset.
7. Run the full test suite when feasible.
8. Review the Git diff before handoff.

## Branch Naming

Use focused branch names.

Recommended pattern:

```text
codex/<milestone>-<ticket>-<short-topic>
```

Example:

```text
codex/oscar-001-platform-docs
```

## Review Expectations

Reviews should prioritize:

- Correctness
- Scenario safety
- Test coverage
- Service boundaries
- Determinism
- Documentation accuracy
- Configuration safety
- Human review and approval controls

Reviewers should look for accidental external calls, hidden generation behavior, weak validation, unclear ownership, and anything that could blur real-world material with exercise fiction.

## Release Discipline

Before a release or leadership demonstration:

- Confirm docs reflect current system behavior.
- Confirm examples are safe and notional.
- Confirm tests pass.
- Confirm generated outputs are not accidentally committed.
- Confirm plugin and profile examples do not contain sensitive data.
- Confirm current limitations are stated plainly.
