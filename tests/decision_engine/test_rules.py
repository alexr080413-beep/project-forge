from datetime import datetime, timezone

import pytest

from project_forge.decision_engine import (
    Decision,
    DecisionContext,
    DecisionOutcome,
    DecisionRule,
    RuleEvaluation,
    create_default_rules,
)
from project_forge.entity_engine import EntityCatalog, Organization, Unit
from project_forge.entity_engine.models import Affiliation
from project_forge.event_engine import EventImpact, EventSeverity, EventSource, EventType
from project_forge.event_engine import ExerciseEvent
from project_forge.exercise_state import (
    EscalationLevel,
    ExerciseDay,
    ExercisePhase,
    ExerciseState,
    ExerciseTempo,
    InformationEnvironment,
    MilitarySituation,
    PoliticalSituation,
    ScenarioSituation,
)
from project_forge.scenario_engine import (
    Scenario,
    ScenarioAssumption,
    ScenarioConstraint,
    ScenarioControlMeasure,
    ScenarioEscalationLevel,
    ScenarioObjective,
    ScenarioPhase,
    ScenarioStatus,
    ScenarioTempo,
)


def make_exercise_state() -> ExerciseState:
    return ExerciseState(
        exercise_name="Forge Decision Exercise",
        current_day=ExerciseDay(day_number=2),
        current_phase=ExercisePhase.EXECUTION,
        current_operational_summary="Controllers are maintaining scenario play.",
        scenario_situation=ScenarioSituation(
            summary="Scenario is active.",
            political=PoliticalSituation(summary="Political situation is steady."),
            military=MilitarySituation(summary="Military situation is monitored."),
            information_environment=InformationEnvironment(
                summary="Information activity is manageable."
            ),
        ),
        active_training_objectives=["Maintain shared scenario awareness"],
        active_scenario_actors=["Joint Task Force Headquarters"],
        active_locations=["Capital Operations Center"],
        exercise_tempo=ExerciseTempo.STEADY,
        escalation_level=EscalationLevel.ELEVATED,
    )


def make_scenario() -> Scenario:
    return Scenario(
        identifier="scenario-decision",
        scenario_name="Decision Scenario",
        description="A scenario for deterministic decision tests.",
        current_exercise_day=2,
        current_phase=ScenarioPhase.EXECUTION,
        active_objectives=[
            ScenarioObjective(
                identifier="obj-awareness",
                title="Maintain shared scenario awareness",
            )
        ],
        active_constraints=[
            ScenarioConstraint(
                identifier="constraint-escalation",
                description="No escalation without approval.",
            )
        ],
        active_assumptions=[
            ScenarioAssumption(
                identifier="assumption-notional",
                description="Scenario play remains notional.",
            )
        ],
        active_control_measures=[
            ScenarioControlMeasure(
                identifier="cm-release",
                title="Release Authority",
                description="Senior Controller approves escalation-sensitive play.",
            )
        ],
        escalation_level=ScenarioEscalationLevel.ELEVATED,
        tempo=ScenarioTempo.STEADY,
        related_entities=["org-excon", "unit-jtf-hq"],
        related_events=["evt-001"],
        related_knowledge_documents=["knowledge_base/README.md"],
        status=ScenarioStatus.CURRENT,
    )


def make_event(identifier: str = "evt-001") -> ExerciseEvent:
    return ExerciseEvent(
        identifier=identifier,
        title="Decision Event",
        summary="A notional event for decision tests.",
        event_type=EventType.MILITARY,
        originating_source=EventSource.EXCON,
        scenario_actors_involved=["Joint Task Force Headquarters"],
        locations_involved=["Capital Operations Center"],
        timestamp=datetime(2026, 6, 27, 15, 30, tzinfo=timezone.utc),
        exercise_day=2,
        exercise_phase="execution",
        confidence=0.9,
        impacts=[
            EventImpact(
                area="force_posture",
                severity=EventSeverity.MEDIUM,
                summary="Monitor posture changes.",
            )
        ],
    )


