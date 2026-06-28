from datetime import datetime, timezone

import pytest

from project_forge.audit_service import (
    AuditAction,
    AuditActor,
    AuditCategory,
    AuditEvent,
    AuditFilter,
    AuditRegistry,
    AuditSeverity,
    AuditValidator,
    create_default_audit_registry,
    create_sample_audit_event,
    create_sample_audit_registry,
)


def actor(actor_id: str = "controller:one") -> AuditActor:
    return AuditActor(
        actor_id=actor_id,
        display_name="Controller One",
        actor_type="human",
    )


def event(
    event_id: str = "event-1",
    *,
    action: AuditAction = AuditAction.SERVICE_EXECUTION,
    category: AuditCategory = AuditCategory.SERVICE,
    service: str = "context_engine",
    parent_event_id: str = "",
    correlation_id: str = "correlation-1",
    severity: AuditSeverity = AuditSeverity.INFO,
    tags: list[str] | None = None,
    metadata: dict | None = None,
    occurred_at: datetime | None = None,
) -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        action=action,
        category=category,
        actor=actor(),
        summary="Action recorded",
        service=service,
        parent_event_id=parent_event_id,
        correlation_id=correlation_id,
        severity=severity,
        tags=tags or ["trace"],
        metadata=metadata or {"notional": True},
        occurred_at=occurred_at or datetime(2026, 1, 2, tzinfo=timezone.utc),
    )


def test_audit_events_validate_correctly() -> None:
    AuditValidator().validate_event(event())


def test_invalid_action_category_fails_validation() -> None:
    with pytest.raises(ValueError):
        AuditValidator().validate_event(
            event(action=AuditAction.APPROVAL, category=AuditCategory.REVIEW, service="")
        )


def test_service_oriented_events_require_service() -> None:
    with pytest.raises(ValueError):
        AuditValidator().validate_event(event(service=""))


def test_ai_request_metadata_only_rejects_prompt_content() -> None:
    with pytest.raises(ValueError):
        AuditValidator().validate_event(
            event(
                action=AuditAction.AI_REQUEST,
                category=AuditCategory.AI,
                service="ai_reasoning_engine",
                metadata={"model": "offline-stub", "prompt": "secret content"},
            )
        )


def test_registry_records_events() -> None:
    registry = create_default_audit_registry()
    entry = registry.record_event(event())

    assert entry.entry_id == "audit-entry:event-1"
    assert registry.get_entry_by_event_id("event-1") is entry
    assert registry.list_entries() == [entry]


def test_events_can_be_queried_by_category() -> None:
    registry = AuditRegistry()
    registry.record_event(event("service"))
    registry.record_event(
        event(
            "approval",
            action=AuditAction.APPROVAL,
            category=AuditCategory.APPROVAL,
            service="",
        )
    )

    results = registry.query_by_category(AuditCategory.APPROVAL)

    assert [entry.event.event_id for entry in results] == ["approval"]


def test_registry_records_all_required_action_types() -> None:
    assert {action.value for action in AuditAction} == {
        "service_execution",
        "workflow_execution",
        "review_action",
        "approval",
        "rejection",
        "configuration_change",
        "profile_selection",
        "ai_request",
        "product_generation",
        "distribution",
        "automation_execution",
    }


def test_parent_child_events_are_tracked() -> None:
    registry = AuditRegistry()
    registry.record_event(event("parent"))
    registry.record_event(event("child", parent_event_id="parent"))

    parent = registry.get_entry_by_event_id("parent")

    assert parent is not None
    assert parent.child_event_ids == ["child"]
    assert registry.query(AuditFilter(parent_event_id="parent"))[0].event.event_id == "child"


def test_sessions_group_events() -> None:
    registry = AuditRegistry()
    session = registry.start_session(
        "session-1",
        actor(),
        "correlation-1",
        tags=["exercise-day-1"],
    )
    entry = registry.record_event(event(), session_id=session.session_id)

    assert entry.session_id == "session-1"
    assert registry.get_session("session-1") is session


def test_missing_session_fails_recording() -> None:
    with pytest.raises(ValueError):
        AuditRegistry().record_event(event(), session_id="missing")


def test_filter_by_correlation_severity_tag_actor_service_metadata_and_date() -> None:
    registry = AuditRegistry()
    registry.record_event(
        event(
            "match",
            service="review_queue",
            correlation_id="corr-match",
            severity=AuditSeverity.WARNING,
            tags=["review", "approval"],
            metadata={"product_id": "product-1"},
            occurred_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
        )
    )
    registry.record_event(
        event(
            "other",
            service="context_engine",
            correlation_id="corr-other",
            occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    )

    results = registry.query(
        AuditFilter(
            categories=[AuditCategory.SERVICE],
            services=["review_queue"],
            actor_ids=["controller:one"],
            severities=[AuditSeverity.WARNING],
            tags=["approval"],
            correlation_id="corr-match",
            date_from=datetime(2026, 1, 2, tzinfo=timezone.utc),
            date_to=datetime(2026, 1, 4, tzinfo=timezone.utc),
            metadata={"product_id": "product-1"},
        )
    )

    assert [entry.event.event_id for entry in results] == ["match"]


def test_duplicate_events_are_rejected() -> None:
    registry = AuditRegistry()
    item = event()
    registry.record_event(item)

    with pytest.raises(ValueError):
        registry.record_event(item)


def test_duplicate_initial_entries_are_rejected() -> None:
    registry = AuditRegistry()
    first = registry.record_event(event())

    with pytest.raises(ValueError):
        AuditRegistry(entries=[first, first])


def test_sample_audit_registry_contains_sample_event() -> None:
    registry = create_sample_audit_registry()

    assert registry.query_by_category(AuditCategory.SERVICE)[0].event.event_id == (
        "audit-event-001"
    )


def test_sample_audit_event_validates() -> None:
    AuditValidator().validate_event(create_sample_audit_event())
