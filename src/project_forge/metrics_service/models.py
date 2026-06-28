from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    """Supported metric value types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    TIMER = "timer"
    HISTOGRAM = "histogram"


class MetricName(str, Enum):
    """Standard Forge operational metric names."""

    WORKFLOW_EXECUTIONS = "workflow_executions"
    PRODUCTS_GENERATED = "products_generated"
    REVIEW_QUEUE_SIZE = "review_queue_size"
    QA_PASS_FAIL_RATE = "qa_pass_fail_rate"
    TRANSLATION_OPERATIONS = "translation_operations"
    AI_REQUESTS = "ai_requests"
    AUTOMATION_EXECUTIONS = "automation_executions"
    SEARCH_REQUESTS = "search_requests"
    DISTRIBUTION_EVENTS = "distribution_events"


@dataclass(frozen=True, slots=True)
class MetricValue:
    """A recorded metric value with optional unit and timestamp."""

    value: float
    unit: str = "count"
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.value, int | float):
            raise ValueError("metric value must be numeric")
        _validate_non_empty("unit", self.unit)
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class Metric:
    """A registerable metric stream."""

    metric_id: str
    name: str
    metric_type: MetricType
    description: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    values: list[MetricValue] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_non_empty("metric_id", self.metric_id)
        _validate_non_empty("name", self.name)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)

    def record(self, value: MetricValue) -> None:
        self.values.append(value)

    @property
    def latest_value(self) -> MetricValue | None:
        if not self.values:
            return None
        return max(self.values, key=lambda value: value.recorded_at)

    def aggregate_value(self) -> float:
        if not self.values:
            return 0.0
        if self.metric_type is MetricType.COUNTER:
            return sum(value.value for value in self.values)
        if self.metric_type in {MetricType.GAUGE, MetricType.TIMER}:
            return self.latest_value.value if self.latest_value else 0.0
        return 0.0


@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    """Point-in-time metric state."""

    snapshot_id: str
    metrics: list[Metric]
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("snapshot_id", self.snapshot_id)
        if not all(isinstance(metric, Metric) for metric in self.metrics):
            raise ValueError("metrics must be a list of Metric instances")
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class MetricReport:
    """A local report object summarizing metric state."""

    report_id: str
    snapshot: MetricSnapshot
    summary: dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("report_id", self.report_id)
        if not isinstance(self.summary, dict) or not all(
            isinstance(key, str) and isinstance(value, int | float)
            for key, value in self.summary.items()
        ):
            raise ValueError("summary must be a dictionary of numeric values")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class MetricFilter:
    """Filters used to query metrics."""

    metric_types: list[MetricType] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_str_list("names", self.names)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError(f"{name} must be a list of non-empty strings")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
