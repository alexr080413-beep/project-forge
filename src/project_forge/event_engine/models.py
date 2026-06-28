from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Supported notional event categories."""

    POLITICAL = "political"
    MILITARY = "military"
    INFORMATION = "information"
    LOGISTICS = "logistics"
    CYBER = "cyber"
    CIVIL = "civil"
    EXERCISE_CONTROL = "exercise_control"


class EventSeverity(str, Enum):
    """Event severity used for triage and scenario management."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventSource(str, Enum):
    """Originating source for an event."""

    EXCON = "excon"
    WHITE_CELL = "white_cell"
    ROLE_PLAYER = "role_player"
    SIMULATED_MEDIA = "simulated_media"
    OPEN_SOURCE = "open_source"
    SYSTEM = "system"


class EventStatus(str, Enum):
    """Lifecycle status for an exercise event."""

    DRAFT = "draft"
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


@dataclass(slots=True)
class EventImpact:
    """A typed impact produced by an exercise event."""

    area: str
    severity: EventSeverity
    summary: str
    affected_entities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("area", self.area)
        _validate_non_empty("summary", self.summary)
        _validate_str_list("affected_entities", self.affected_entities)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(slots=True)
class ExerciseEvent:
    """A scenario event used by Project Forge workflows."""

    identifier: str
    title: str
    summary: str
    event_type: EventType
    originating_source: EventSource
    scenario_actors_involved: list[str]
    locations_involved: list[str]
    timestamp: datetime
    exercise_day: int
    exercise_phase: str
    confidence: float
    impacts: list[EventImpact] = field(default_factory=list)
    related_entities: list[str] = field(default_factory=list)
    supporting_source_references: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: EventStatus = EventStatus.DRAFT

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("title", self.title)
        _validate_non_empty("summary", self.summary)
        _validate_non_empty("exercise_phase", self.exercise_phase)
        _validate_str_list("scenario_actors_involved", self.scenario_actors_involved)
        _validate_str_list("locations_involved", self.locations_involved)
        _validate_str_list("related_entities", self.related_entities)
        _validate_str_list(
            "supporting_source_references",
            self.supporting_source_references,
        )
        _validate_str_list("tags", self.tags)
        if self.exercise_day < 1:
            raise ValueError("exercise_day must be greater than zero")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")
