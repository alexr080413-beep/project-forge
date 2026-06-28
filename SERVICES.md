# Project Forge Services

This document describes the current and planned service boundaries for Project Forge. Services are listed by platform responsibility, not by implementation maturity.

## Service Summary

| Service | Responsibility | Current Status |
| --- | --- | --- |
| Core Models | Shared source, scenario, request, report, and review entities | Implemented foundation |
| Integration Service | Load, validate, register, and dry-run external and internal source connectors | Implemented foundation |
| Knowledge Engine | Index exercise knowledge documents | Implemented foundation |
| Scenario Engine | Load and validate scenario facts, assumptions, constraints, objectives, and control measures | Implemented foundation |
| Entity Engine | Load and validate exercise entities and relationships | Implemented foundation |
| Event Engine | Load and validate exercise events and event metadata | Implemented foundation |
| Exercise State Engine | Represent current exercise phase, day, tempo, escalation, and situation | Implemented foundation |
| Context Engine | Assemble deterministic context snapshots for downstream services | Implemented foundation |
| Decision Engine | Evaluate deterministic rules for relevance, escalation, duplicates, and consistency | Implemented foundation |
| Profile Manager | Load, validate, and register exercise environment profiles | Implemented foundation |
| Translation Engine | Apply deterministic profile dictionaries and mappings | Implemented foundation |
| AI Reasoning Engine | Build bounded prompts and provider interfaces without live API calls | Implemented foundation |
| Product SDK | Load, validate, discover, register, and format product plugins | Implemented foundation |
| QA Service | Run deterministic product checks and aggregate QA status | Implemented foundation |
| Review Queue | Hold products for human controller review before release | Implemented foundation |
| Distribution Service | Handle approved product outputs after review through local and placeholder channels | Implemented foundation |
| Storage Service | Read metadata, list, dry-run write, and archive project artifacts through local and placeholder providers | Implemented foundation |
| Search Service | Query and rank local indexes across Forge service domains | Implemented foundation |
| Audit Service | Record and filter significant platform actions for traceability and after-action review | Implemented foundation |
| Metrics Service | Collect local operational metrics, snapshots, and reports for health and exercise analytics | Implemented foundation |
| Configuration Service | Load, resolve, validate, and look up local platform configuration | Implemented foundation |
| Automation Service | Record schedule, manual, event, workflow, and conditional triggers for workflows | Implemented foundation |
| Workflow Engine | Execute ordered local workflow steps | Implemented foundation |
| Pipeline Orchestrator | Coordinate platform services into end-to-end pipelines | Implemented foundation |

## Core Models

**Responsibilities**

- Define shared domain entities for sources, exercise context, scenario actors, locations, report requests, generated reports, review status, and quality checks.
- Provide simple typed containers used across early platform foundations.

**Inputs**

- Source item metadata
- Scenario context metadata
- Report request metadata

**Outputs**

- Typed source, context, request, generated report, and review objects

**Dependencies**

- Python standard library only

## Integration Service

**Responsibilities**

- Load integration source definitions from local YAML.
- Validate RSS, website, manual upload, local file, email placeholder, social media placeholder, SharePoint placeholder, and API placeholder sources.
- Register source connectors by source type.
- Execute dry-run collection without contacting external systems.
- Preserve result status, metadata, errors, and audit history.

**Inputs**

- Integration source configuration such as `config/integration_sources.example.yaml`
- `IntegrationSource`
- `IntegrationRequest`
- Registered local connectors

**Outputs**

- `IntegrationResult`
- `IntegrationStatus`
- Connector audit metadata

**Dependencies**

- Local filesystem for local file validation
- Python standard library validation utilities

**Current Boundary**

The service does not scrape websites, access email, call APIs, access social media, call SharePoint, or publish source material. Placeholder connectors record intent and audit metadata only.

## Knowledge Engine

**Responsibilities**

- Load and index durable exercise knowledge documents.
- Preserve document type, path, references, and metadata.
- Provide knowledge references for context assembly.

**Inputs**

- Files in `knowledge_base/`
- Knowledge document metadata

**Outputs**

- `ExerciseKnowledgeBase`
- `KnowledgeBaseIndex`
- `KnowledgeDocument`

**Dependencies**

- Local filesystem
- Knowledge document configuration conventions

## Scenario Engine

**Responsibilities**

- Load scenario definitions.
- Validate scenario objectives, constraints, assumptions, control measures, escalation level, tempo, and status.
- Provide scenario facts for context snapshots and QA boundaries.

**Inputs**

