from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ExerciseStatus(str, Enum):
    """High-level lifecycle status for a Forge Studio exercise."""

    DRAFT = "draft"
    PLANNING = "planning"
    PREPARING = "preparing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ExercisePhase(str, Enum):
    """Exercise lifecycle phase used by Forge Studio."""

    PLANNING = "planning"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    ASSESSMENT = "assessment"


class UserRole(str, Enum):
    """Forge Studio MVP user roles."""

    EXERCISE_DIRECTOR = "exercise_director"
    INTELLIGENCE_CHIEF = "intelligence_chief"
    EXERCISE_CONTROL_OFFICER = "exercise_control_officer"
    CONTROLLER = "controller"
    OBSERVER = "observer"
    REVIEWER = "reviewer"
    ADMINISTRATOR = "administrator"


class UserStatus(str, Enum):
    """User availability for Forge Studio MVP workflows."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class InjectType(str, Enum):
    """Supported inject categories for the MVP foundation."""

    INTELLIGENCE = "intelligence"
    OPERATIONS = "operations"
    MEDIA = "media"
    LOGISTICS = "logistics"
    EXERCISE_CONTROL = "exercise_control"
    OTHER = "other"


class InjectPriority(str, Enum):
    """Inject priority used by controller queues."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InjectStatus(str, Enum):
    """Human-controlled inject lifecycle."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TimelineEventType(str, Enum):
    """Timeline event categories for the MVP foundation."""

    EXERCISE_PHASE = "exercise_phase"
    INJECT = "inject"
    REVIEW = "review"
    AUDIT = "audit"
    NOTE = "note"


class StudioReviewStatus(str, Enum):
    """Human review queue lifecycle states."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class ReviewDecision(str, Enum):
    """Explicit human review decisions."""

    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class ReviewItemType(str, Enum):
    """Reviewable Forge Studio item families."""

    INJECT = "inject"
    TIMELINE_EVENT = "timeline_event"
    PRODUCT = "product"
    NOTE = "note"


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Exercise:
    """Top-level Forge Studio exercise container."""

    id: str
    name: str
    description: str = ""
    status: ExerciseStatus = ExerciseStatus.DRAFT
    phase: ExercisePhase = ExercisePhase.PLANNING
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def __post_init__(self) -> None:
        _validate_identifier("id", self.id)
        _validate_non_empty("name", self.name)
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be before created_at")

    def transition_status(self, status: ExerciseStatus) -> None:
        self.status = status
        self.updated_at = _now()

    def transition_phase(self, phase: ExercisePhase) -> None:
        self.phase = phase
        self.updated_at = _now()


@dataclass(frozen=True, slots=True)
class User:
    """Forge Studio MVP user record."""

    id: str
    display_name: str
    email: str
    role: UserRole
    organization: str = ""
    status: UserStatus = UserStatus.ACTIVE

    def __post_init__(self) -> None:
        _validate_identifier("id", self.id)
        _validate_non_empty("display_name", self.display_name)
        _validate_email(self.email)

    @property
    def active(self) -> bool:
        return self.status is UserStatus.ACTIVE


@dataclass(slots=True)
class Inject:
    """Controller-managed inject that requires human approval before release."""

    id: str
    exercise_id: str
    title: str
    description: str = ""
    inject_type: InjectType = InjectType.OTHER
    priority: InjectPriority = InjectPriority.MEDIUM
    status: InjectStatus = InjectStatus.DRAFT
    assigned_controller: str = ""
    scheduled_time: datetime | None = None
    created_by: str = ""
    approved_by: str = ""
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def __post_init__(self) -> None:
        _validate_identifier("id", self.id)
        _validate_identifier("exercise_id", self.exercise_id)
        _validate_non_empty("title", self.title)
        _validate_optional_identifier("assigned_controller", self.assigned_controller)
        _validate_optional_identifier("created_by", self.created_by)
        _validate_optional_identifier("approved_by", self.approved_by)
        if self.status in {InjectStatus.APPROVED, InjectStatus.SCHEDULED}:
            _validate_non_empty("approved_by", self.approved_by)
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be before created_at")

    @property
    def releasable(self) -> bool:
        return self.status in {InjectStatus.APPROVED, InjectStatus.SCHEDULED} and bool(
            self.approved_by.strip()
        )

    def submit_for_review(self) -> None:
        if self.status not in {InjectStatus.DRAFT, InjectStatus.REJECTED}:
            raise ValueError("only draft or rejected injects can be submitted for review")
        self.status = InjectStatus.PENDING_REVIEW
        self.updated_at = _now()

    def approve(self, reviewer_id: str) -> None:
        _validate_identifier("reviewer_id", reviewer_id)
        self.approved_by = reviewer_id
        self.status = InjectStatus.APPROVED
        self.updated_at = _now()

    def reject(self) -> None:
        self.approved_by = ""
        self.status = InjectStatus.REJECTED
        self.updated_at = _now()

    def schedule(self, scheduled_time: datetime) -> None:
        if not self.releasable:
            raise ValueError("inject requires explicit human approval before scheduling")
        self.scheduled_time = scheduled_time
        self.status = InjectStatus.SCHEDULED
        self.updated_at = _now()


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    """One event on the exercise operational timeline."""

    id: str
    exercise_id: str
    event_type: TimelineEventType
    title: str
    description: str = ""
    timestamp: datetime = field(default_factory=_now)
    source: str = ""
    related_inject_id: str = ""

    def __post_init__(self) -> None:
        _validate_identifier("id", self.id)
        _validate_identifier("exercise_id", self.exercise_id)
        _validate_non_empty("title", self.title)
        _validate_optional_identifier("related_inject_id", self.related_inject_id)


