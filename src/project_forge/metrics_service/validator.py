from __future__ import annotations

from .models import Metric, MetricFilter, MetricReport, MetricSnapshot, MetricType


class MetricValidator:
    """Validates metrics, snapshots, reports, and query filters."""

    def validate_metric(self, metric: Metric) -> None:
        if metric.metric_type is MetricType.COUNTER:
            for value in metric.values:
                if value.value < 0:
                    raise ValueError("counter metric values must not be negative")
        if metric.metric_type is MetricType.TIMER:
            for value in metric.values:
                if value.value < 0:
                    raise ValueError("timer metric values must not be negative")
        if metric.metric_type is MetricType.HISTOGRAM and metric.values:
            raise NotImplementedError("histogram metric collection is a placeholder")

    def validate_metrics(self, metrics: list[Metric]) -> None:
        identifiers = [metric.metric_id for metric in metrics]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("metric identifiers must be unique")
        for metric in metrics:
            self.validate_metric(metric)

    def validate_snapshot(self, snapshot: MetricSnapshot) -> None:
        self.validate_metrics(snapshot.metrics)

    def validate_report(self, report: MetricReport) -> None:
        self.validate_snapshot(report.snapshot)
        metric_ids = {metric.metric_id for metric in report.snapshot.metrics}
        for key in report.summary:
            if key not in metric_ids:
                raise ValueError("metric report summary keys must reference snapshot metrics")

    def validate_filter(self, metric_filter: MetricFilter) -> None:
        if not isinstance(metric_filter.metadata, dict):
            raise ValueError("metadata must be a dictionary")
