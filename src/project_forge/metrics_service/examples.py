from __future__ import annotations

from .collector import MetricCollector
from .registry import create_default_metric_registry


def create_sample_metric_registry():
    """Create a sample registry with standard Forge metrics and values."""

    registry = create_default_metric_registry()
    registry.record_value("workflow-executions", 1)
    registry.record_value("products-generated", 2)
    registry.record_value("review-queue-size", 3)
    return registry


def create_sample_metric_collector() -> MetricCollector:
    """Create a collector using the standard metric registry."""

    return MetricCollector(registry=create_default_metric_registry())
