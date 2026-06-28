# Project Forge Workflows

## Workflow Philosophy

Project Forge workflows should be explicit, deterministic, auditable, and controller-centered.

The platform should make it clear:

- Which steps ran
- Which inputs were used
- Which services contributed
- Which metadata was preserved
- Which checks passed or failed
- Where human review is required

Automation should accelerate preparation, not remove EXCON judgment. Every workflow should preserve the difference between real-world source material, exercise-world truth, draft product content, QA findings, and approved release material.

## Workflow Principles

- **Deterministic first**: Prefer repeatable local processing before model-assisted drafting.
- **Context before content**: Assemble scenario context before preparing products.
- **Translation before release**: Convert real-world terms into scenario language before products enter review.
- **QA before review**: Run automated checks before asking controllers to approve.
- **Human approval before output**: Do not release products without controller review.
- **Logs matter**: Workflows and pipelines should record execution status, results, metadata, and failures.
- **Small steps compose**: Services should remain independently testable and then be composed into larger workflows.

## Workflow Engine

The Workflow Engine provides ordered step execution for deterministic preparation workflows.

It supports:

- Workflow definitions
- Ordered steps
- Step dependencies
- Conditional execution
- Retry attempts
- Execution context
- Step results
- Execution logging
- Workflow status

Example workflow families in `config/workflows.example.yaml` include:

- Daily Intelligence Summary
- Breaking News Inject
- White Cell Morning Products
- Intelligence Report Generation prerequisites

These workflows currently prepare and stage inputs. They do not generate final reports.

## Pipeline Execution

The Pipeline Orchestrator coordinates platform services into an end-to-end execution path.

It supports:

- Pipeline definitions
- Dynamic stage registration
- Ordered stage execution
- Shared pipeline context
- Execution metadata
- Stage result metadata
- Execution logs
- Failure handling
- Pipeline status

The current example pipeline is:

```text
Real World Event -> Context -> Translation -> AI Reasoning -> Product SDK -> QA -> Review Queue
```

This represents the platform-level flow from signal to review. The current foundation uses local deterministic handlers and does not call external APIs, invoke OpenAI, or generate final reports.

## End-to-End Demo Pipeline

The `project_forge.demo_pipeline` package provides the first full local Project Forge demonstration pipeline. It can be executed with:

```bash
python -m project_forge.demo_pipeline
```

The demo runs this deterministic flow:

```text
Sample real-world event
-> Integration Service dry-run
-> Storage Service dry-run
-> Knowledge lookup
-> Scenario lookup
-> Entity lookup
-> Event creation
-> Decision Engine
-> Context Engine
-> Translation Engine
-> AI Reasoning offline stub
-> Product SDK draft output
-> QA Service
-> Review Queue
-> Distribution dry-run
-> Audit log
-> Metrics snapshot
```

The command prints the pipeline status and each stage result. It uses only repository sample data, local registries/loaders, dry-run handlers, and the offline AI stub provider. It does not call external APIs, invoke OpenAI, send email, scrape the web, or write distribution output.

## Integration Source Intake

The Integration Service defines where source material may originate before an event or workflow uses it. It supports YAML-loaded source definitions, connector registration, source validation, dry-run collection, and audit metadata.

Integration intake is deliberately conservative in the current foundation. RSS, website, manual upload, and local file sources can be represented and validated; email, social media, SharePoint, and API sources are placeholders. No connector performs live collection, scraping, mailbox access, platform access, or API calls.

## Review Queue Execution

The Review Queue Service holds prepared products after QA and before any release or export step. It supports priority ordering, reviewer assignment, approval, rejection, revision requests, notes, timestamps, and audit history.

The review queue is not an automatic publishing surface. It is the explicit human control point where EXCON decides whether a product can proceed, must be revised, or should be rejected.

## Distribution Execution

The Distribution Service handles approved product outputs after human review. It supports channel registration, target validation, dry-run mode, status tracking, and audit metadata.

The current foundation supports local file export and archive folder handlers, plus safe placeholder channels for email-ready output, markdown, HTML, DOCX, PDF, PowerPoint, SharePoint, and Teams. Placeholder channels do not send messages, call collaboration platforms, or use external APIs.

## Storage Execution

The Storage Service provides a common artifact access boundary for project folders. It supports provider registration, path validation, metadata reads, dry-run writes, local folder listing, archive operations, and audit metadata.

