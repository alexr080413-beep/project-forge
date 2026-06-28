from pathlib import Path

import pytest

from project_forge.scenario_engine import (
    Scenario,
    ScenarioAssumption,
    ScenarioConstraint,
    ScenarioControlMeasure,
    ScenarioEscalationLevel,
    ScenarioLoader,
    ScenarioObjective,
    ScenarioPhase,
    ScenarioRegistry,
    ScenarioStatus,
    ScenarioTempo,
    ScenarioValidator,
    load_scenarios,
)


def make_scenario(identifier: str = "scenario-test") -> Scenario:
    return Scenario(
        identifier=identifier,
        scenario_name="Test Scenario",
        description="A notional scenario for tests.",
        current_exercise_day=2,
        current_phase=ScenarioPhase.EXECUTION,
        active_objectives=[
            ScenarioObjective(
                identifier="obj-1",
                title="Maintain awareness",
                description="Keep the scenario picture aligned.",
            )
        ],
        active_constraints=[
            ScenarioConstraint(
                identifier="constraint-1",
                description="No escalation without approval.",
                severity="high",
            )
        ],
        active_assumptions=[
            ScenarioAssumption(
                identifier="assumption-1",
                description="Scenario activity remains notional.",
                confidence=0.8,
            )
        ],
        active_control_measures=[
            ScenarioControlMeasure(
                identifier="cm-1",
                title="Release Authority",
                description="Senior Controller approves sensitive scenario changes.",
            )
        ],
        escalation_level=ScenarioEscalationLevel.ELEVATED,
        tempo=ScenarioTempo.STEADY,
        related_entities=["unit-jtf-hq"],
        related_events=["evt-001"],
        related_knowledge_documents=["knowledge_base/README.md"],
        metadata={"notional": True},
        status=ScenarioStatus.CURRENT,
    )


def test_scenario_can_be_created_directly() -> None:
    scenario = make_scenario()

    assert scenario.identifier == "scenario-test"
    assert scenario.current_phase is ScenarioPhase.EXECUTION
    assert scenario.escalation_level is ScenarioEscalationLevel.ELEVATED
    assert scenario.tempo is ScenarioTempo.STEADY


def test_loader_loads_example_scenario() -> None:
    registry = load_scenarios("config/scenario.example.yaml")
    current = registry.get_current_scenario()

    assert current is not None
    assert current.identifier == "scenario-forge-example"
    assert current.status is ScenarioStatus.CURRENT
    assert current.current_phase is ScenarioPhase.EXECUTION
    assert current.related_events == ["evt-001", "evt-002"]


def test_registry_supports_lookup_by_id_and_current_scenario() -> None:
    current = make_scenario("scenario-current")
    archived = make_scenario("scenario-archived")
    archived.status = ScenarioStatus.ARCHIVED
    registry = ScenarioRegistry(scenarios=[current, archived])

    assert registry.get_scenario("scenario-archived") is archived
    assert registry.get_scenario("missing") is None
    assert registry.get_current_scenario() is current


def test_registry_uses_first_scenario_as_current_fallback() -> None:
    scenario = make_scenario("scenario-fallback")
    scenario.status = ScenarioStatus.ACTIVE
    registry = ScenarioRegistry(scenarios=[scenario])

    assert registry.get_current_scenario() is scenario


def test_registry_can_add_current_scenario_after_non_current_scenario() -> None:
    existing = make_scenario("scenario-existing")
    existing.status = ScenarioStatus.ACTIVE
    current = make_scenario("scenario-current")
    registry = ScenarioRegistry(scenarios=[existing])

    registry.add_scenario(current)

    assert registry.get_current_scenario() is current


def test_validator_accepts_valid_scenario() -> None:
    ScenarioValidator().validate_scenario(make_scenario())


def test_validator_rejects_duplicate_scenario_identifiers() -> None:
    first = make_scenario("scenario-dup")
    second = make_scenario("scenario-dup")
    second.status = ScenarioStatus.ARCHIVED

    with pytest.raises(ValueError):
        ScenarioRegistry(scenarios=[first, second])


def test_validator_rejects_multiple_current_scenarios() -> None:
    with pytest.raises(ValueError):
        ScenarioRegistry(
            scenarios=[make_scenario("scenario-a"), make_scenario("scenario-b")]
        )


def test_validator_rejects_scenario_without_objectives() -> None:
    scenario = make_scenario()
    scenario.active_objectives = []

    with pytest.raises(ValueError):
        ScenarioValidator().validate_scenario(scenario)


def test_model_rejects_invalid_assumption_confidence() -> None:
    with pytest.raises(ValueError):
        ScenarioAssumption(
            identifier="assumption-bad",
            description="Invalid confidence.",
            confidence=1.5,
        )


def test_loader_rejects_missing_config(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ScenarioLoader(tmp_path / "missing.yaml").load()