- Scenario configuration such as `config/scenario.example.yaml`

**Outputs**

- `Scenario`
- Scenario objectives, constraints, assumptions, phases, and control measures
- `ScenarioRegistry`

**Dependencies**

- Knowledge Engine references
- Entity and event identifiers
- Exercise state concepts

## Entity Engine

**Responsibilities**

- Load exercise organizations, units, installations, individuals, platforms, capabilities, and relationships.
- Normalize entity categories, affiliations, aliases, and status.
- Support scenario and context services with stable entity references.

**Inputs**

- Entity configuration such as `config/entities.example.yaml`

**Outputs**

- `EntityCatalog`
- Typed entity records
- Relationship records

**Dependencies**

- Scenario profile conventions
- Translation dictionaries for aliases and mappings

## Event Engine

**Responsibilities**

- Load and validate exercise events.
- Track event type, source, severity, impact, status, related entities, and metadata.
- Provide event context for workflows and pipelines.

**Inputs**

- Event configuration such as `config/events.example.yaml`

**Outputs**

- `ExerciseEvent`
- `EventRegistry`
- Validated event metadata

**Dependencies**

- Entity identifiers
- Scenario day and phase
- Exercise state

## Exercise State Engine

**Responsibilities**

- Represent the current exercise state.
- Track phase, day, tempo, escalation, political situation, military situation, and information environment.
- Provide current state to context assembly and workflow decisions.

**Inputs**

- Exercise state configuration such as `config/exercise_state.example.yaml`

**Outputs**

- `ExerciseState`
- Current exercise day and phase
- Situation state objects

**Dependencies**

- Scenario timeline
- Controller-defined state updates

## Context Engine

**Responsibilities**

- Assemble deterministic context snapshots.
- Combine scenario, knowledge, entities, events, decisions, exercise state, and training objectives.
- Produce references that downstream services can trace.

**Inputs**

- Knowledge base
- Exercise state
- Scenario registry
- Entity catalog
- Event registry
- Decision results

**Outputs**

- `ContextSnapshot`
- `ExerciseContext`
- `ContextReference`

**Dependencies**

- Knowledge Engine
- Scenario Engine
- Entity Engine
- Event Engine
- Decision Engine
- Exercise State Engine

## Decision Engine

**Responsibilities**

- Evaluate deterministic decision rules.
- Identify duplicate events, escalation issues, scenario consistency risks, and training objective relevance.
- Produce rule results that can guide workflow branching and QA.

**Inputs**

- `DecisionContext`
- Scenario facts
- Event metadata
- Training objectives

**Outputs**

- `DecisionResult`
- `RuleEvaluation`
- `DecisionOutcome`

**Dependencies**

- Scenario Engine
- Event Engine
- Context Engine

## Translation Engine

**Responsibilities**

- Apply deterministic translation dictionaries.
- Map real-world names, countries, organizations, units, locations, leaders, equipment, agencies, alliances, and exercise names into scenario terms.
- Support profile-specific transformation rules.

**Inputs**

- Translation dictionaries such as `config/translation_dictionaries.example.yaml`
- `TranslationContext`
- Source text or structured fields

**Outputs**

- `TranslationResult`
- Applied rule metadata
- Scenario-safe terminology

**Dependencies**

- Profiles
- Scenario Engine
- Entity Engine

## Profile Manager

**Responsibilities**

- Load exercise environment profiles from local YAML.
- Validate required profile fields and path bindings.
- Register profiles for lookup by profile ID.
- Select enabled services, enabled plugins, dictionaries, workflows, templates, knowledge paths, and default scenarios without modifying Forge Core.

**Inputs**

- Profile configuration such as `config/profiles.example.yaml`
- Local paths to knowledge base, templates, translation dictionaries, and workflows

**Outputs**

- `ForgeProfile`
- `ProfileMetadata`
- `ProfileComponent`
- `ProfileRegistry`

**Dependencies**

- Local filesystem
- Knowledge Engine paths
- Product SDK plugin/template paths
- Translation Engine dictionary paths
- Workflow Engine configuration paths

## AI Reasoning Engine

**Responsibilities**

- Build deterministic prompts and AI request structures.
- Provide provider interfaces for future OpenAI, Azure OpenAI, government-hosted LLM, and offline stub use.
- Keep model configuration and prompt templates explicit and testable.

**Inputs**

- `AIContext`
- Prompt templates
- Model configuration
- Prepared scenario and product context

**Outputs**

- `AIRequest`
- `AIResponse`
- Prompt material

**Dependencies**

