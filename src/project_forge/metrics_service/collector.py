from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter

from .models import Metric, MetricType, MetricValue
from .registry import MetricRegistry


@dataclass(slots=True)
class MetricCollector:
    """Convenience facade for recording local metric values."""

    registry: MetricRegistry = field(default_factory=MetricRegistry)

    def ensure_metric(
        self,
        metric_id: str,
        name: str,
        metric_type: MetricType,
        *,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> Metric:
        metric = self.registry.get_metric(metric_id)
        if metric is not None:
            return metric
        metric = Metric(
            metric_id=metric_id,
            name=name,
            metric_type=metric_type,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.registry.register_metric(metric)
        return metric

    def increment(
        self,
        metric_id: str,
        amount: float = 1,
        *,
        unit: str = "count",
        metadata: dict | None = None,
    ) -> MetricValue:
        return self.registry.record_value(metric_id, amount, unit=unit, metadata=metadata)

    def set_gauge(
        self,
        metric_id: str,
        value: float,
        *,
        unit: str = "count",
        metadata: dict | None = None,
    ) -> MetricValue:
        return self.registry.record_value(metric_id, value, unit=unit, metadata=metadata)

    def record_timer(
        self,
        metric_id: str,
        duration_ms: float,
        *,
        metadata: dict | None = None,
    ) -> MetricValue:
        return self.registry.record_value(metric_id, duration_ms, unit="milliseconds", metadata=metadata)

    def measure_elapsed_ms(self) -> float:
        start = perf_counter()
        return (perf_counter() - start) * 1000
