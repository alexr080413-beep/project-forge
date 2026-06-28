from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from project_forge.ai_reasoning_engine import (
    AIContext,
    ModelConfiguration,
    OfflineStubProvider,
    PromptBuilder,
    PromptRegistry,
    PromptTemplate,
    TemplateRegistry,
)
from project_forge.ai_reasoning_engine.models import ProviderType
from project_forge.audit_service import (
    AuditAction,
    AuditActor,
    AuditCategory,
    AuditEvent,
    AuditRegistry,
    AuditSeverity,
)
from project_forge.context_engine import ContextBuilder
from project_forge.decision_engine import Decision, create_default_rules
from project_forge.decision_engine.models import DecisionContext
from project_forge.distribution_service import (
    DistributionItem,
    DistributionRequest,
    DistributionTarget,
    create_default_distribution_registry,
)
from project_forge.entity_engine import load_entities
from project_forge.event_engine import (
    EventImpact,
    EventRegistry,
    EventSeverity,
    EventSource,
    EventStatus,
    EventType,
    ExerciseEvent,
    load_events,
)
from project_forge.exercise_state import load_exercise_state
from project_forge.integration_service import (
    IntegrationRequest,
    IntegrationSource,
    IntegrationSourceType,
    create_default_integration_registry,
)
from project_forge.knowledge_engine import KnowledgeBaseLoader, KnowledgeDocumentType
from project_forge.metrics_service import create_default_metric_registry
from project_forge.pipeline_orchestrator import (
    Pipeline,
    PipelineContext,
    PipelineExecution,
    PipelineStage,
)
from project_forge.product_sdk import ProductFormatter, ProductRegistry, load_product_plugin
from project_forge.qa_service import QARegistry, QAStatus, create_default_qa_checks
from project_forge.review_queue import (
    ReviewItem,
    ReviewQueueManager,
    Reviewer,
    ReviewStatus,
)
from project_forge.scenario_engine import load_scenarios
from project_forge.storage_service import StorageLocation, create_default_storage_registry
from project_forge.translation_engine import (
    TranslationContext,
    TranslationPipeline,
    load_translation_dictionary,
)


DEMO_PIPELINE_IDENTIFIER = "forge-core-demo"
DEMO_EVENT_IDENTIFIER = "demo-real-world-event-001"


def create_end_to_end_demo_pipeline() -> Pipeline:
    """Create the local Project Forge end-to-end demo pipeline."""

    pipeline = Pipeline(
        identifier=DEMO_PIPELINE_IDENTIFIER,
        name="Forge Core End-to-End Demo",
        description=(
            "Runs a sample signal through local Forge services from intake to "
            "metrics snapshot without external APIs."
        ),
        metadata={"demo": True, "external_calls": False},
    )
    for stage in [
        _stage("sample-real-world-event", "Sample Real-World Event", "source_intake", _sample_event),
        _stage("integration-dry-run", "Integration Service Dry-Run", "integration_service", _integration_dry_run),
        _stage("storage", "Storage Service", "storage_service", _storage),
        _stage("knowledge-lookup", "Knowledge Lookup", "knowledge_engine", _knowledge_lookup),
        _stage("scenario-lookup", "Scenario Lookup", "scenario_engine", _scenario_lookup),
        _stage("entity-lookup", "Entity Lookup", "entity_engine", _entity_lookup),
        _stage("event-creation", "Event Creation", "event_engine", _event_creation),
        _stage("decision-engine", "Decision Engine", "decision_engine", _decision_engine),
        _stage("context-engine", "Context Engine", "context_engine", _context_engine),
        _stage("translation-engine", "Translation Engine", "translation_engine", _translation_engine),
        _stage("ai-reasoning-stub", "AI Reasoning Stub", "ai_reasoning_engine", _ai_reasoning_stub),
        _stage("product-sdk", "Product SDK Draft Output", "product_sdk", _product_sdk),
        _stage("qa-service", "QA Service", "qa_service", _qa_service),
        _stage("review-queue", "Review Queue", "review_queue", _review_queue),
        _stage("distribution-dry-run", "Distribution Dry-Run", "distribution_service", _distribution_dry_run),
        _stage("audit-log", "Audit Log", "audit_service", _audit_log),
        _stage("metrics-snapshot", "Metrics Snapshot", "metrics_service", _metrics_snapshot),
    ]:
        pipeline.register_stage(stage)
    return pipeline


