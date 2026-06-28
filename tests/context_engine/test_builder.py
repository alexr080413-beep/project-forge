from project_forge.context_engine import ContextBuilder, ContextReference
from project_forge.decision_engine import Decision, DecisionOutcome, create_default_rules
from project_forge.decision_engine.models import DecisionContext
from project_forge.entity_engine import load_entities
from project_forge.event_engine import load_events
from project_forge.exercise_state import load_exercise_state
from project_forge.knowledge_engine import KnowledgeBaseLoader
from project_forge.scenario_engine import load_scenarios


def make_builder() -> ContextBuilder:
    exercise_state = load_exercise_state("config/exercise_state.example.yaml")
    scenario_registry = load_scenarios("config/scenario.example.yaml")
    entity_catalog = load_entities("config/entities.example.yaml")
    event_registry = load_events("config/events.example.yaml")
    knowledge_base = KnowledgeBaseLoader("knowledge_base").load()
    decision_context = DecisionContext(
        exercise_state=exercise_state,
        scenario=scenario_registry.get_current_scenario(),
        events=event_registry.events,
        entities=entity_catalog,
        training_objectives=["Validate EXCON decision rhythm"],
        escalation_rules=["Senior Controller approval required."],
    )
    decision_result = Decision(
        identifier="decision-context",
        rules=create_default_rules(),
    ).execute(decision_context)
    return ContextBuilder(
        knowledge_base=knowledge_base,
        exercise_state=exercise_state,
        scenario_registry=scenario_registry,
        entity_catalog=entity_catalog,
        event_registry=event_registry,
        decision_results=[decision_result],
        training_objectives=["Validate EXCON decision rhythm"],
    )


def test_build_current_context_aggregates_all_engines() -> None:
    snapshot = make_builder().build_current_context()
    context = snapshot.exercise_context

    assert snapshot.identifier == "current"
    assert snapshot.context_type == "current"
    assert context.exercise_state.exercise_name == "Forge Example Exercise"
    assert context.scenario.identifier == "scenario-forge-example"
    assert len(context.knowledge_documents) == 1
    assert len(context.entities) == 6
    assert len(context.events) == 2
    assert len(context.decision_results) == 1
    assert context.decision_results[0].outcome is DecisionOutcome.APPROVE
    assert "Validate EXCON decision rhythm" in context.training_objectives


def test_context_references_are_deterministic() -> None:
    builder = make_builder()
    first = builder.build_current_context()
    second = builder.build_current_context()

    assert first.exercise_context.training_objectives == (
        second.exercise_context.training_objectives
    )
    assert [
        reference.sort_key() for reference in first.exercise_context.references
    ] == [reference.sort_key() for reference in second.exercise_context.references]


def test_build_event_context_filters_to_requested_event() -> None:
    snapshot = make_builder().build_event_context("evt-002")
    context = snapshot.exercise_context

    assert snapshot.identifier == "event:evt-002"
    assert snapshot.metadata == {"event_identifier": "evt-002"}
    assert [event.identifier for event in context.events] == ["evt-002"]
    assert any(
        reference.reference_type == "event" and reference.identifier == "evt-002"
        for reference in context.references
    )


def test_build_entity_context_filters_entity_and_related_events() -> None:
    snapshot = make_builder().build_entity_context("platform-watchtower")
    context = snapshot.exercise_context

    assert snapshot.identifier == "entity:platform-watchtower"
    assert [entity.identifier for entity in context.entities] == ["platform-watchtower"]
    assert [event.identifier for event in context.events] == ["evt-002"]


def test_build_daily_context_filters_by_day() -> None:
    snapshot = make_builder().build_daily_context(2)

    assert snapshot.identifier == "day:2"
    assert snapshot.metadata == {"exercise_day": 2}
    assert [event.identifier for event in snapshot.exercise_context.events] == [
        "evt-001",
        "evt-002",
    ]


def test_build_daily_context_uses_current_exercise_day_by_default() -> None:
    snapshot = make_builder().build_daily_context()

    assert snapshot.identifier == "day:2"
    assert snapshot.metadata == {"exercise_day": 2}


def test_context_reference_validation_rejects_blank_identifier() -> None:
    import pytest

    with pytest.raises(ValueError):
        ContextReference(reference_type="event", identifier="")
