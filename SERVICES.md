# Project Forge Services

This document describes the current and planned service boundaries for Project Forge. Services are listed by platform responsibility, not by implementation maturity.

## Service Summary

| Service | Responsibility | Current Status |
| --- | --- | --- |
| Core Models | Shared source, scenario, request, report, and review entities | Implemented foundation |
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
