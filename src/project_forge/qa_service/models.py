from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class QASeverity(str, Enum):
    """Severity of an individual QA finding."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class QAStatus(str, Enum):
    """Status for QA checks, results, and reports."""

    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class QAFinding:
    """A single QA finding."""

    check_identifier: str
    severity: QASeverity
    message: str
    field: str = ""
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("check_identifier", self.check_identifier)
        _validate_non_empty("message", self.message)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(frozen=True, slots=True)
class QAResult:
    """Result for a single QA check."""

    check_identifier: str
    status: QAStatus
    findings: list[QAFinding] = dataclass_field(default_factory=list)
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("check_identifier", self.check_identifier)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


QACheckEvaluator = Callable[[dict[str, Any]], QAResult]


@dataclass(slots=True)
class QACheck:
    """A registerable deterministic QA check."""

    identifier: str
    name: str
    description: str
    evaluator: QACheckEvaluator = dataclass_field(repr=False)
    categories: list[str] = dataclass_field(default_factory=list)
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("description", self.description)
        _validate_str_list("categories", self.categories)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def execute(self, product: dict[str, Any]) -> QAResult:
        result = self.evaluator(product)
        if result.check_identifier != self.identifier:
            raise ValueError("QA result identifier must match check identifier")
        return result


@dataclass(frozen=True, slots=True)
class QAReport:
    """Aggregate QA report for a proposed or generated product."""

    product_identifier: str
    status: QAStatus
    results: list[QAResult]
    created_at: datetime = dataclass_field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("product_identifier", self.product_identifier)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    @property
    def findings(self) -> list[QAFinding]:
        return [finding for result in self.results for finding in result.findings]


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")
