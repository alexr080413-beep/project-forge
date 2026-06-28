from __future__ import annotations

from typing import Any

from .models import Pipeline, PipelineContext, PipelineStage


def create_real_world_event_pipeline() -> Pipeline:
    """Create the local example pipeline spanning the Project Forge services."""

    pipeline = Pipeline(
        identifier="real-world-event",
        name="Real World Event Pipeline",
        description="Coordinates a real-world event into the local review queue.",
        metadata={"example": True},
    )
    for stage in [
        PipelineStage(
            identifier="real-world-event",
            name="Real World Event",
            service="source_intake",
            handler=_real_world_event_stage,
        ),
        PipelineStage(
            identifier="context",
            name="Context",
            service="context_engine",
            handler=_context_stage,
        ),
        PipelineStage(
            identifier="translation",
            name="Translation",
            service="translation_engine",
            handler=_translation_stage,
        ),
        PipelineStage(
            identifier="ai-reasoning",
            name="AI Reasoning",
            service="ai_reasoning_engine",
            handler=_ai_reasoning_stage,
        ),
        PipelineStage(
            identifier="product-sdk",
            name="Product SDK",
            service="product_sdk",
            handler=_product_sdk_stage,
        ),
        PipelineStage(
            identifier="qa",
            name="QA",
            service="qa_service",
            handler=_qa_stage,
        ),
        PipelineStage(
            identifier="review-queue",
            name="Review Queue",
            service="review_queue",
            handler=_review_queue_stage,
        ),
    ]:
        pipeline.register_stage(stage)
    return pipeline


def _real_world_event_stage(
    context: PipelineContext,
    stage: PipelineStage,
) -> dict[str, Any]:
    event = context.data.get("real_world_event") or {
        "identifier": "event-001",
        "title": "Real-world event reference",
        "source_type": "local-example",
    }
    return {"real_world_event": event, stage.identifier: True}


def _context_stage(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    event = context.data["real_world_event"]
    return {
        "context": {
            "event_identifier": event["identifier"],
            "scenario_boundary": "exercise-only",
        },
        stage.identifier: True,
    }


def _translation_stage(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    return {
        "translation": {
            "source_event": context.data["real_world_event"]["identifier"],
            "notional_actor": "Asteria",
        },
        stage.identifier: True,
    }


def _ai_reasoning_stage(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    return {
        "reasoning": {
            "assessment": "scenario-consistent draft path selected",
            "uses_external_api": False,
        },
        stage.identifier: True,
    }


def _product_sdk_stage(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    return {
        "product": {
            "product_identifier": "notional-product-001",
            "content": "Draft notional exercise product queued for QA.",
            "source_event": context.data["real_world_event"]["identifier"],
        },
        stage.identifier: True,
    }


def _qa_stage(context: PipelineContext, stage: PipelineStage) -> dict[str, Any]:
    product = context.data["product"]
    return {
        "qa": {
            "product_identifier": product["product_identifier"],
            "status": "pass",
            "findings": [],
        },
        stage.identifier: True,
    }


def _review_queue_stage(
    context: PipelineContext,
    stage: PipelineStage,
) -> dict[str, Any]:
    product = context.data["product"]
    return {
        "review_queue": {
            "product_identifier": product["product_identifier"],
            "status": "queued",
        },
        stage.identifier: True,
    }