def run_demo_pipeline() -> PipelineExecution:
    """Execute the end-to-end demo pipeline and return the full execution record."""

    return PipelineExecution(pipeline=create_end_to_end_demo_pipeline()).execute()


def _stage(identifier: str, name: str, service: str, handler) -> PipelineStage:
    return PipelineStage(
        identifier=identifier,
        name=name,
        service=service,
        handler=handler,
        metadata={"demo": True},
    )


def _sample_event(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    event = {
        "identifier": DEMO_EVENT_IDENTIFIER,
        "title": "Sample Real-World Coordination Signal",
        "summary": (
            "A sample open-source style report says Host Nation officials requested "
            "additional coordination from Joint Task Force Headquarters near the "
            "northern border region."
        ),
        "source_reference": "demo://sample-real-world-event",
        "observed_at": "2026-06-27T20:00:00Z",
        "related_entity": "unit-jtf-hq",
        "location": "Capital Operations Center",
        "notional": True,
    }
    return {
        "real_world_event": event,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "sample event prepared",
            event_identifier=event["identifier"],
        ),
    }


def _integration_dry_run(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    event = context.data["real_world_event"]
    source = IntegrationSource(
        source_id="demo-manual-signal",
        name="Demo Manual Signal",
        source_type=IntegrationSourceType.MANUAL_UPLOAD,
        location=event["source_reference"],
        metadata={"event_identifier": event["identifier"], "notional": True},
    )
    registry = create_default_integration_registry(sources=[source])
    request = IntegrationRequest(
        request_id="demo-integration-dry-run",
        source=source,
        dry_run=True,
        requested_by="EXCON Demo",
        metadata={"pipeline": DEMO_PIPELINE_IDENTIFIER},
    )
    result = registry.collect(request)
    return {
        "integration_source": source,
        "integration_result": result,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            result.status.value,
            connector=result.connector_identifier,
        ),
    }


def _storage(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    event = context.data["real_world_event"]
    registry = create_default_storage_registry()
    location = StorageLocation(
        location_id="demo-outputs",
        provider_identifier="output-folder",
        path="outputs",
        description="Demo output folder.",
        metadata={"demo": True},
    )
    result = registry.write(
        location,
        "demo/forge-core-demo-signal.txt",
        event["summary"],
        dry_run=True,
        requested_by="EXCON Demo",
    )
    return {
        "storage_location": location,
        "storage_result": result,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            result.status.value,
            artifact_path=result.artifact_path,
        ),
    }


def _knowledge_lookup(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    knowledge_base = KnowledgeBaseLoader("knowledge_base").load(name="demo")
    documents = knowledge_base.list_documents(KnowledgeDocumentType.BASE_DOCUMENTS)
    selected_document = documents[0] if documents else knowledge_base.list_documents()[0]
    return {
        "knowledge_base": knowledge_base,
        "knowledge_document": selected_document,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "knowledge document selected",
            document=str(selected_document.relative_path),
        ),
    }


def _scenario_lookup(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    scenario_registry = load_scenarios("config/scenario.example.yaml")
    scenario = scenario_registry.get_current_scenario()
    if scenario is None:
        raise ValueError("demo scenario not found")
    return {
        "scenario_registry": scenario_registry,
        "scenario": scenario,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "scenario selected",
            scenario_identifier=scenario.identifier,
        ),
    }


def _entity_lookup(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    event = context.data["real_world_event"]
    entity_catalog = load_entities("config/entities.example.yaml")
    entity = entity_catalog.get_entity(event["related_entity"])
    if entity is None:
        raise ValueError(f"demo entity not found: {event['related_entity']}")
    return {
        "entity_catalog": entity_catalog,
        "entity": entity,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "entity selected",
            entity_identifier=entity.identifier,
        ),
    }