- Context Engine
- Translation Engine
- Product SDK
- Future provider integration

**Current Boundary**

The current foundation does not perform live API calls.

## Product SDK

**Responsibilities**

- Load product plugin definitions.
- Validate product metadata, definitions, templates, required fields, and output formats.
- Discover product plugins from configuration.
- Format product output from supplied context.

**Inputs**

- Product plugin files such as `config/product_plugins/*.yaml`
- Product context dictionaries

**Outputs**

- `ProductPlugin`
- `ProductDefinition`
- `ProductTemplate`
- `ProductOutput`

**Dependencies**

- Product plugin configuration
- Context Engine
- QA Service

## QA Service

**Responsibilities**

- Register and run deterministic QA checks.
- Validate required fields, exercise day, report type, source references, confidence, and real-world actor leakage.
- Aggregate pass, warning, and fail status.

**Inputs**

- Product dictionaries
- QA check definitions

**Outputs**

- `QAReport`
- `QAResult`
- `QAFinding`
- `QAStatus`

**Dependencies**

- Product SDK
- Scenario and profile rules
- Translation Engine for leakage control

## Review Queue

**Responsibilities**

- Hold prepared or generated products before release.
- Preserve queue ordering by priority and submission time.
- Support reviewer assignment, approval, rejection, and revision requests.
- Retain review comments, notes, audit history, and timestamps.
- Provide registry and manager interfaces for local queue operations.

**Inputs**

- Product identifiers and product metadata
- Reviewer assignments
- Review decisions
- Review comments and notes

**Outputs**

- `ReviewItem`
- `ReviewQueue`
- `ReviewDecision`
- `ReviewComment`
- `ReviewStatus`
- `Reviewer`

**Dependencies**

- Product SDK
- QA Service
- Human controller workflow

## Distribution Service

**Responsibilities**

- Handle approved product outputs after human review.
- Register distribution channels.
- Validate targets and supported output formats.
- Track distribution status.
- Preserve distribution metadata and audit logs.
- Support dry-run mode for safe operational rehearsal.
- Provide local file and archive folder handlers.
- Provide placeholder channels for email-ready output, markdown, HTML, DOCX, PDF, PowerPoint, SharePoint, and Teams.

**Inputs**

- Approved distribution items
- Distribution requests
- Distribution targets
- Registered channels

**Outputs**

- `DistributionItem`
- `DistributionChannel`
- `DistributionTarget`
- `DistributionRequest`
- `DistributionResult`
- `DistributionStatus`

**Dependencies**

- Review Queue approval boundary
- Product SDK output metadata
- Local filesystem for local file and archive folder handlers

**Current Boundary**

The service does not send email, call SharePoint, call Teams, use external APIs, or automatically publish products. Placeholder channels record status and audit metadata only.

## Storage Service

**Responsibilities**

- Register storage providers for local and placeholder artifact locations.
- Validate configured paths and prevent relative path traversal.
- Read local artifact metadata.
- Support dry-run writes by default.
- List items from configured local folders.
- Archive local artifacts into configured archive folders.
- Preserve storage operation metadata and audit logs.

**Inputs**

- `StorageLocation`
- `StorageProvider`
- `StorageRequest`
- Local project folders such as `outputs/`, `knowledge_base/`, and `assets/`

**Outputs**

- `StorageItem`
- `StorageResult`
- `StorageStatus`
- Audit metadata for storage operations

**Dependencies**

- Local filesystem for implemented providers
- Python standard library only

**Current Boundary**

The service does not call S3, Azure Blob Storage, SharePoint, cloud APIs, or network services. Cloud and SharePoint providers are placeholders that record intent and audit metadata only.

## Search Service

**Responsibilities**

- Register multiple local search indexes.
- Validate search queries, filters, indexes, and ranked results.
- Search knowledge documents, events, entities, exercise state, scenarios, products, review queue items, QA findings, workflows, and profiles.
- Support exact, partial, tag, metadata, date-filtered, and service-filtered search.
- Rank results with deterministic relevance scoring.
- Return paginated results.
- Declare future semantic, vector, and hybrid search capabilities without implementing them.

**Inputs**

- `SearchQuery`
- `SearchFilter`
- `SearchIndex`
- Local indexed `SearchMatch` records from Forge services

**Outputs**

- `SearchResult`
- Ranked `SearchMatch` records
- Search metadata

**Dependencies**

- Registered local service indexes
- Python standard library only

**Current Boundary**

The service does not perform semantic search, vector search, hybrid search, embedding generation, external API calls, or network calls.

## Audit Service

**Responsibilities**

