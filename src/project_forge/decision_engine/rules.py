from __future__ import annotations

from typing import Any

from .models import DecisionContext, DecisionOutcome, DecisionRule, RuleEvaluation


def create_default_rules() -> list[DecisionRule]:
    """Create the foundational deterministic rule set."""

    return [
        escalation_check_rule(),
        training_objective_relevance_rule(),
        duplicate_event_detection_rule(),
        scenario_consistency_rule(),
    ]


def escalation_check_rule(priority: int = 10) -> DecisionRule:
    return DecisionRule(
        identifier="escalation-check",
        name="Escalation Check",
        description="Checks state and scenario escalation levels against rules.",
        priority=priority,
        evaluator=_evaluate_escalation_check,
    )


def training_objective_relevance_rule(priority: int = 20) -> DecisionRule:
    return DecisionRule(
        identifier="training-objective-relevance",
        name="Training Objective Relevance",
        description="Checks whether active training objectives are present.",
        priority=priority,
        evaluator=_evaluate_training_objective_relevance,
    )


def duplicate_event_detection_rule(priority: int = 30) -> DecisionRule:
    return DecisionRule(
        identifier="duplicate-event-detection",
        name="Duplicate Event Detection",
        description="Detects duplicate event identifiers in decision context.",
        priority=priority,
        evaluator=_evaluate_duplicate_event_detection,
    )


def scenario_consistency_rule(priority: int = 40) -> DecisionRule:
    return DecisionRule(
        identifier="scenario-consistency",
        name="Scenario Consistency",
        description="Checks exercise state and scenario day, phase, and references.",
        priority=priority,
        evaluator=_evaluate_scenario_consistency,
    )


def _evaluate_escalation_check(
    context: DecisionContext,
    rule: DecisionRule,
) -> RuleEvaluation:
    state_level = _enum_value(_get_nested(context.exercise_state, "escalation_level"))
    scenario_level = _enum_value(_get_nested(context.scenario, "escalation_level"))
    escalation_rules = context.escalation_rules

    if not state_level and not scenario_level:
        return _evaluation(
            rule,
            DecisionOutcome.REVIEW,
            False,
            "No escalation level is available for evaluation.",
        )

    if state_level and scenario_level and state_level != scenario_level:
        return _evaluation(
            rule,
            DecisionOutcome.REVIEW,
            False,
            "Exercise state and scenario escalation levels differ.",
            {"exercise_state": state_level, "scenario": scenario_level},
        )

    level = scenario_level or state_level
    if level in {"high", "crisis"} and not escalation_rules:
        return _evaluation(
            rule,
            DecisionOutcome.REVIEW,
            False,
            "High escalation requires explicit escalation rules.",
            {"escalation_level": level},
        )

    return _evaluation(
        rule,
        DecisionOutcome.APPROVE,
        True,
        "Escalation level is consistent with available rules.",
        {"escalation_level": level, "rule_count": len(escalation_rules)},
    )


def _evaluate_training_objective_relevance(
    context: DecisionContext,
    rule: DecisionRule,
) -> RuleEvaluation:
    objectives = list(context.training_objectives)
    scenario_objectives = _get_nested(context.scenario, "active_objectives") or []
    state_objectives = _get_nested(context.exercise_state, "active_training_objectives") or []
    objectives.extend(_objective_titles(scenario_objectives))
    objectives.extend(str(objective) for objective in state_objectives)

    unique_objectives = {objective for objective in objectives if objective.strip()}
    if not unique_objectives:
        return _evaluation(
            rule,
            DecisionOutcome.REVIEW,
            False,
            "No active training objectives are available.",
        )

    return _evaluation(
        rule,
        DecisionOutcome.APPROVE,
        True,
        "Active training objectives are available.",
        {"objective_count": len(unique_objectives)},
    )


def _evaluate_duplicate_event_detection(
    context: DecisionContext,
    rule: DecisionRule,
) -> RuleEvaluation:
    identifiers = [_get_nested(event, "identifier") for event in context.events]
    normalized = [str(identifier) for identifier in identifiers if identifier]
    duplicates = sorted(
        identifier for identifier in set(normalized) if normalized.count(identifier) > 1
    )

    if duplicates:
        return _evaluation(
            rule,
            DecisionOutcome.BLOCK,
            False,
            "Duplicate event identifiers were detected.",
            {"duplicate_event_identifiers": duplicates},
        )

    return _evaluation(
        rule,
        DecisionOutcome.APPROVE,
        True,
        "No duplicate event identifiers were detected.",
        {"event_count": len(normalized)},
    )


def _evaluate_scenario_consistency(
    context: DecisionContext,
    rule: DecisionRule,
) -> RuleEvaluation:
    if context.exercise_state is None or context.scenario is None:
        return _evaluation(
            rule,
            DecisionOutcome.REVIEW,
            False,
            "Exercise state and scenario are both required for consistency checks.",
        )

    state_day = _get_nested(context.exercise_state, "current_day", "day_number")
    scenario_day = _get_nested(context.scenario, "current_exercise_day")
    state_phase = _enum_value(_get_nested(context.exercise_state, "current_phase"))
    scenario_phase = _enum_value(_get_nested(context.scenario, "current_phase"))
    issues: list[str] = []

    if state_day != scenario_day:
        issues.append("exercise day differs")
    if state_phase != scenario_phase:
        issues.append("exercise phase differs")

    missing_entities = _missing_related_entities(context)
    if missing_entities:
        issues.append("scenario references missing entities")

    if issues:
        return _evaluation(
            rule,
            DecisionOutcome.REVIEW,
            False,
            "Scenario consistency issues require review.",
            {"issues": issues, "missing_entities": missing_entities},
        )

    return _evaluation(
        rule,
        DecisionOutcome.APPROVE,
        True,
        "Exercise state and scenario are consistent.",
        {"exercise_day": scenario_day, "exercise_phase": scenario_phase},
    )


def _missing_related_entities(context: DecisionContext) -> list[str]:
    related_entities = _get_nested(context.scenario, "related_entities") or []
    entity_catalog = context.entities
    if not related_entities or entity_catalog is None:
        return []
    get_entity = getattr(entity_catalog, "get_entity", None)
    if not callable(get_entity):
        return []
    return [
        identifier
        for identifier in related_entities
        if isinstance(identifier, str) and get_entity(identifier) is None
    ]


def _objective_titles(objectives: list[Any]) -> list[str]:
    titles: list[str] = []
    for objective in objectives:
        title = _get_nested(objective, "title")
        if isinstance(title, str):
            titles.append(title)
    return titles


def _evaluation(
    rule: DecisionRule,
    outcome: DecisionOutcome,
    passed: bool,
    message: str,
    details: dict[str, Any] | None = None,
) -> RuleEvaluation:
    return RuleEvaluation(
        rule_identifier=rule.identifier,
        rule_name=rule.name,
        outcome=outcome,
        passed=passed,
        message=message,
        priority=rule.priority,
        details=details or {},
    )


def _enum_value(value: Any) -> str | None:
    if value is None:
        return None
    enum_value = getattr(value, "value", value)
    return str(enum_value)


def _get_nested(value: Any, *attributes: str) -> Any:
    current = value
    for attribute in attributes:
        if current is None:
            return None
        current = getattr(current, attribute, None)
    return current
