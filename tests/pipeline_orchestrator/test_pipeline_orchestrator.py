import pytest

from project_forge.pipeline_orchestrator import (
    Pipeline,
    PipelineContext,
    PipelineExecution,
    PipelineRegistry,
    PipelineStage,
    PipelineStatus,
    create_real_world_event_pipeline,
)


def test_stages_register_dynamically_and_execute_in_order() -> None:
    calls: list[str] = []
    pipeline = Pipeline(
        identifier="custom",
        name="Custom",
        description="Custom deterministic pipeline.",
    )

    def handler(context, stage):
        calls.append(stage.identifier)
        return {stage.identifier: len(calls)}

    pipeline.register_stage(
        PipelineStage(
            identifier="first",
            name="First",
            service="one",
            handler=handler,
        )
    )
    pipeline.register_stage(
        PipelineStage(
            identifier="second",
            name="Second",
            service="two",
            handler=handler,
        )
    )

    execution = PipelineExecution(pipeline=pipeline).execute()

    assert execution.status is PipelineStatus.SUCCEEDED
    assert calls == ["first", "second"]
    assert execution.context.data == {"first": 1, "second": 2}
    assert [result.stage_identifier for result in execution.results] == [
        "first",
        "second",
    ]


def test_execution_logs_and_metadata_are_recorded() -> None:
    pipeline = Pipeline(
        identifier="metadata",
        name="Metadata",
        description="Checks metadata.",
        stages=[
            PipelineStage(
                identifier="stage",
                name="Stage",
                service="metadata-service",
                handler=lambda context, stage: {"value": True},
            )
        ],
    )

    execution = PipelineExecution(
        pipeline=pipeline,
        context=PipelineContext(metadata={"exercise_day": 3}),
        metadata={"requested_by": "controller"},
    ).execute()

    assert execution.metadata["requested_by"] == "controller"
    assert execution.context.metadata["exercise_day"] == 3
    assert execution.execution_log == [
        "pipeline metadata started",
        "stage stage started",
        "stage stage succeeded",
        "pipeline metadata succeeded",
    ]
    assert execution.results[0].metadata == {
        "service": "metadata-service",
        "input_keys": [],
        "output_keys": ["value"],
    }


def test_failure_handling_stops_remaining_stages() -> None:
    calls: list[str] = []

    def fail(context, stage):
        calls.append(stage.identifier)
        raise RuntimeError("boom")

    def succeed(context, stage):
        calls.append(stage.identifier)
        return {"should_not_run": True}

    pipeline = Pipeline(
        identifier="failure",
        name="Failure",
        description="Checks failures.",
        stages=[
            PipelineStage(
                identifier="first",
                name="First",
                service="one",
                handler=fail,
            ),
            PipelineStage(
                identifier="second",
                name="Second",
                service="two",
                handler=succeed,
            ),
        ],
    )

    execution = PipelineExecution(pipeline=pipeline).execute()

    assert execution.status is PipelineStatus.FAILED
    assert calls == ["first"]
    assert len(execution.results) == 1
    assert execution.results[0].status is PipelineStatus.FAILED
    assert execution.results[0].message == "boom"
    assert execution.execution_log[-1] == "pipeline failure failed"


def test_pipeline_registry_registers_pipelines_and_stages() -> None:
    stage = PipelineStage(
        identifier="registered-stage",
        name="Registered Stage",
        service="registry",
        handler=lambda context, stage: {"registered": True},
    )
    pipeline = Pipeline(
        identifier="registered-pipeline",
        name="Registered Pipeline",
        description="Pipeline registered in memory.",
    )
    pipeline.register_stage(stage)
    registry = PipelineRegistry()

    registry.register_stage(stage)
    registry.register_pipeline(pipeline)
    execution = registry.execute_pipeline("registered-pipeline")

    assert registry.get_stage("registered-stage") is stage
    assert registry.get_pipeline("registered-pipeline") is pipeline
    assert execution.status is PipelineStatus.SUCCEEDED
    assert execution.context.data["registered"] is True


def test_duplicate_stage_registration_is_rejected() -> None:
    stage = PipelineStage(
        identifier="duplicate",
        name="Duplicate",
        service="test",
        handler=lambda context, stage: {},
    )
    pipeline = Pipeline(
        identifier="duplicates",
        name="Duplicates",
        description="Rejects duplicate stages.",
        stages=[stage],
    )

    with pytest.raises(ValueError):
        pipeline.register_stage(stage)


def test_real_world_event_example_pipeline_is_deterministic() -> None:
    pipeline = create_real_world_event_pipeline()

    first = PipelineExecution(pipeline=pipeline).execute()
    second = PipelineExecution(pipeline=pipeline).execute()

    assert first.status is PipelineStatus.SUCCEEDED
    assert second.status is PipelineStatus.SUCCEEDED
    assert [stage.identifier for stage in pipeline.stages] == [
        "real-world-event",
        "context",
        "translation",
        "ai-reasoning",
        "product-sdk",
        "qa",
        "review-queue",
    ]
    assert first.context.data == second.context.data
    assert first.context.data["reasoning"]["uses_external_api"] is False
    assert first.context.data["review_queue"]["status"] == "queued"
