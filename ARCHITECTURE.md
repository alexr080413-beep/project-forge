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

## Storage Service Foundation

`project_forge.storage_service` provides a local artifact abstraction for reading metadata, writing in dry-run mode, listing configured folders, and archiving project artifacts. It uses registered providers and validated locations so future services can reference project storage without embedding filesystem assumptions throughout the platform.

The foundation implements local filesystem behavior only. S3, Azure Blob, and SharePoint providers are placeholders and do not perform network or cloud calls.

## Search Service Foundation

`project_forge.search_service` provides a unified discovery interface across Forge service indexes. A `SearchIndex` acts as a local provider for one service and scope, `SearchQuery` and `SearchFilter` describe deterministic lexical search intent, `SearchMatch` represents indexed service records, `SearchResult` returns ranked paginated results, and `SearchRegistry` coordinates multiple indexes.

The foundation supports exact, partial, tag, metadata, date, service, relevance, and pagination behavior only. Semantic, vector, and hybrid search are explicit future capabilities and are not implemented.

## Audit Service Foundation

`project_forge.audit_service` provides in-memory traceability for significant platform actions. `AuditActor` identifies who or what acted, `AuditEvent` describes the action, category, severity, timestamps, correlation ID, parent event, tags, and metadata, `AuditEntry` stores the event with session context, `AuditSession` groups related activity, and `AuditRegistry` records and filters entries.

The foundation supports audit capture for service execution, workflows, review actions, approvals, rejections, configuration changes, profile selection, AI request metadata, product generation, distribution, and automation execution. It intentionally does not implement persistent storage or database connections.

## Metrics Service Foundation

`project_forge.metrics_service` provides local operational observability for Forge services. `Metric` defines a stream, `MetricValue` records a value, `MetricRegistry` stores and queries metrics, `MetricCollector` offers convenience recording methods, `MetricSnapshot` captures point-in-time state, and `MetricReport` summarizes snapshot values.

The foundation supports counters, gauges, timers, histogram placeholders, tags, metadata, snapshots, and standard metrics for workflow executions, products generated, review queue size, QA pass/fail rates, translation operations, AI requests, automation executions, search requests, and distribution events. It intentionally avoids visualization and external monitoring systems.

## Configuration Service Foundation

`project_forge.configuration_service` provides central local configuration management. `ConfigurationSource` identifies local files and precedence, `ConfigurationItem` represents one scoped setting, `ConfigurationProfile` groups settings for a named runtime profile, `ConfigurationLoader` loads YAML or JSON, `ConfigurationRegistry` provides lookup by scope and key, `ConfigurationResult` records resolved items and audit-ready changes, and `ConfigurationValidator` enforces required fields.

The foundation supports platform, service, profile, workflow, plugin, environment, and user scopes, plus defaults, deterministic overrides, environment variable placeholders, and metadata. It intentionally avoids external secret managers, network calls, and database connections.

## Security Service Foundation

`project_forge.security_service` provides local authorization foundations for Project Forge. `SecurityPrincipal` identifies users, service accounts, and system actors, `SecurityRole` groups permissions, `SecurityPermission` defines action/resource access, `SecurityPolicy` records allow or deny rules, `SecurityContext` resolves effective roles and permissions, `SecurityDecision` preserves audit-ready evaluation records, and `SecurityRegistry` provides in-memory lookup and RBAC evaluation.

The foundation supports default Forge roles, policy validation, role-based access control, metadata, and allow/deny decision records. It intentionally avoids real authentication, CAC integration, external identity providers, credential storage, sessions, databases, and network calls.

## Demo Pipeline Foundation

`project_forge.demo_pipeline` composes the implemented local foundations into the first end-to-end Forge demonstration. It uses `Pipeline`, `PipelineStage`, and `PipelineExecution` to run a sample signal through intake, storage, lookup, event creation, deterministic decisioning, context assembly, translation, offline AI reasoning, product formatting, QA, review, dry-run distribution, audit capture, and metrics snapshotting.

The foundation is intentionally demonstrative and local. It uses repository sample data, dry-run handlers, and stub providers only; it does not perform external collection, web scraping, OpenAI calls, email delivery, or real distribution output.

## Future Sections

As functionality is implemented, expand this document with:

- Core workflows
- Data flow diagrams
- Configuration model
- Error handling strategy
- Testing strategy
- Deployment and operations model
