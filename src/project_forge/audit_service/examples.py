from __future__ import annotations

from .models import AuditAction, AuditActor, AuditCategory, AuditEvent
from .registry import AuditRegistry


def create_sample_audit_actor() -> AuditActor:
    """Create a safe sample audit actor."""

    return AuditActor(
        actor_id="service:pipeline-orchestrator",
        display_name="Pipeline Orchestrator",
        actor_type="service",
        metadata={"notional": True},
    )


def create_sample_audit_event() -> AuditEvent:
    """Create a sample service execution audit event."""

    return AuditEvent(
        event_id="audit-event-001",
        action=AuditAction.SERVICE_EXECUTION,
        category=AuditCategory.SERVICE,
        actor=create_sample_audit_actor(),
        summary="Pipeline stage executed",
        service="pipeline_orchestrator",
        correlation_id="correlation-001",
        tags=["pipeline", "service-execution"],
        metadata={"stage": "context"},
    )


def create_sample_audit_registry() -> AuditRegistry:
    """Create an audit registry containing one sample event."""

    registry = AuditRegistry()
    registry.record_event(create_sample_audit_event())
    return registry
