# Architecture

This document records the intended architecture for Project Forge. It exists before implementation so future contributors have a shared place to explain design decisions as the system grows.

## Current State

Project Forge contains a typed local foundation for core domain models and deterministic service modules. It now includes an in-process Pipeline Orchestrator foundation for ordered workflows, but it does not yet include production services, external integrations, or command-line entry points.

## Intended Boundaries

- `src/project_forge/` contains importable Python package code.
- `config/` contains safe, version-controlled configuration examples.
- `knowledge_base/` contains human-readable research and project context.
- `assets/` contains static inputs that support the application or documentation.
- `outputs/` is reserved for generated files and local run artifacts.
- `tests/` mirrors the package structure as functionality is added.

## Design Guidelines

- Keep domain logic separate from I/O and orchestration.
- Prefer small modules with clear responsibilities.
- Make external service integrations replaceable and testable.
- Keep configuration loading explicit and documented.
- Record significant architecture decisions in this file or future ADRs.

## Pipeline Orchestrator Foundation

`project_forge.pipeline_orchestrator` coordinates Project Forge services through local, ordered pipeline stages. A `Pipeline` owns the ordered stage list, `PipelineStage` wraps one deterministic callable, `PipelineContext` carries shared data and metadata, `PipelineExecution` records status, stage results, and execution logs, and `PipelineRegistry` provides in-memory registration for pipelines and reusable stages.

The foundation intentionally avoids external APIs, AI provider calls, and report generation. It is designed to connect existing deterministic service foundations while preserving auditable status, failure handling, and human review boundaries.

## Future Sections

As functionality is implemented, expand this document with:

- Core workflows
- Data flow diagrams
- Configuration model
- Error handling strategy
- Testing strategy
- Deployment and operations model
