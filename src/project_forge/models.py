from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ReviewStatus(str, Enum):
    """Lifecycle states for generated reports."""

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(slots=True)
class SourceItem:
    """An ingested or referenced source used as input for report drafting."""

    id: str
    title: str
    source_type: str
    content: str
    published_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("title", self.title)
        self._validate_non_empty("source_type", self.source_type)
        self._validate_non_empty("content", self.content)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


@dataclass(slots=True)
class TrainingObjective:
    """A learning or exercise objective used to frame the scenario context."""

    id: str
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("name", self.name)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


@dataclass(slots=True)
class ScenarioActor:
    """A participant or role defined by the exercise scenario."""

    id: str
    name: str
    role: str
    affiliation: str | None = None

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("name", self.name)
        self._validate_non_empty("role", self.role)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


@dataclass(slots=True)
class ScenarioLocation:
    """A place or site defined by the exercise scenario."""

    id: str
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("name", self.name)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


@dataclass(slots=True)
class ScenarioMapping:
    """Links a source item to scenario actors and locations."""

    id: str
    source_item_id: str
    actor_ids: list[str] = field(default_factory=list)
    location_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("source_item_id", self.source_item_id)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


@dataclass(slots=True)
class ExerciseContext:
    """The scenario context that frames the output generation workflow."""

    id: str
    name: str
    description: str
    objectives: list[TrainingObjective] = field(default_factory=list)
    actors: list[ScenarioActor] = field(default_factory=list)
    locations: list[ScenarioLocation] = field(default_factory=list)
    mappings: list[ScenarioMapping] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("name", self.name)
        self._validate_non_empty("description", self.description)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


@dataclass(slots=True)
class ReportRequest:
    """A request for generating a report from a source and scenario context."""

    id: str
    request_type: str
    source_item_id: str
    exercise_context_id: str
    requested_by: str
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("request_type", self.request_type)
        self._validate_non_empty("source_item_id", self.source_item_id)
        self._validate_non_empty("exercise_context_id", self.exercise_context_id)
        self._validate_non_empty("requested_by", self.requested_by)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


@dataclass(slots=True)
class QualityCheckResult:
    """A single quality validation for a generated report."""

    id: str
    check_name: str
    passed: bool
    details: str = ""

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("check_name", self.check_name)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


@dataclass(slots=True)
class GeneratedReport:
    """A generated, notional exercise report ready for review."""

    id: str
    report_type: str
    request_id: str
    content: str
    status: ReviewStatus = ReviewStatus.DRAFT
    quality_checks: list[QualityCheckResult] = field(default_factory=list)
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        self._validate_non_empty("id", self.id)
        self._validate_non_empty("report_type", self.report_type)
        self._validate_non_empty("request_id", self.request_id)
        self._validate_non_empty("content", self.content)

    @staticmethod
    def _validate_non_empty(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} must not be empty")


__all__ = [
    "ExerciseContext",
    "GeneratedReport",
    "QualityCheckResult",
    "ReportRequest",
    "ReviewStatus",
    "ScenarioActor",
    "ScenarioLocation",
    "ScenarioMapping",
    "SourceItem",
    "TrainingObjective",
]
