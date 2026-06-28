from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class DecisionOutcome(str, Enum):
    """Aggregate or individual outcome from deterministic decision evaluation."""

    APPROVE = "approve"
    REVIEW = "review"
    BLOCK = "block"


@dataclass(slots=True)
class DecisionContext:
    """Inputs available to deterministic decision rules."""

    exercise_state: Any | None = None
    scenario: Any | None = None
    events: list[Any] = field(default_factory=list)
    entities: Any | None = None
    training_objectives: list[str] = field(default_factory=list)
    escalation_rules: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_str_list("training_objectives", self.training_objectives)
        _validate_str_list("escalation_rules", self.escalation_rules)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(slots=True)
class RuleEvaluation:
    """Result from one deterministic rule execution."""

    rule_identifier: str
    rule_name: str
    outcome: DecisionOutcome
    passed: bool
    message: str
    priority: int
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("rule_identifier", self.rule_identifier)
        _validate_non_empty("rule_name", self.rule_name)
        _validate_non_empty("message", self.message)
        if self.priority < 0:
            raise ValueError("priority must be greater than or equal to zero")
        if not isinstance(self.details, dict):
            raise ValueError("details must be a dictionary")


@dataclass(slots=True)
class DecisionRule:
    """A modular deterministic rule."""

    identifier: str
    name: str
    description: str
    priority: int
    evaluator: Callable[[DecisionContext, "DecisionRule"], RuleEvaluation] = field(
        repr=False
    )

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("description", self.description)
        if self.priority < 0:
            raise ValueError("priority must be greater than or equal to zero")

    def execute(self, context: DecisionContext) -> RuleEvaluation:
        evaluation = self.evaluator(context, self)
        if evaluation.rule_identifier != self.identifier:
            raise ValueError("rule evaluation identifier must match rule identifier")
        return evaluation


@dataclass(slots=True)
class DecisionResult:
    """Aggregate result from executing decision rules."""

    decision_identifier: str
    outcome: DecisionOutcome
    evaluations: list[RuleEvaluation]
    decision_log: list[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("decision_identifier", self.decision_identifier)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    @property
    def passed(self) -> bool:
        return self.outcome is DecisionOutcome.APPROVE


@dataclass(slots=True)
class Decision:
    """Deterministic rule runner with registration and in-memory logging."""

    identifier: str
    rules: list[DecisionRule] = field(default_factory=list)
    decision_log: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        self._validate_unique_rules()

    def register_rule(self, rule: DecisionRule) -> None:
        if any(existing.identifier == rule.identifier for existing in self.rules):
            raise ValueError(f"rule identifier already exists: {rule.identifier}")
        self.rules.append(rule)
        self._log(f"registered rule {rule.identifier}")

    def execute(self, context: DecisionContext) -> DecisionResult:
        ordered_rules = sorted(self.rules, key=lambda rule: rule.priority)
        evaluations: list[RuleEvaluation] = []
        self._log(f"executing {len(ordered_rules)} rules")

        for rule in ordered_rules:
            evaluation = rule.execute(context)
            evaluations.append(evaluation)
            self._log(
                f"rule {rule.identifier} returned {evaluation.outcome.value}: "
                f"{evaluation.message}"
            )

        outcome = _aggregate_outcome(evaluations)
        self._log(f"decision outcome {outcome.value}")
        return DecisionResult(
            decision_identifier=self.identifier,
            outcome=outcome,
            evaluations=evaluations,
            decision_log=list(self.decision_log),
        )

    def _validate_unique_rules(self) -> None:
        identifiers = [rule.identifier for rule in self.rules]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("rule identifiers must be unique")

    def _log(self, message: str) -> None:
        self.decision_log.append(message)


def _aggregate_outcome(evaluations: list[RuleEvaluation]) -> DecisionOutcome:
    if any(evaluation.outcome is DecisionOutcome.BLOCK for evaluation in evaluations):
        return DecisionOutcome.BLOCK
    if any(evaluation.outcome is DecisionOutcome.REVIEW for evaluation in evaluations):
        return DecisionOutcome.REVIEW
    return DecisionOutcome.APPROVE


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")