def _event_creation(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    event = context.data["real_world_event"]
    existing_events = load_events("config/events.example.yaml")
    registry = EventRegistry(events=list(existing_events.events))
    exercise_event = ExerciseEvent(
        identifier=event["identifier"],
        title="Notional Coordination Signal Created From Sample Event",
        summary=event["summary"],
        event_type=EventType.POLITICAL,
        originating_source=EventSource.OPEN_SOURCE,
        scenario_actors_involved=["Host Nation Government", "Joint Task Force Headquarters"],
        locations_involved=[event["location"]],
        timestamp=datetime(2026, 6, 27, 20, 0, tzinfo=timezone.utc),
        exercise_day=context.data["scenario"].current_exercise_day,
        exercise_phase=context.data["scenario"].current_phase.value,
        confidence=0.88,
        impacts=[
            EventImpact(
                area="decision_rhythm",
                severity=EventSeverity.MEDIUM,
                summary="Controllers may need a notional coordination update.",
                affected_entities=[context.data["entity"].identifier, "org-excon"],
            )
        ],
        related_entities=[context.data["entity"].identifier, "org-excon"],
        supporting_source_references=[
            event["source_reference"],
            str(context.data["knowledge_document"].relative_path),
        ],
        tags=["demo", "coordination"],
        metadata={"notional": True, "source_event": event["identifier"]},
        status=EventStatus.ACTIVE,
    )
    registry.add_event(exercise_event)
    return {
        "event_registry": registry,
        "exercise_event": exercise_event,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "exercise event created",
            event_identifier=exercise_event.identifier,
            event_count=len(registry.events),
        ),
    }


def _decision_engine(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    exercise_state = load_exercise_state("config/exercise_state.example.yaml")
    decision_context = DecisionContext(
        exercise_state=exercise_state,
        scenario=context.data["scenario"],
        events=[context.data["exercise_event"]],
        entities=context.data["entity_catalog"],
        training_objectives=["Validate EXCON decision rhythm"],
        escalation_rules=["Senior Controller approval required."],
        metadata={"demo": True},
    )
    decision = Decision(identifier="demo-decision", rules=create_default_rules())
    decision_result = decision.execute(decision_context)
    return {
        "exercise_state": exercise_state,
        "decision_result": decision_result,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            decision_result.outcome.value,
            evaluations=len(decision_result.evaluations),
        ),
    }


def _context_engine(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    builder = ContextBuilder(
        knowledge_base=context.data["knowledge_base"],
        exercise_state=context.data["exercise_state"],
        scenario_registry=context.data["scenario_registry"],
        entity_catalog=context.data["entity_catalog"],
        event_registry=context.data["event_registry"],
        decision_results=[context.data["decision_result"]],
        training_objectives=["Validate EXCON decision rhythm"],
        metadata={"demo": True},
    )
    snapshot = builder.build_event_context(context.data["exercise_event"].identifier)
    return {
        "context_snapshot": snapshot,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "event context built",
            references=len(snapshot.exercise_context.references),
        ),
    }


def _translation_engine(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    registry = load_translation_dictionary("config/translation_dictionaries.example.yaml")
    dictionary = registry.get_dictionary("forge-example-translation")
    if dictionary is None:
        raise ValueError("demo translation dictionary not found")
    text = context.data["exercise_event"].summary
    result = TranslationPipeline(dictionary).translate(
        TranslationContext(
            text=text,
            profile_identifier="exercise-products",
            metadata={"demo": True},
        )
    )
    return {
        "translation_registry": registry,
        "translation_result": result,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "translation complete",
            applied_rules=len(result.applied_rule_identifiers),
        ),
    }


def _ai_reasoning_stub(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    template = PromptTemplate(
        identifier="demo-scenario-reasoning",
        version="1.0.0",
        system_prompt="You assist EXCON with notional scenario reasoning.",
        user_template=(
            "Use the deterministic context below.\n"
            "{context_summary}\n"
            "Instructions:\n"
            "{instructions}"
        ),
        metadata={"demo": True},
    )
    template_registry = TemplateRegistry(templates=[template])
    ai_context = AIContext(
        context_snapshot=context.data["context_snapshot"],
        translation_result=context.data["translation_result"],
        instructions=[
            "Preserve notional exercise boundaries.",
            "Prepare a concise draft path only.",
        ],
        metadata={"demo": True},
    )
    request = PromptBuilder().build_request(
        template=template_registry.get_template("demo-scenario-reasoning", "1.0.0"),
        ai_context=ai_context,
        model_configuration=ModelConfiguration(
            provider_type=ProviderType.OFFLINE_STUB,
            model_name="offline-stub-model",
            temperature=0.0,
            max_tokens=500,
        ),
    )
    prompt_registry = PromptRegistry()
    prompt_registry.register_request(request)
    response = OfflineStubProvider(
        content="Stub reasoning complete: create a notional coordination summary draft."
    ).generate(request)
    return {
        "prompt_template_registry": template_registry,
        "prompt_registry": prompt_registry,
        "ai_request": request,
        "ai_response": response,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "offline stub response generated",
            provider=response.provider_type.value,
        ),
    }


