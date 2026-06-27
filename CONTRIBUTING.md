# Contributing

Thank you for helping improve Project Forge.

This project is currently in the scaffold stage. Contributions should focus on clarifying documentation, establishing standards, and adding tested functionality only after the intended behavior is documented.

## Development Expectations

- Keep changes small and reviewable.
- Add or update tests with behavior changes.
- Update documentation when workflows, configuration, or operations change.
- Avoid committing generated output unless it is an intentional fixture.
- Do not commit secrets, credentials, private keys, or personal machine paths.

## Suggested Workflow

1. Create a focused branch.
2. Update or add tests for the behavior being changed.
3. Implement the smallest clear change.
4. Run the project checks once they are defined.
5. Update relevant documentation.

## Code Style

Project Forge will use the tooling configured in `pyproject.toml`. As the project matures, this file should remain the source of truth for formatting, linting, testing, and type-checking settings.
