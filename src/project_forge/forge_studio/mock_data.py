from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    AuditLog,
    Exercise,
    ExercisePhase,
    ExerciseStatus,
    Inject,
    InjectPriority,
    InjectStatus,
    InjectType,
    ReviewItemType,
    StudioReviewItem,
    StudioReviewStatus,
    TimelineEvent,
    TimelineEventType,
    User,
    UserRole,
)
from .registry import ForgeStudioRegistry


def create_mock_registry() -> ForgeStudioRegistry:
    """Create safe local mock data for the first Forge Studio web app."""

    exercise = Exercise(
        id="exercise-forge-demo",
        name="Forge Demo Exercise",
        description="Notional service-level training exercise for Forge Studio MVP.",
        status=ExerciseStatus.ACTIVE,
        phase=ExercisePhase.EXECUTION,
        start_date=datetime(2026, 7, 1, 8, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 7, 10, 17, 0, tzinfo=timezone.utc),
    )
    users = [
        User(
            id="user-exdir",
            display_name="Exercise Director",
            email="exercise.director@example.test",
            role=UserRole.EXERCISE_DIRECTOR,
            organization="EXCON",
        ),
        User(
            id="user-intel-chief",
            display_name="Intelligence Chief",
            email="intel.chief@example.test",
            role=UserRole.INTELLIGENCE_CHIEF,
            organization="Intelligence Cell",
        ),
        User(
            id="user-controller",
            display_name="Controller One",
            email="controller.one@example.test",
            role=UserRole.CONTROLLER,
            organization="White Cell",
        ),
        User(
            id="user-reviewer",
            display_name="Reviewer One",
            email="reviewer.one@example.test",
            role=UserRole.REVIEWER,
            organization="Review Cell",
        ),
        User(
            id="user-observer",
            display_name="Observer One",
            email="observer.one@example.test",
            role=UserRole.OBSERVER,
            organization="Training Command",
        ),
    ]
    injects = [
        Inject(
            id="inject-001",
            exercise_id=exercise.id,
            title="Logistics Convoy Delay",
            description="Notional route disruption requiring controller review.",
            inject_type=InjectType.LOGISTICS,
            priority=InjectPriority.HIGH,
            status=InjectStatus.PENDING_REVIEW,
            assigned_controller="user-controller",
            created_by="user-controller",
        ),
        Inject(
            id="inject-002",
            exercise_id=exercise.id,
            title="Simulated Media Query",
            description="Media cell inject awaiting final timing.",
            inject_type=InjectType.MEDIA,
            priority=InjectPriority.MEDIUM,
            status=InjectStatus.APPROVED,
            assigned_controller="user-controller",
            created_by="user-intel-chief",
            approved_by="user-reviewer",
        ),
        Inject(
            id="inject-003",
            exercise_id=exercise.id,
            title="Exercise Control Update",
            description="Internal EXCON synchronization note.",
            inject_type=InjectType.EXERCISE_CONTROL,
            priority=InjectPriority.LOW,
            status=InjectStatus.DRAFT,
            assigned_controller="user-controller",
            created_by="user-exdir",
        ),
    ]
    timeline_events = [
        TimelineEvent(
            id="timeline-001",
            exercise_id=exercise.id,
            event_type=TimelineEventType.EXERCISE_PHASE,
            title="Execution Phase Started",
            description="Exercise moved from preparation into execution.",
            timestamp=datetime(2026, 7, 3, 8, 0, tzinfo=timezone.utc),
            source="exercise_control",
        ),
        TimelineEvent(
            id="timeline-002",
            exercise_id=exercise.id,
            event_type=TimelineEventType.INJECT,
            title="Approved Media Query Staged",
            description="Approved media inject staged for controller timing.",
            timestamp=datetime(2026, 7, 3, 10, 30, tzinfo=timezone.utc),
            source="forge_studio",
            related_inject_id="inject-002",
        ),
        TimelineEvent(
            id="timeline-003",
            exercise_id=exercise.id,
            event_type=TimelineEventType.REVIEW,
            title="Logistics Inject Entered Review",
            description="High-priority logistics inject awaiting human review.",
            timestamp=datetime(2026, 7, 3, 11, 15, tzinfo=timezone.utc),
            source="review_queue",
            related_inject_id="inject-001",
        ),
    ]
    review_items = [
        StudioReviewItem(
            id="review-001",
            exercise_id=exercise.id,
            item_type=ReviewItemType.INJECT,
            item_id="inject-001",
            status=StudioReviewStatus.PENDING,
            reviewer_id="user-reviewer",
        ),
        StudioReviewItem(
            id="review-002",
            exercise_id=exercise.id,
            item_type=ReviewItemType.PRODUCT,
            item_id="product-daily-intsum",
            status=StudioReviewStatus.IN_REVIEW,
            reviewer_id="user-reviewer",
            comments="Checking source traceability.",
        ),
    ]
    audit_logs = [
        AuditLog(
            id="audit-001",
            exercise_id=exercise.id,
            actor_id="user-exdir",
            action="exercise.phase.updated",
            target_type="exercise",
            target_id=exercise.id,
            timestamp=datetime(2026, 7, 3, 8, 0, tzinfo=timezone.utc),
            metadata={"phase": ExercisePhase.EXECUTION.value},
        ),
        AuditLog(
            id="audit-002",
            exercise_id=exercise.id,
            actor_id="user-controller",
            action="inject.review.submitted",
            target_type="inject",
            target_id="inject-001",
            timestamp=datetime(2026, 7, 3, 11, 15, tzinfo=timezone.utc),
            metadata={"status": InjectStatus.PENDING_REVIEW.value},
        ),
    ]

    return ForgeStudioRegistry(
        exercises=[exercise],
        users=users,
        injects=injects,
        timeline_events=timeline_events,
        review_items=review_items,
        audit_logs=audit_logs,
    )
