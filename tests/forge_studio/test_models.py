from datetime import datetime, timezone

import pytest

from project_forge.forge_studio import (
    AuditLog,
    Exercise,
    ExercisePhase,
    ExerciseStatus,
    ForgeStudioRegistry,
    Inject,
    InjectPriority,
    InjectStatus,
    InjectType,
    ReviewDecision,
    ReviewItemType,
    StudioReviewItem,
    StudioReviewStatus,
    TimelineEvent,
    TimelineEventType,
    User,
    UserRole,
)
from project_forge.forge_studio.api import exercises, injects, review


def sample_exercise() -> Exercise:
    return Exercise(
        id="exercise-1",
        name="Forge Studio MVP Exercise",
        description="Notional service-level training exercise.",
        start_date=datetime(2026, 7, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 7, 10, tzinfo=timezone.utc),
    )


def sample_user(user_id: str = "user-reviewer", role: UserRole = UserRole.REVIEWER) -> User:
    return User(
        id=user_id,
        display_name="Reviewer One",
        email=f"{user_id}@example.test",
        role=role,
        organization="EXCON",
    )


def test_exercise_model_creation_and_status_transitions() -> None:
    exercise = sample_exercise()

    exercise.transition_status(ExerciseStatus.ACTIVE)
    exercise.transition_phase(ExercisePhase.EXECUTION)

    assert exercise.id == "exercise-1"
    assert exercise.status is ExerciseStatus.ACTIVE
    assert exercise.phase is ExercisePhase.EXECUTION
    assert exercise.updated_at >= exercise.created_at


def test_user_model_creation_with_required_roles() -> None:
    roles = {role.value for role in UserRole}

    user = User(
        id="user-director",
        display_name="Exercise Director",
        email="director@example.test",
        role=UserRole.EXERCISE_DIRECTOR,
        organization="Training Command",
    )

    assert user.active
    assert user.role is UserRole.EXERCISE_DIRECTOR
    assert roles == {
        "exercise_director",
        "intelligence_chief",
        "exercise_control_officer",
        "controller",
        "observer",
        "reviewer",
        "administrator",
    }


def test_inject_requires_human_approval_before_scheduling() -> None:
    inject = Inject(
        id="inject-1",
        exercise_id="exercise-1",
        title="Notional logistics disruption",
        inject_type=InjectType.LOGISTICS,
        priority=InjectPriority.HIGH,
        assigned_controller="user-controller",
        created_by="user-controller",
    )

    inject.submit_for_review()

    assert inject.status is InjectStatus.PENDING_REVIEW
    assert not inject.releasable
    with pytest.raises(ValueError):
        inject.schedule(datetime(2026, 7, 2, 12, 0, tzinfo=timezone.utc))

    inject.approve("user-reviewer")
    inject.schedule(datetime(2026, 7, 2, 12, 0, tzinfo=timezone.utc))

    assert inject.releasable
    assert inject.approved_by == "user-reviewer"
    assert inject.status is InjectStatus.SCHEDULED


def test_timeline_event_model_creation() -> None:
    event = TimelineEvent(
        id="timeline-1",
        exercise_id="exercise-1",
        event_type=TimelineEventType.INJECT,
        title="Inject scheduled",
        description="Controller scheduled inject for execution.",
        source="forge_studio",
        related_inject_id="inject-1",
    )

    assert event.exercise_id == "exercise-1"
    assert event.related_inject_id == "inject-1"
    assert event.event_type is TimelineEventType.INJECT


def test_review_queue_lifecycle_approves_inject_with_human_decision() -> None:
    registry = ForgeStudioRegistry()
    registry.register_exercise(sample_exercise())
    registry.register_user(sample_user("user-controller", UserRole.CONTROLLER))
    registry.register_user(sample_user("user-reviewer", UserRole.REVIEWER))
    registry.register_inject(
        Inject(
            id="inject-1",
            exercise_id="exercise-1",
            title="Media narrative shift",
            created_by="user-controller",
            assigned_controller="user-controller",
        )
    )
    item = StudioReviewItem(
        id="review-1",
        exercise_id="exercise-1",
        item_type=ReviewItemType.INJECT,
        item_id="inject-1",
    )
    registry.register_review_item(item)

    item.assign("user-reviewer")
    registry.approve_review_item("review-1", "user-reviewer", comments="Approved.")

    assert item.status is StudioReviewStatus.APPROVED
    assert item.decision is ReviewDecision.APPROVED
    assert item.reviewed_at is not None
    assert registry.get_inject("inject-1").status is InjectStatus.APPROVED
    assert registry.get_inject("inject-1").approved_by == "user-reviewer"


def test_review_rejection_keeps_inject_unreleasable() -> None:
    registry = ForgeStudioRegistry(
        exercises=[sample_exercise()],
        users=[
            sample_user("user-controller", UserRole.CONTROLLER),
            sample_user("user-reviewer", UserRole.REVIEWER),
        ],
    )
    registry.register_inject(
        Inject(id="inject-1", exercise_id="exercise-1", title="Unapproved inject")
    )
    registry.register_review_item(
        StudioReviewItem(
            id="review-1",
            exercise_id="exercise-1",
            item_type=ReviewItemType.INJECT,
            item_id="inject-1",
        )
    )

    registry.reject_review_item("review-1", "user-reviewer", comments="Needs sources.")

    assert registry.get_review_item("review-1").status is StudioReviewStatus.REJECTED
    assert registry.get_inject("inject-1").status is InjectStatus.REJECTED
    assert not registry.get_inject("inject-1").releasable


def test_audit_log_creation_and_registry_lookup() -> None:
    registry = ForgeStudioRegistry(exercises=[sample_exercise()])
    registry.register_user(sample_user("user-director", UserRole.EXERCISE_DIRECTOR))

    log = AuditLog(
        id="audit-1",
        exercise_id="exercise-1",
        actor_id="user-director",
        action="exercise.phase.updated",
        target_type="exercise",
        target_id="exercise-1",
        metadata={"from": "planning", "to": "execution"},
    )
    registry.register_audit_log(log)

    assert registry.get_audit_log("audit-1") is log
    assert registry.list_audit_logs("exercise-1") == [log]


def test_api_scaffold_routes_delegate_to_registry() -> None:
    registry = ForgeStudioRegistry()
    exercise = exercises.create_exercise(registry, sample_exercise())
    user = sample_user("user-controller", UserRole.CONTROLLER)
    registry.register_user(user)
    inject = injects.create_inject(
        registry,
        Inject(
            id="inject-1",
            exercise_id=exercise.id,
            title="Controller inject",
            created_by=user.id,
        ),
    )
    review_item = review.create_review_item(
        registry,
        StudioReviewItem(
            id="review-1",
            exercise_id=exercise.id,
            item_type=ReviewItemType.INJECT,
            item_id=inject.id,
        ),
    )

    exercises.update_exercise_status(registry, exercise.id, ExerciseStatus.PREPARING)
    injects.submit_inject_for_review(registry, inject.id)

    assert exercises.get_exercise(registry, exercise.id).status is ExerciseStatus.PREPARING
    assert injects.get_inject(registry, inject.id).status is InjectStatus.PENDING_REVIEW
    assert review.get_review_item(registry, review_item.id) is review_item


def test_registry_rejects_unknown_exercise_relationships() -> None:
    registry = ForgeStudioRegistry()

    with pytest.raises(ValueError):
        registry.register_inject(
            Inject(id="inject-1", exercise_id="missing", title="Missing exercise")
        )
