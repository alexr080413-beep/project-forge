from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ScenarioPhase(str, Enum):
    """High-level phase of scenario play."""

    SETUP = "setup"
    STARTEX = "startex"
    EXECUTION = "execution"
    TRANSITION = "transition"
    ENDEX = "endex"
    AFTER_ACTION = "after_action"


class ScenarioStatus(str, Enum):
    """Lifecycle status for a scenario."""

    DRAFT = "draft"
    CURRENT = "current"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ScenarioEscalationLevel(str, Enum):
    """Scenario escalation level."""

    LOW = "low"
    ELEVATED = "elevated"
    HIGH = "high"
    CRISIS = "crisis"


class ScenarioTempo(str, Enum):
    """Scenario operating tempo."""

    PAUSED = "paused"
    SLOW = "slow"
    STEADY = "steady"
    FAST = "fast"
    SURGE = "surge"


@dataclass(slots=True)
class ScenarioObjective:
    """An objective active in a scenario."""

    identifier: str
    title: str
    description: str = ""
    status: str = "active"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("title", self.title)
        _validate_non_empty("status", self.status)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class ScenarioConstraint:
    """A scenario rule, boundary, or limitation."""

    identifier: str
    description: str
    severity: str = "standard"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("description", self.description)
        _validate_non_empty("severity", self.severity)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class ScenarioAssumption:
    """An assumption that frames scenario interpretation."""

    identifier: str
    description: str
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("description", self.description)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class ScenarioControlMeasure:
    """A control measure for scenario management and EXCON boundaries."""

    identifier: str
    title: str
    description: str
    owner: str = "EXCON"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("title", self.title)
        _validate_non_empty("description", self.description)
        _validate_non_empty("owner", self.owner)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class Scenario:
    """A complete scenario state used to guide Project Forge workflows."""

    identifier: str
    scenario_name: str
    description: str
    current_exercise_day: int
    current_phase: ScenarioPhase
    active_objectives: list[ScenarioObjective] = field(default_factory=list)
    active_constraints: list[ScenarioConstraint] = field(default_factory=list)
    active_assumptions: list[ScenarioAssumption] = field(default_factory=list)
    active_control_measures: list[ScenarioControlMeasure] = field(default_factory=list)
    escalation_level: ScenarioEscalationLevel = ScenarioEscalationLevel.LOW
    tempo: ScenarioTempo = ScenarioTempo.STEADY
    related_entities: list[str] = field(default_factory=list)
    related_events: list[str] = field(default_factory=list)
    related_knowledge_documents: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: ScenarioStatus = ScenarioStatus.DRAFT

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("scenario_name", self.scenario_name)
        _validate_non_empty("description", self.description)
        if self.current_exercise_day < 1:
            raise ValueError("current_exercise_day must be greater than zero")
        _validate_str_list("related_entities", self.related_entities)
        _validate_str_list("related_events", self.related_events)
        _validate_str_list(
            "related_knowledge_documents",
            self.related_knowledge_documents,
        )
        _validate_metadata(self.metadata)


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
