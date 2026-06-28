# Contributing

Thank you for helping improve Project Forge.

This project is currently in the scaffold stage. Contributions should focus on clarifying documentation, establishing standards, and adding tested functionality only after the intended behavior is documented.

## Product Governance

Before changing Forge behavior, read the product and governance foundation:

- [PRODUCT.md](PRODUCT.md)
- [docs/product/PRINCIPLES.md](docs/product/PRINCIPLES.md)
- [docs/product/FEATURE_SPEC_TEMPLATE.md](docs/product/FEATURE_SPEC_TEMPLATE.md)
- [docs/product/REFERENCE_IMPLEMENTATIONS.md](docs/product/REFERENCE_IMPLEMENTATIONS.md)
- [docs/academy/README.md](docs/academy/README.md)
- [docs/decisions/README.md](docs/decisions/README.md)
- [docs/rfcs/README.md](docs/rfcs/README.md)

Significant product work should start with a feature specification. Architecture-changing work should update Architecture Decision Records. Major proposals should follow the RFC process. Project Sentinel is the canonical reference implementation for tutorials, screenshots, demonstrations, and regression planning.

## Development Expectations

- Keep changes small and reviewable.
- Follow the Forge product principles.
- Add or update tests with behavior changes.
- Update documentation when workflows, configuration, or operations change.
- Update Forge Academy when user workflows change.
- Validate applicable changes against Project Sentinel.
- Avoid committing generated output unless it is an intentional fixture.
- Do not commit secrets, credentials, private keys, or personal machine paths.

## Suggested Workflow

1. Read the relevant product principles, Academy material, reference docs, ADRs, and RFCs.
2. Create or update a feature specification for significant product work.
3. Create a focused branch.
4. Update or add tests for the behavior being changed.
5. Implement the smallest clear change.
6. Validate against Project Sentinel when the workflow, UI, data model, or documentation example applies.
7. Run the project checks once they are defined.
8. Update relevant documentation, Academy material, release notes, ADRs, and RFCs.

## Code Style

Project Forge will use the tooling configured in `pyproject.toml`. As the project matures, this file should remain the source of truth for formatting, linting, testing, and type-checking settings.