def make_entities() -> EntityCatalog:
    return EntityCatalog(
        entities=[
            Organization(
                identifier="org-excon",
                display_name="Exercise Control",
                affiliation=Affiliation.EXERCISE_CONTROL,
            ),
            Unit(
                identifier="unit-jtf-hq",
                display_name="Joint Task Force Headquarters",
                affiliation=Affiliation.FRIENDLY,
            ),
        ]
    )


def make_context(events: list[ExerciseEvent] | None = None) -> DecisionContext:
    return DecisionContext(
        exercise_state=make_exercise_state(),
        scenario=make_scenario(),
        events=events if events is not None else [make_event()],
        entities=make_entities(),
        training_objectives=["Maintain shared scenario awareness"],
        escalation_rules=["Senior Controller approval required for escalation."],
    )


def test_default_rules_execute_successfully() -> None:
    decision = Decision(identifier="decision-test", rules=create_default_rules())

    result = decision.execute(make_context())

    assert result.outcome is DecisionOutcome.APPROVE
    assert result.passed is True
    assert [evaluation.rule_identifier for evaluation in result.evaluations] == [
        "escalation-check",
        "training-objective-relevance",
        "duplicate-event-detection",
        "scenario-consistency",
    ]
    assert result.decision_log[-1] == "decision outcome approve"


def test_rules_can_be_added_modularly() -> None:
    def evaluate(
        context: DecisionContext,
        rule: DecisionRule,
    ) -> RuleEvaluation:
        return RuleEvaluation(
            rule_identifier=rule.identifier,
            rule_name=rule.name,
            outcome=DecisionOutcome.APPROVE,
            passed=True,
            message=f"Evaluated {len(context.events)} events.",
            priority=rule.priority,
        )

    decision = Decision(identifier="decision-modular")
    decision.register_rule(
        DecisionRule(
            identifier="custom-rule",
            name="Custom Rule",
            description="A custom modular rule.",
            priority=5,
            evaluator=evaluate,
        )
    )

    result = decision.execute(make_context())

    assert result.outcome is DecisionOutcome.APPROVE
    assert result.evaluations[0].rule_identifier == "custom-rule"
    assert "registered rule custom-rule" in result.decision_log


def test_rule_priorities_control_execution_order() -> None:
    rules = create_default_rules()
    rules[0].priority = 40
    rules[3].priority = 5
    decision = Decision(identifier="decision-priority", rules=rules)

    result = decision.execute(make_context())

    assert result.evaluations[0].rule_identifier == "scenario-consistency"
    assert result.evaluations[-1].rule_identifier == "escalation-check"


def test_duplicate_event_detection_blocks_decision() -> None:
    decision = Decision(identifier="decision-duplicate", rules=create_default_rules())

    result = decision.execute(make_context(events=[make_event("evt-a"), make_event("evt-a")]))

    assert result.outcome is DecisionOutcome.BLOCK
    duplicate_evaluation = result.evaluations[2]
    assert duplicate_evaluation.rule_identifier == "duplicate-event-detection"
    assert duplicate_evaluation.passed is False


def test_escalation_check_requires_rules_for_high_escalation() -> None:
    context = make_context()
    context.escalation_rules = []
    context.exercise_state.escalation_level = EscalationLevel.HIGH
    context.scenario.escalation_level = ScenarioEscalationLevel.HIGH
    decision = Decision(identifier="decision-escalation", rules=create_default_rules())

    result = decision.execute(context)

    assert result.outcome is DecisionOutcome.REVIEW
    assert result.evaluations[0].rule_identifier == "escalation-check"
    assert result.evaluations[0].passed is False


def test_scenario_consistency_detects_phase_mismatch() -> None:
    context = make_context()
    context.scenario.current_phase = ScenarioPhase.TRANSITION
    decision = Decision(identifier="decision-consistency", rules=create_default_rules())

    result = decision.execute(context)

    assert result.outcome is DecisionOutcome.REVIEW
    assert result.evaluations[-1].rule_identifier == "scenario-consistency"
    assert "exercise phase differs" in result.evaluations[-1].details["issues"]


def test_decision_rejects_duplicate_rule_registration() -> None:
    decision = Decision(identifier="decision-rules")
    rule = create_default_rules()[0]
    decision.register_rule(rule)

    with pytest.raises(ValueError):
        decision.register_rule(rule)