The current foundation supports local filesystem, archive folder, output folder, knowledge base folder, and template folder providers. S3, Azure Blob, and SharePoint providers are placeholders and do not make cloud, SharePoint, or network calls.

## Search Execution

The Search Service provides ranked discovery across local Forge service indexes. It supports exact search, partial search, tag search, metadata search, date filtering, service filtering, relevance scoring, and pagination.

The current foundation is lexical and deterministic. Semantic search, vector search, and hybrid search are represented as future capabilities only and are not executed.

## Audit Execution

The Audit Service records significant platform actions for traceability, accountability, and after-action review. It supports timestamps, actors, action categories, correlation IDs, parent/child events, severity, tags, metadata, sessions, and filtering.

The current foundation is in-memory only. It does not persist audit entries, connect to databases, or store AI prompt or response content.

## Metrics Execution

The Metrics Service collects local operational metrics across Forge services. It supports counters, gauges, timers, histogram placeholders, tags, metadata, snapshots, collectors, and reports for workflow executions, product generation, review queue size, QA pass/fail rates, translation operations, AI requests, automation executions, search requests, and distribution events.

The current foundation does not implement visualization, dashboards, external monitoring systems, or histogram aggregation.

## Configuration Execution

The Configuration Service resolves local platform settings before services, workflows, profiles, plugins, and runtime behavior consume them. It supports YAML and JSON loading, default values, deterministic override precedence, required field validation, environment variable placeholders, metadata, and audit-ready change records.

The current foundation does not use external secret managers, network services, or databases.

## Automation Execution

The Automation Service records when a workflow would be triggered by a cron schedule, manual action, event payload, workflow event, or condition. It preserves execution history and retry policy metadata, but it does not invoke workflow handlers or depend on an external scheduler.

## Example Workflow: Daily Intelligence Summary

Purpose:

- Prepare the context and decision inputs needed for a daily intelligence summary.

Typical steps:

1. Load current context.
2. Evaluate decision rules.
3. Stage summary inputs.
4. Route staged material to product preparation.
5. Run QA.
6. Send to review queue.
7. Distribute approved output through dry-run or local channels.

Expected controls:

- Scenario context must be current.
- Training objectives must be represented.
- Source references must be preserved.
- Generated or prepared content must remain notional.

## Example Workflow: Breaking News Inject

Purpose:

- Convert a real-world or exercise event into a controlled inject candidate.

Typical steps:

1. Load event context.
2. Translate event terms into scenario language.
3. Determine whether an inject is required.
4. Stage inject inputs.
5. Prepare product draft through the Product SDK.
6. Run QA and leakage checks.
7. Route to controller review.

Expected controls:

- Escalation-sensitive injects require senior controller approval.
- Real-world actor names must be translated or flagged.
- Confidence and source notes must be retained.

## Example Workflow: White Cell Morning Products

Purpose:

- Prepare morning controller products from current exercise state and control measures.

Typical steps:

1. Load daily context.
2. Check active control measures.
3. Stage white cell inputs.
4. Prepare selected product families.
5. Run QA.
6. Queue for review.

Expected controls:

- Current exercise day and phase must be correct.
- Control measures must be visible.
- Product content must support the controller battle rhythm.

## Example Workflow: Product Plugin Preparation

Purpose:

- Use a product plugin to format a controlled product candidate.

Typical steps:

1. Select product plugin.
2. Validate required context.
3. Format template fields.
4. Produce product output.
5. Run QA.
6. Queue for review.

Expected controls:

- Required fields must be present.
- Plugin version must be traceable.
- Output must not bypass review.

## Failure Handling

Workflows and pipelines should fail clearly. A failed step should preserve:

- Step or stage identifier
- Failure message
- Execution status
- Input metadata
- Partial results where safe
- Logs needed for triage

Failures should stop downstream execution when continuing could create misleading, incomplete, or unsafe products.

## Future Workflow Direction

Future workflow work should add:

- Profile-aware workflow selection
- Review queue integration
- Human approval events
- Export workflow stages
- Storage-backed artifact retention
- Cross-service search surfaces
- Audit-backed after-action review
- Metrics-backed health and performance snapshots
- Configuration-backed runtime selection
- Automation runtime integration
- Runtime observability
- Controller-facing workflow status
- Policy-based AI provider selection
- Stronger provenance and audit records
