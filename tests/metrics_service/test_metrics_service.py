import pytest

from project_forge.metrics_service import (
    Metric,
    MetricCollector,
    MetricFilter,
    MetricName,
    MetricRegistry,
    MetricReport,
    MetricSnapshot,
    MetricType,
    MetricValidator,
    MetricValue,
    create_default_metric_registry,
    create_sample_metric_registry,
)


def metric(
    metric_id: str = "workflow-executions",
    *,
    name: str = "workflow_executions",
    metric_type: MetricType = MetricType.COUNTER,
) -> Metric:
    return Metric(
        metric_id=metric_id,
        name=name,
        metric_type=metric_type,
        tags=["workflow"],
        metadata={"service": "workflow_engine"},
    )


def test_metrics_register_successfully() -> None:
    registry = MetricRegistry()
    item = metric()

    registry.register_metric(item)

    assert registry.get_metric("workflow-executions") is item


def test_default_metrics_cover_required_services() -> None:
    registry = create_default_metric_registry()

    assert [item.name for item in registry.list_metrics()] == [
        "ai_requests",
        "automation_executions",
        "distribution_events",
        "products_generated",
        "qa_pass_fail_rate",
        "review_queue_size",
        "search_requests",
        "translation_operations",
        "workflow_executions",
    ]
    assert {item.value for item in MetricName} == set(item.name for item in registry.list_metrics())


def test_counter_values_aggregate() -> None:
    registry = MetricRegistry(metrics=[metric()])

    registry.record_value("workflow-executions", 1)
    registry.record_value("workflow-executions", 2)

    assert registry.get_metric("workflow-executions").aggregate_value() == 3


def test_gauge_uses_latest_value() -> None:
    item = metric(
        "review-queue-size",
        name="review_queue_size",
        metric_type=MetricType.GAUGE,
    )
    registry = MetricRegistry(metrics=[item])

    registry.record_value("review-queue-size", 4)
    registry.record_value("review-queue-size", 7)

    assert item.aggregate_value() == 7


def test_snapshots_can_be_created() -> None:
    registry = MetricRegistry(metrics=[metric()])
    registry.record_value("workflow-executions", 1)

    snapshot = registry.create_snapshot("snapshot-1")

    assert snapshot.snapshot_id == "snapshot-1"
    assert snapshot.metrics[0].metric_id == "workflow-executions"


def test_metrics_can_be_queried_by_type() -> None:
    registry = create_default_metric_registry()

    counters = registry.query_by_type(MetricType.COUNTER)

    assert "workflow_executions" in [item.name for item in counters]
    assert all(item.metric_type is MetricType.COUNTER for item in counters)


def test_metrics_can_be_queried_by_tags_and_metadata() -> None:
    registry = MetricRegistry(
        metrics=[
            metric(),
            Metric(
                "queue",
                "review_queue_size",
                MetricType.GAUGE,
                tags=["review"],
                metadata={"service": "review_queue"},
            ),
        ]
    )

    results = registry.query(
        MetricFilter(tags=["review"], metadata={"service": "review_queue"})
    )

    assert [item.metric_id for item in results] == ["queue"]


def test_metric_collector_records_values() -> None:
    collector = MetricCollector(registry=MetricRegistry(metrics=[metric()]))

    value = collector.increment("workflow-executions", 2)

    assert isinstance(value, MetricValue)
    assert collector.registry.get_metric("workflow-executions").aggregate_value() == 2


def test_metric_collector_can_register_missing_metric() -> None:
    collector = MetricCollector()

    item = collector.ensure_metric(
        "search-requests",
        "search_requests",
        MetricType.COUNTER,
        tags=["search"],
    )

    assert collector.registry.get_metric("search-requests") is item


def test_metric_report_summarizes_snapshot() -> None:
    registry = MetricRegistry(metrics=[metric()])
    registry.record_value("workflow-executions", 5)

    report = registry.create_report("report-1")

    assert isinstance(report, MetricReport)
    assert report.summary == {"workflow-executions": 5}


def test_negative_counter_fails_validation() -> None:
    item = metric()
    item.record(MetricValue(-1))

    with pytest.raises(ValueError):
        MetricValidator().validate_metric(item)


def test_histogram_values_are_placeholder_only() -> None:
    item = Metric("latency-histogram", "latency_histogram", MetricType.HISTOGRAM)
    item.record(MetricValue(12, unit="milliseconds"))

    with pytest.raises(NotImplementedError):
        MetricValidator().validate_metric(item)


def test_duplicate_metrics_are_rejected() -> None:
    item = metric()

    with pytest.raises(ValueError):
        MetricRegistry(metrics=[item, item])


def test_snapshot_validation_rejects_duplicate_metrics() -> None:
    item = metric()

    with pytest.raises(ValueError):
        MetricValidator().validate_snapshot(
            MetricSnapshot("snapshot", metrics=[item, item])
        )


def test_report_summary_keys_must_reference_snapshot_metrics() -> None:
    snapshot = MetricSnapshot("snapshot", metrics=[metric()])

    with pytest.raises(ValueError):
        MetricValidator().validate_report(
            MetricReport(
                report_id="report",
                snapshot=snapshot,
                summary={"missing": 1},
            )
        )


def test_sample_metric_registry_has_values() -> None:
    registry = create_sample_metric_registry()

    assert registry.get_metric("products-generated").aggregate_value() == 2
