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
- Runtime observability
- Controller-facing workflow status
- Policy-based AI provider selection
- Stronger provenance and audit records
