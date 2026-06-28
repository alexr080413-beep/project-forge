from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, TypeVar

from .models import (
    AuditLog,
    Exercise,
    Inject,
    ReviewDecision,
    StudioReviewItem,
    TimelineEvent,
    User,
)


class Identified(Protocol):
    id: str


T = TypeVar("T", bound=Identified)


@dataclass(slots=True)
class ForgeStudioRegistry:
    """In-memory Forge Studio MVP object registry.

    The registry is intentionally local and deterministic. It provides a narrow
    API surface for tests and future route adapters without implementing
    persistence, publishing, authentication, or network behavior.
    """

    exercises: list[Exercise] = field(default_factory=list)
    users: list[User] = field(default_factory=list)
    injects: list[Inject] = field(default_factory=list)
    timeline_events: list[TimelineEvent] = field(default_factory=list)
    review_items: list[StudioReviewItem] = field(default_factory=list)
    audit_logs: list[AuditLog] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_unique("exercise", [item.id for item in self.exercises])
        self._validate_unique("user", [item.id for item in self.users])
        self._validate_unique("inject", [item.id for item in self.injects])
        self._validate_unique("timeline event", [item.id for item in self.timeline_events])
        self._validate_unique("review item", [item.id for item in self.review_items])
        self._validate_unique("audit log", [item.id for item in self.audit_logs])
        self._sort_all()

    def register_exercise(self, exercise: Exercise) -> None:
        self._reject_duplicate("exercise", exercise.id, self.get_exercise(exercise.id))
        self.exercises.append(exercise)
        self.exercises.sort(key=lambda item: item.id)

    def register_user(self, user: User) -> None:
        self._reject_duplicate("user", user.id, self.get_user(user.id))
        self.users.append(user)
        self.users.sort(key=lambda item: item.id)

    def register_inject(self, inject: Inject) -> None:
        self._required_exercise(inject.exercise_id)
        if inject.created_by:
            self._required_user(inject.created_by)
        if inject.assigned_controller:
            self._required_user(inject.assigned_controller)
        if inject.approved_by:
            self._required_user(inject.approved_by)
        self._reject_duplicate("inject", inject.id, self.get_inject(inject.id))
        self.injects.append(inject)
        self.injects.sort(key=lambda item: item.id)

    def register_timeline_event(self, event: TimelineEvent) -> None:
        self._required_exercise(event.exercise_id)
        if event.related_inject_id:
            self._required_inject(event.related_inject_id)
        self._reject_duplicate("timeline event", event.id, self.get_timeline_event(event.id))
        self.timeline_events.append(event)
        self.timeline_events.sort(key=lambda item: item.timestamp)

    def register_review_item(self, item: StudioReviewItem) -> None:
        self._required_exercise(item.exercise_id)
        if item.reviewer_id:
            self._required_user(item.reviewer_id)
        self._reject_duplicate("review item", item.id, self.get_review_item(item.id))
        self.review_items.append(item)
        self.review_items.sort(key=lambda entry: entry.created_at)

    def register_audit_log(self, log: AuditLog) -> None:
        self._required_exercise(log.exercise_id)
        self._required_user(log.actor_id)
        self._reject_duplicate("audit log", log.id, self.get_audit_log(log.id))
        self.audit_logs.append(log)
        self.audit_logs.sort(key=lambda entry: entry.timestamp)

    def get_exercise(self, exercise_id: str) -> Exercise | None:
        return _find_by_id(self.exercises, exercise_id)

    def get_user(self, user_id: str) -> User | None:
        return _find_by_id(self.users, user_id)

    def get_inject(self, inject_id: str) -> Inject | None:
        return _find_by_id(self.injects, inject_id)

    def get_timeline_event(self, event_id: str) -> TimelineEvent | None:
        return _find_by_id(self.timeline_events, event_id)

    def get_review_item(self, item_id: str) -> StudioReviewItem | None:
        return _find_by_id(self.review_items, item_id)

    def get_audit_log(self, log_id: str) -> AuditLog | None:
        return _find_by_id(self.audit_logs, log_id)

    def list_exercises(self) -> list[Exercise]:
        return list(self.exercises)

    def list_users(self) -> list[User]:
        return list(self.users)

    def list_injects(self, exercise_id: str | None = None) -> list[Inject]:
        return [
            inject
            for inject in self.injects
            if exercise_id is None or inject.exercise_id == exercise_id
        ]

    def list_timeline_events(self, exercise_id: str | None = None) -> list[TimelineEvent]:
        return [
            event
            for event in self.timeline_events
            if exercise_id is None or event.exercise_id == exercise_id
        ]

    def list_review_items(self, exercise_id: str | None = None) -> list[StudioReviewItem]:
        return [
            item
            for item in self.review_items
            if exercise_id is None or item.exercise_id == exercise_id
        ]

    def list_audit_logs(self, exercise_id: str | None = None) -> list[AuditLog]:
        return [
            log
            for log in self.audit_logs
            if exercise_id is None or log.exercise_id == exercise_id
        ]

    def approve_review_item(
        self,
        item_id: str,
        reviewer_id: str,
        *,
        comments: str = "",
    ) -> StudioReviewItem:
        item = self._required_review_item(item_id)
        self._required_user(reviewer_id)
        item.record_decision(ReviewDecision.APPROVED, reviewer_id, comments=comments)
        if item.item_type.value == "inject":
            self._required_inject(item.item_id).approve(reviewer_id)
        return item

    def reject_review_item(
        self,
        item_id: str,
        reviewer_id: str,
        *,
        comments: str = "",
    ) -> StudioReviewItem:
        item = self._required_review_item(item_id)
        self._required_user(reviewer_id)
        item.record_decision(ReviewDecision.REJECTED, reviewer_id, comments=comments)
        if item.item_type.value == "inject":
            self._required_inject(item.item_id).reject()
        return item

    def _sort_all(self) -> None:
        self.exercises.sort(key=lambda item: item.id)
        self.users.sort(key=lambda item: item.id)
        self.injects.sort(key=lambda item: item.id)
        self.timeline_events.sort(key=lambda item: item.timestamp)
        self.review_items.sort(key=lambda item: item.created_at)
        self.audit_logs.sort(key=lambda item: item.timestamp)

    def _required_exercise(self, exercise_id: str) -> Exercise:
        exercise = self.get_exercise(exercise_id)
        if exercise is None:
            raise ValueError(f"exercise not found: {exercise_id}")
        return exercise

    def _required_user(self, user_id: str) -> User:
        user = self.get_user(user_id)
        if user is None:
            raise ValueError(f"user not found: {user_id}")
        return user

    def _required_inject(self, inject_id: str) -> Inject:
        inject = self.get_inject(inject_id)
        if inject is None:
            raise ValueError(f"inject not found: {inject_id}")
        return inject

    def _required_review_item(self, item_id: str) -> StudioReviewItem:
        item = self.get_review_item(item_id)
        if item is None:
            raise ValueError(f"review item not found: {item_id}")
        return item

    @staticmethod
    def _validate_unique(label: str, identifiers: list[str]) -> None:
        if len(identifiers) != len(set(identifiers)):
            raise ValueError(f"{label} identifiers must be unique")

    @staticmethod
    def _reject_duplicate(label: str, identifier: str, existing: object | None) -> None:
        if existing is not None:
            raise ValueError(f"{label} already exists: {identifier}")


def _find_by_id(items: list[T], identifier: str) -> T | None:
    for item in items:
        if item.id == identifier:
            return item
    return None