def _product_sdk(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    plugin = load_product_plugin("config/product_plugins/intelligence_summary.yaml")
    registry = ProductRegistry(plugins=[plugin])
    output = ProductFormatter().format(
        plugin,
        {
            "title": "Notional Coordination Update",
            "summary": context.data["translation_result"].translated_text,
            "key_judgments": context.data["ai_response"].content,
        },
    )
    return {
        "product_registry": registry,
        "product_output": output,
        "product_payload": _product_payload(context, output.content),
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "draft product formatted",
            product_identifier=output.product_identifier,
            output_format=output.output_format,
        ),
    }


def _qa_service(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    registry = QARegistry(checks=create_default_qa_checks())
    report = registry.run_checks(context.data["product_payload"])
    return {
        "qa_registry": registry,
        "qa_report": report,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            report.status.value,
            findings=len(report.findings),
        ),
    }


def _review_queue(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    if context.data["qa_report"].status is not QAStatus.PASS:
        raise ValueError("demo product must pass QA before review queue")
    manager = ReviewQueueManager()
    queue = manager.create_queue("demo-review", "Demo Review Queue", metadata={"demo": True})
    output = context.data["product_output"]
    item = ReviewItem(
        item_id="demo-review-item-001",
        product_identifier=output.product_identifier,
        product_type="intelligence_summary",
        title="Notional Coordination Update",
        priority=90,
        metadata={"demo": True, "source_event": context.data["exercise_event"].identifier},
    )
    manager.add_item(queue.identifier, item)
    reviewer = Reviewer(
        reviewer_id="controller-demo",
        display_name="Demo Controller",
        role="EXCON",
        metadata={"demo": True},
    )
    manager.assign_reviewer(queue.identifier, item.item_id, reviewer, note="Demo review assigned.")
    approved = manager.approve(
        queue.identifier,
        item.item_id,
        reviewer,
        note="Approved for dry-run distribution.",
    )
    return {
        "review_manager": manager,
        "review_queue": queue,
        "review_item": approved,
        "reviewer": reviewer,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            approved.status.value,
            queue_size=len(queue.list_items()),
        ),
    }


def _distribution_dry_run(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    review_item = context.data["review_item"]
    item = DistributionItem(
        item_id="demo-distribution-item-001",
        product_identifier=context.data["product_output"].product_identifier,
        product_type=review_item.product_type,
        content=context.data["product_output"].content,
        output_format=context.data["product_output"].output_format,
        approved=review_item.status is ReviewStatus.APPROVED,
        metadata={"demo": True, "review_item_id": review_item.item_id},
    )
    request = DistributionRequest(
        request_id="demo-distribution-dry-run",
        item=item,
        channel_identifier="markdown",
        target=DistributionTarget(
            identifier="demo-markdown-preview",
            target_type="markdown",
            destination="outputs/demo/notional-coordination-update.md",
            metadata={"demo": True},
        ),
        dry_run=True,
        requested_by="EXCON Demo",
        metadata={"demo": True},
    )
    result = create_default_distribution_registry().distribute(request)
    return {
        "distribution_item": item,
        "distribution_request": request,
        "distribution_result": result,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            result.status.value,
            channel=result.channel_identifier,
        ),
    }


def _audit_log(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    registry = AuditRegistry()
    actor = AuditActor(
        actor_id="system:forge-core-demo",
        display_name="Forge Core Demo Pipeline",
        actor_type="system",
        metadata={"demo": True},
    )
    session = registry.start_session(
        "demo-audit-session",
        actor,
        DEMO_PIPELINE_IDENTIFIER,
        tags=["demo", "pipeline"],
        metadata={"stage_count": len(_stage_summaries(context))},
    )
    for index, summary in enumerate(_stage_summaries(context), start=1):
        registry.record_event(
            _audit_event_for_stage(actor, summary, index),
            session_id=session.session_id,
        )
    registry.close_session(session.session_id)
    return {
        "audit_registry": registry,
        "audit_session": registry.get_session(session.session_id),
        "audit_entries": registry.list_entries(),
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "audit events recorded",
            entries=len(registry.list_entries()),
        ),
    }


