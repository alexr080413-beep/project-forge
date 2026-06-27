from datetime import datetime, timezone

import pytest

from project_forge.models import (
    ExerciseContext,
    GeneratedReport,
    QualityCheckResult,
    ReportRequest,
    ReviewStatus,
    ScenarioActor,
    ScenarioLocation,
    ScenarioMapping,
    SourceItem,
    TrainingObjective,
)


def test_models_can_be_created_with_valid_values() -> None:
    source = SourceItem(
        id="source-1",
        title="Initial report",
        source_type="news",
        content="A short report body.",
        published_at=datetime(2026, 6, 27, 12, 0, tzinfo=timezone.utc),
    )

    objective = TrainingObjective(id="obj-1", name="Scenario awareness", description="Understand the scenario")
    actor = ScenarioActor(id="actor-1", name="Chief Analyst", role="Controller", affiliation="EXCON")
    location = ScenarioLocation(id="loc-1", name="Operations Center", description="Main coordination hub")
    mapping = ScenarioMapping(
        id="map-1",
        source_item_id=source.id,
        actor_ids=[actor.id],
        location_ids=[location.id],
    )

    context = ExerciseContext(
        id="ctx-1",
        name="Exercise Horizon",
        description="A fictional exercise context",
        objectives=[objective],
        actors=[actor],
        locations=[location],
        mappings=[mapping],
    )

    request = ReportRequest(
        id="req-1",
        request_type="situation-update",
        source_item_id=source.id,
        exercise_context_id=context.id,
        requested_by="analyst",
    )

    quality_check = QualityCheckResult(id="qc-1", check_name="fiction-boundary", passed=True, details="Within allowed fiction")
    report = GeneratedReport(
        id="report-1",
        report_type="situation-update",
        request_id=request.id,
        content="This is a notional report.",
        status=ReviewStatus.DRAFT,
        quality_checks=[quality_check],
    )

    assert source.title == "Initial report"
    assert context.objectives[0].name == "Scenario awareness"
    assert request.request_type == "situation-update"
    assert report.status is ReviewStatus.DRAFT
    assert report.quality_checks[0].passed is True


def test_source_item_validation_rejects_blank_values() -> None:
    with pytest.raises(ValueError):
        SourceItem(id="source-2", title="   ", source_type="news", content="")


def test_generated_report_validation_rejects_blank_content() -> None:
    with pytest.raises(ValueError):
        GeneratedReport(id="report-2", report_type="situation-update", request_id="req-2", content="   ")
