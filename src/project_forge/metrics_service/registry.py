from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .models import Metric, MetricFilter, MetricReport, MetricSnapshot, MetricType, MetricValue
from .validator import MetricValidator


@dataclass(slots=True)
class MetricRegistry:
    """In-memory metric registry for Forge service metrics."""

    metrics: list[Metric] = field(default_factory=list)
    validator: MetricValidator = field(default_factory=MetricValidator)

    def __post_init__(self) -> None:
        self.validator.validate_metrics(self.metrics)
        self.metrics.sort(key=lambda metric: metric.metric_id)

    def register_metric(self, metric: Metric) -> None:
        if self.get_metric(metric.metric_id) is not None:
            raise ValueError(f"metric identifier already exists: {metric.metric_id}")
        self.validator.validate_metric(metric)
        self.metrics.append(metric)
        self.metrics.sort(key=lambda item: item.metric_id)

    def get_metric(self, metric_id: str) -> Metric | None:
        for metric in self.metrics:
            if metric.metric_id == metric_id:
                return metric
        return None

    def list_metrics(self) -> list[Metric]:
        return list(self.metrics)

    def record_value(
        self,
        metric_id: str,
        value: float,
        *,
        unit: str = "count",
        metadata: dict | None = None,
    ) -> MetricValue:
        metric = self.get_metric(metric_id)
        if metric is None:
            raise ValueError(f"metric not found: {metric_id}")
        metric_value = MetricValue(value=value, unit=unit, metadata=metadata or {})
        metric.record(metric_value)
        self.validator.validate_metric(metric)
        return metric_value

    def query(self, metric_filter: MetricFilter | None = None) -> list[Metric]:
        active_filter = metric_filter or MetricFilter()
        self.validator.validate_filter(active_filter)
        return [metric for metric in self.metrics if _matches(metric, active_filter)]

    def query_by_type(self, metric_type: MetricType) -> list[Metric]:
        return self.query(MetricFilter(metric_types=[metric_type]))

    def create_snapshot(
        self,
        snapshot_id: str | None = None,
        *,
        metric_filter: MetricFilter | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> MetricSnapshot:
        selected_metrics = self.query(metric_filter)
        snapshot = MetricSnapshot(
            snapshot_id=snapshot_id or f"metric-snapshot:{datetime.now(timezone.utc).isoformat()}",
            metrics=selected_metrics,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.validator.validate_snapshot(snapshot)
        return snapshot

    def create_report(
        self,
        report_id: str,
        *,
        snapshot: MetricSnapshot | None = None,
        metadata: dict | None = None,
    ) -> MetricReport:
        active_snapshot = snapshot or self.create_snapshot()
        report = MetricReport(
            report_id=report_id,
            snapshot=active_snapshot,
            summary={
                metric.metric_id: metric.aggregate_value()
                for metric in active_snapshot.metrics
            },
            metadata=metadata or {},
        )
        self.validator.validate_report(report)
        return report


def _matches(metric: Metric, metric_filter: MetricFilter) -> bool:
    if metric_filter.metric_types and metric.metric_type not in metric_filter.metric_types:
        return False
    if metric_filter.names and metric.name not in metric_filter.names:
        return False
    normalized_tags = {tag.lower() for tag in metric.tags}
    if metric_filter.tags and not all(tag.lower() in normalized_tags for tag in metric_filter.tags):
        return False
    for key, expected in metric_filter.metadata.items():
        if metric.metadata.get(key) != expected:
            return False
    return True


def create_default_metric_registry() -> MetricRegistry:
    """Create a registry with standard Forge operational metrics."""

    return MetricRegistry(metrics=create_default_metrics())


def create_default_metrics() -> list[Metric]:
    """Create standard metrics across Forge services."""

    return [
        Metric("workflow-executions", "workflow_executions", MetricType.COUNTER, tags=["workflow"]),
        Metric("products-generated", "products_generated", MetricType.COUNTER, tags=["product"]),
        Metric("review-queue-size", "review_queue_size", MetricType.GAUGE, tags=["review"]),
        Metric("qa-pass-fail-rate", "qa_pass_fail_rate", MetricType.GAUGE, tags=["qa"]),
        Metric("translation-operations", "translation_operations", MetricType.COUNTER, tags=["translation"]),
        Metric("ai-requests", "ai_requests", MetricType.COUNTER, tags=["ai"]),
        Metric("automation-executions", "automation_executions", MetricType.COUNTER, tags=["automation"]),
        Metric("search-requests", "search_requests", MetricType.COUNTER, tags=["search"]),
        Metric("distribution-events", "distribution_events", MetricType.COUNTER, tags=["distribution"]),
    ]