def _metrics_snapshot(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    registry = create_default_metric_registry()
    registry.record_value("workflow-executions", 1, metadata={"pipeline": DEMO_PIPELINE_IDENTIFIER})
    registry.record_value("products-generated", 1, metadata={"pipeline": DEMO_PIPELINE_IDENTIFIER})
    registry.record_value(
        "review-queue-size",
        len(context.data["review_queue"].list_items()),
        metadata={"pipeline": DEMO_PIPELINE_IDENTIFIER},
    )
    qa_status = context.data["qa_report"].status
    registry.record_value(
        "qa-pass-fail-rate",
        1.0 if qa_status is QAStatus.PASS else 0.0,
        unit="ratio",
        metadata={"qa_status": qa_status.value},
    )
    registry.record_value("translation-operations", 1, metadata={"pipeline": DEMO_PIPELINE_IDENTIFIER})
    registry.record_value("ai-requests", 1, metadata={"provider": ProviderType.OFFLINE_STUB.value})
    registry.record_value("distribution-events", 1, metadata={"dry_run": True})
    snapshot = registry.create_snapshot(
        "demo-metrics-snapshot",
        tags=["demo", "pipeline"],
        metadata={"pipeline": DEMO_PIPELINE_IDENTIFIER},
    )
    report = registry.create_report("demo-metrics-report", snapshot=snapshot)
    return {
        "metric_registry": registry,
        "metrics_snapshot": snapshot,
        "metrics_report": report,
        "stage_summary": _append_stage_summary(
            context,
            stage,
            "metrics snapshot captured",
            metric_count=len(snapshot.metrics),
        ),
    }


def _product_payload(context: PipelineContext, content: str) -> dict[str, Any]:
    event = context.data["exercise_event"]
    return {
        "product_identifier": "intelligence-summary",
        "report_type": "intelligence_summary",
        "content": content,
        "exercise_day": event.exercise_day,
        "confidence": event.confidence,
        "source_references": list(event.supporting_source_references),
        "metadata": {
            "demo": True,
            "event_identifier": event.identifier,
            "ai_request_identifier": context.data["ai_request"].identifier,
        },
    }


def _audit_event_for_stage(
    actor: AuditActor,
    summary: dict[str, Any],
    index: int,
) -> AuditEvent:
    service = str(summary["service"])
    action, category = _audit_action_category(service)
    return AuditEvent(
        event_id=f"demo-audit-{index:03d}-{summary['stage']}",
        action=action,
        category=category,
        actor=actor,
        summary=f"Demo stage {summary['stage']} completed: {summary['status']}",
        service=service,
        correlation_id=DEMO_PIPELINE_IDENTIFIER,
        severity=AuditSeverity.INFO,
        tags=["demo", "pipeline", str(summary["stage"])],
        metadata={
            "stage": summary["stage"],
            "status": summary["status"],
            "details": summary["details"],
        },
    )


def _audit_action_category(service: str) -> tuple[AuditAction, AuditCategory]:
    if service == "ai_reasoning_engine":
        return AuditAction.AI_REQUEST, AuditCategory.AI
    if service == "product_sdk":
        return AuditAction.PRODUCT_GENERATION, AuditCategory.PRODUCT
    if service == "distribution_service":
        return AuditAction.DISTRIBUTION, AuditCategory.DISTRIBUTION
    if service == "review_queue":
        return AuditAction.REVIEW_ACTION, AuditCategory.REVIEW
    return AuditAction.SERVICE_EXECUTION, AuditCategory.SERVICE


def _append_stage_summary(
    context: PipelineContext,
    stage: PipelineStage,
    status: str,
    **details: Any,
) -> list[dict[str, Any]]:
    summaries = _stage_summaries(context)
    summaries.append(
        {
            "stage": stage.identifier,
            "service": stage.service,
            "status": status,
            "details": details,
        }
    )
    return summaries


def _stage_summaries(context: PipelineContext) -> list[dict[str, Any]]:
    return list(context.data.get("stage_summary", []))
