from pathlib import Path

import pytest

from project_forge.exercise_state import (
    EscalationLevel,
    ExerciseDay,
    ExercisePhase,
    ExerciseState,
    ExerciseStateLoader,
    ExerciseTempo,
    InformationEnvironment,
    MilitarySituation,
    PoliticalSituation,
    ScenarioSituation,
    load_exercise_state,
)


def test_exercise_state_can_be_created_directly() -> None:
    state = ExerciseState(
        exercise_name="Forge Direct Exercise",
        current_day=ExerciseDay(day_number=1, label="Training Day 1"),
        current_phase=ExercisePhase.STARTEX,
        current_operational_summary="Initial play is beginning under controller supervision.",
        scenario_situation=ScenarioSituation(
            summary="The exercise scenario is stable at start.",
            political=PoliticalSituation(summary="Political conditions are calm."),
            military=MilitarySituation(summary="Forces remain at baseline posture."),
            information_environment=InformationEnvironment(
                summary="Information activity is limited."
            ),
        ),
        active_training_objectives=["Establish shared awareness"],
        active_scenario_actors=["EXCON"],
        active_locations=["Main Operations Center"],
        recent_notional_events=["STARTEX announced"],
        constraints_or_escalation_limits=["No escalation without controller approval"],
        exercise_tempo=ExerciseTempo.STEADY,
        escalation_level=EscalationLevel.LOW,
    )

    assert state.exercise_name == "Forge Direct Exercise"
    assert state.current_phase is ExercisePhase.STARTEX
    assert state.current_day.day_number == 1
    assert state.active_training_objectives == ["Establish shared awareness"]


def test_loader_loads_example_config() -> None:
    state = load_exercise_state("config/exercise_state.example.yaml")

    assert state.exercise_name == "Forge Example Exercise"
    assert state.current_day.day_number == 2
    assert state.current_phase is ExercisePhase.EXECUTION
    assert state.exercise_tempo is ExerciseTempo.STEADY
    assert state.escalation_level is EscalationLevel.ELEVATED
    assert "Joint Task Force Headquarters" in state.active_scenario_actors
    assert state.scenario_situation.military.force_posture.startswith("Heightened readiness")


def test_loader_rejects_missing_config(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ExerciseStateLoader(tmp_path / "missing.yaml").load()


def test_loader_validates_required_fields(tmp_path: Path) -> None:
    config_path = tmp_path / "exercise_state.yaml"
    config_path.write_text(
        """
exercise_name: ""
current_day:
  day_number: 1
current_phase: execution
current_operational_summary: Missing useful name.
scenario_situation:
  summary: Placeholder.
  political:
    summary: Placeholder.
  military:
    summary: Placeholder.
  information_environment:
    summary: Placeholder.
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        ExerciseStateLoader(config_path).load()