@dataclass(slots=True)
class StudioReviewItem:
    """Human review queue item for Forge Studio MVP objects."""

    id: str
    exercise_id: str
    item_type: ReviewItemType
    item_id: str
    status: StudioReviewStatus = StudioReviewStatus.PENDING
    reviewer_id: str = ""
    decision: ReviewDecision | None = None
    comments: str = ""
    created_at: datetime = field(default_factory=_now)
    reviewed_at: datetime | None = None

    def __post_init__(self) -> None:
        _validate_identifier("id", self.id)
        _validate_identifier("exercise_id", self.exercise_id)
        _validate_identifier("item_id", self.item_id)
        _validate_optional_identifier("reviewer_id", self.reviewer_id)
        if self.decision and self.status not in {
            StudioReviewStatus.APPROVED,
            StudioReviewStatus.REJECTED,
            StudioReviewStatus.REVISION_REQUESTED,
        }:
            raise ValueError("review decision requires a completed review status")
        if self.decision and self.reviewed_at is None:
            raise ValueError("reviewed_at is required when decision is set")

    def assign(self, reviewer_id: str) -> None:
        _validate_identifier("reviewer_id", reviewer_id)
        if self.status not in {StudioReviewStatus.PENDING, StudioReviewStatus.IN_REVIEW}:
            raise ValueError("only pending or in-review items can be assigned")
        self.reviewer_id = reviewer_id
        self.status = StudioReviewStatus.IN_REVIEW

    def record_decision(
        self,
        decision: ReviewDecision,
        reviewer_id: str,
        *,
        comments: str = "",
        reviewed_at: datetime | None = None,
    ) -> None:
        _validate_identifier("reviewer_id", reviewer_id)
        self.reviewer_id = reviewer_id
        self.decision = decision
        self.comments = comments
        self.reviewed_at = reviewed_at or _now()
        self.status = _review_status_for_decision(decision)


@dataclass(frozen=True, slots=True)
class AuditLog:
    """Audit record for a Forge Studio MVP action."""

    id: str
    exercise_id: str
    actor_id: str
    action: str
    target_type: str
    target_id: str
    timestamp: datetime = field(default_factory=_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_identifier("id", self.id)
        _validate_identifier("exercise_id", self.exercise_id)
        _validate_identifier("actor_id", self.actor_id)
        _validate_non_empty("action", self.action)
        _validate_non_empty("target_type", self.target_type)
        _validate_identifier("target_id", self.target_id)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


def _review_status_for_decision(decision: ReviewDecision) -> StudioReviewStatus:
    if decision is ReviewDecision.APPROVED:
        return StudioReviewStatus.APPROVED
    if decision is ReviewDecision.REJECTED:
        return StudioReviewStatus.REJECTED
    return StudioReviewStatus.REVISION_REQUESTED


def _validate_identifier(name: str, value: str | None) -> None:
    _validate_non_empty(name, value)
    assert value is not None
    if any(character.isspace() for character in value):
        raise ValueError(f"{name} must not contain whitespace")


def _validate_optional_identifier(name: str, value: str) -> None:
    if value and any(character.isspace() for character in value):
        raise ValueError(f"{name} must not contain whitespace")


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_email(value: str) -> None:
    _validate_non_empty("email", value)
    if "@" not in value or value.startswith("@") or value.endswith("@"):
        raise ValueError("email must be a valid email-like value")