- Record significant platform actions in memory.
- Validate audit actors, actions, categories, events, entries, sessions, and filters.
- Capture timestamps, correlation IDs, parent/child event relationships, severity, tags, and metadata.
- Support filtering by category, action, severity, service, actor, tag, correlation ID, parent event, date range, and metadata.
- Support service execution, workflow execution, review actions, approvals, rejections, configuration changes, profile selection, AI request metadata, product generation, distribution, and automation execution events.

**Inputs**

- `AuditActor`
- `AuditEvent`
- `AuditSession`
- `AuditFilter`

**Outputs**

- `AuditEntry`
- Filtered audit entry lists
- Session records

**Dependencies**

- Python standard library only
- Platform services that emit audit events

**Current Boundary**

The service stores entries in memory only. It does not implement persistent storage, connect to databases, or store AI prompt/response content.

## Metrics Service

**Responsibilities**

- Register local metrics across Forge services.
- Collect counters, gauges, timers, and histogram placeholders.
- Record metric values with tags and metadata.
- Create metric snapshots.
- Produce local metric reports.
- Query metrics by type, name, tag, and metadata.
- Support standard metrics for workflow executions, products generated, review queue size, QA pass/fail rates, translation operations, AI requests, automation executions, search requests, and distribution events.

**Inputs**

- `Metric`
- `MetricValue`
- `MetricFilter`
- Collector updates from platform services

**Outputs**

- `MetricSnapshot`
- `MetricReport`
- Queried metric lists

**Dependencies**

- Python standard library only
- Platform services that emit metric values

**Current Boundary**

The service does not implement visualization, dashboards, external monitoring integrations, or histogram aggregation. Histogram metrics are placeholders only.

## Configuration Service

**Responsibilities**

- Load local YAML and JSON configuration files.
- Resolve default values and deterministic override precedence.
- Validate required configuration fields.
- Support platform, service, profile, workflow, plugin, environment, and user scopes.
- Support environment variable placeholders with safe fallbacks.
- Register and look up configuration by scope and key.
- Preserve metadata and audit-ready change records.

**Inputs**

- `ConfigurationSource`
- Local YAML or JSON configuration files
- `ConfigurationItem`
- `ConfigurationProfile`

**Outputs**

- `ConfigurationRegistry`
- `ConfigurationResult`
- Resolved configuration values
- Audit-ready `ConfigurationChangeRecord` entries

**Dependencies**

- Local filesystem
- Python standard library only, with optional PyYAML when available

**Current Boundary**

The service does not connect to external secret managers, perform network calls, connect to databases, or decrypt/manage secrets.

## Automation Service

**Responsibilities**

- Define automation rules for workflow-oriented activity.
- Validate cron schedules, event triggers, manual triggers, workflow triggers, and conditional triggers.
- Enable or disable rules.
- Record automation execution history.
- Apply retry policy limits to recorded execution attempts.
- Register and look up automation rules.

**Inputs**

- `AutomationRule`
- `Schedule`
- `Trigger`
- `EventTrigger`
- `WorkflowTrigger`
- Local event or workflow status payloads

**Outputs**

- `AutomationExecution`
- Recorded execution history
- Trigger status metadata

**Dependencies**

- Workflow identifiers
- Local event payloads
- Local registry state

**Current Boundary**

The service does not use external schedulers and does not execute workflows. It records that a trigger matched or was skipped so future runtime services can act deliberately.

## Workflow Engine

**Responsibilities**

- Load and execute ordered workflow steps.
- Support dependencies, conditions, retry attempts, execution context, step results, and logs.
- Provide deterministic workflow preparation for known product families.

**Inputs**

- Workflow configuration such as `config/workflows.example.yaml`
- Local step handlers

**Outputs**

- `WorkflowExecution`
- `WorkflowResult`
- Workflow execution log

**Dependencies**

- Context Engine
- Decision Engine
- Translation Engine
- Product SDK

## Pipeline Orchestrator

**Responsibilities**

- Coordinate services into a single end-to-end pipeline.
- Register stages dynamically.
- Execute stages in order.
- Capture execution metadata, stage results, logs, failure state, and pipeline status.

**Inputs**

- `Pipeline`
- `PipelineStage`
- `PipelineContext`
- Local stage handlers

**Outputs**

- `PipelineExecution`
- `PipelineResult`
- Updated pipeline context

**Dependencies**

- Workflow Engine concepts
- Context Engine
- Translation Engine
- AI Reasoning Engine
- Product SDK
- QA Service
- Review Queue
- Distribution Service
