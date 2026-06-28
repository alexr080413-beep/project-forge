from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ExercisePhase(str, Enum):
    """High-level phase of exercise play."""

    SETUP = "setup"
    STARTEX = "startex"
    EXECUTION = "execution"
    TRANSITION = "transition"
    ENDEX = "endex"
    AFTER_ACTION = "after_action"


class ExerciseTempo(str, Enum):
    """Current operating tempo for controller and scenario activity."""

    PAUSED = "paused"
    SLOW = "slow"
    STEADY = "steady"
    FAST = "fast"
    SURGE = "surge"


class EscalationLevel(str, Enum):
    """Current scenario escalation level."""

    LOW = "low"
    ELEVATED = "elevated"
    HIGH = "high"
    CRISIS = "crisis"


@dataclass(slots=True)
class ExerciseDay:
    """The current day marker in exercise time."""

    day_number: int
    label: str = ""

    def __post_init__(self) -> None:
        if self.day_number < 1:
            raise ValueError("day_number must be greater than zero")


@dataclass(slots=True)
class PoliticalSituation:
    """Political context active in the exercise scenario."""

    summary: str
    key_dynamics: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_non_empty("summary", self.summary)


@dataclass(slots=True)
class MilitarySituation:
    """Military context active in the exercise scenario."""

    summary: str
    force_posture: str = ""
    key_dynamics: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_non_empty("summary", self.summary)


@dataclass(slots=True)
class InformationEnvironment:
    """Information environment context active in the exercise scenario."""

    summary: str
    active_narratives: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_non_empty("summary", self.summary)


@dataclass(slots=True)
class ScenarioSituation:
    """Combined scenario situation used to frame exercise state."""

    summary: str
    political: PoliticalSituation
    military: MilitarySituation
    information_environment: InformationEnvironment

    def __post_init__(self) -> None:
        _validate_non_empty("summary", self.summary)


@dataclass(slots=True)
class ExerciseState:
    """Current state of exercise play for scenario-consistent workflows."""

    exercise_name: str
    current_day: ExerciseDay
    current_phase: ExercisePhase
    current_operational_summary: str
    scenario_situation: ScenarioSituation
    active_training_objectives: list[str] = field(default_factory=list)
    active_scenario_actors: list[str] = field(default_factory=list)
    active_locations: list[str] = field(default_factory=list)
    recent_notional_events: list[str] = field(default_factory=list)
    constraints_or_escalation_limits: list[str] = field(default_factory=list)
    exercise_tempo: ExerciseTempo = ExerciseTempo.STEADY
    escalation_level: EscalationLevel = EscalationLevel.LOW

    def __post_init__(self) -> None:
        _validate_non_empty("exercise_name", self.exercise_name)
        _validate_non_empty(
            "current_operational_summary",
            self.current_operational_summary,
        )


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")
