from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AuditAction(str, Enum):
    """Significant platform actions that should be traceable."""

    SERVICE_EXECUTION = "service_execution"
    WORKFLOW_EXECUTION = "workflow_execution"
    REVIEW_ACTION = "review_action"
    APPROVAL = "approval"
    REJECTION = "rejection"
    CONFIGURATION_CHANGE = "configuration_change"
    PROFILE_SELECTION = "profile_selection"
    AI_REQUEST = "ai_request"
    PRODUCT_GENERATION = "product_generation"
    DISTRIBUTION = "distribution"
    AUTOMATION_EXECUTION = "automation_execution"


class AuditCategory(str, Enum):
    """High-level audit categories for filtering and after-action review."""

    SERVICE = "service"
    WORKFLOW = "workflow"
    REVIEW = "review"
    APPROVAL = "approval"
    CONFIGURATION = "configuration"
    PROFILE = "profile"
    AI = "ai"
    PRODUCT = "product"
    DISTRIBUTION = "distribution"
    AUTOMATION = "automation"


class AuditSeverity(str, Enum):
    """Severity levels for audit entries."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class AuditActor:
    """A human, service, or automated component that performed an action."""

    actor_id: str
    display_name: str
    actor_type: str = "service"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("actor_id", self.actor_id)
        _validate_non_empty("display_name", self.display_name)
        _validate_non_empty("actor_type", self.actor_type)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """One significant action emitted by the platform."""

    event_id: str
    action: AuditAction
    category: AuditCategory
    actor: AuditActor
    summary: str
    service: str = ""
    correlation_id: str = ""
    parent_event_id: str = ""
    severity: AuditSeverity = AuditSeverity.INFO
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        _validate_non_empty("event_id", self.event_id)
        _validate_non_empty("summary", self.summary)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """A stored audit event with session and child event context."""

    entry_id: str
    event: AuditEvent
    session_id: str = ""
    child_event_ids: list[str] = field(default_factory=list)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("entry_id", self.entry_id)
        _validate_str_list("child_event_ids", self.child_event_ids)
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class AuditSession:
    """A local grouping of related audit entries."""

    session_id: str
    actor: AuditActor
    correlation_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("session_id", self.session_id)
        _validate_non_empty("correlation_id", self.correlation_id)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)
        if self.ended_at and self.ended_at < self.started_at:
            raise ValueError("ended_at must not be before started_at")

    def close(self, ended_at: datetime | None = None) -> None:
        close_time = ended_at or datetime.now(timezone.utc)
        if close_time < self.started_at:
            raise ValueError("ended_at must not be before started_at")
        self.ended_at = close_time


@dataclass(frozen=True, slots=True)
class AuditFilter:
    """Filters used to query the local audit registry."""

    categories: list[AuditCategory] = field(default_factory=list)
    actions: list[AuditAction] = field(default_factory=list)
    severities: list[AuditSeverity] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    actor_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    correlation_id: str = ""
    parent_event_id: str = ""
    date_from: datetime | None = None
    date_to: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_str_list("services", self.services)
        _validate_str_list("actor_ids", self.actor_ids)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be before or equal to date_to")


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError(f"{name} must be a list of non-empty strings")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
