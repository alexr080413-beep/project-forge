from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import (
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


class ExerciseStateLoader:
    """Loads exercise state from a local YAML configuration file."""

    def __init__(self, path: str | Path = "config/exercise_state.yaml") -> None:
        self.path = Path(path)

    def load(self) -> ExerciseState:
        config_path = self.path.resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Exercise state config does not exist: {config_path}")
        if not config_path.is_file():
            raise IsADirectoryError(f"Exercise state config is not a file: {config_path}")

        data = _load_yaml_mapping(config_path)
        return exercise_state_from_mapping(data)


def load_exercise_state(path: str | Path = "config/exercise_state.yaml") -> ExerciseState:
    """Load an ExerciseState from a local YAML file."""

    return ExerciseStateLoader(path).load()


def exercise_state_from_mapping(data: dict[str, Any]) -> ExerciseState:
    """Build an ExerciseState from a parsed configuration mapping."""

    scenario_situation = _required_mapping(data, "scenario_situation")
    return ExerciseState(
        exercise_name=_required_str(data, "exercise_name"),
        current_day=_load_exercise_day(_required_mapping(data, "current_day")),
        current_phase=ExercisePhase(_required_str(data, "current_phase")),
        current_operational_summary=_required_str(data, "current_operational_summary"),
        scenario_situation=_load_scenario_situation(scenario_situation),
        active_training_objectives=_optional_str_list(data, "active_training_objectives"),
        active_scenario_actors=_optional_str_list(data, "active_scenario_actors"),
        active_locations=_optional_str_list(data, "active_locations"),
        recent_notional_events=_optional_str_list(data, "recent_notional_events"),
        constraints_or_escalation_limits=_optional_str_list(
            data,
            "constraints_or_escalation_limits",
        ),
        exercise_tempo=ExerciseTempo(data.get("exercise_tempo", ExerciseTempo.STEADY.value)),
        escalation_level=EscalationLevel(data.get("escalation_level", EscalationLevel.LOW.value)),
    )


def _load_exercise_day(data: dict[str, Any]) -> ExerciseDay:
    return ExerciseDay(
        day_number=_required_int(data, "day_number"),
        label=str(data.get("label", "")),
    )


def _load_scenario_situation(data: dict[str, Any]) -> ScenarioSituation:
    return ScenarioSituation(
        summary=_required_str(data, "summary"),
        political=_load_political_situation(_required_mapping(data, "political")),
        military=_load_military_situation(_required_mapping(data, "military")),
        information_environment=_load_information_environment(
            _required_mapping(data, "information_environment")
        ),
    )


def _load_political_situation(data: dict[str, Any]) -> PoliticalSituation:
    return PoliticalSituation(
        summary=_required_str(data, "summary"),
        key_dynamics=_optional_str_list(data, "key_dynamics"),
    )


def _load_military_situation(data: dict[str, Any]) -> MilitarySituation:
    return MilitarySituation(
        summary=_required_str(data, "summary"),
        force_posture=str(data.get("force_posture", "")),
        key_dynamics=_optional_str_list(data, "key_dynamics"),
    )


def _load_information_environment(data: dict[str, Any]) -> InformationEnvironment:
    return InformationEnvironment(
        summary=_required_str(data, "summary"),
        active_narratives=_optional_str_list(data, "active_narratives"),
    )


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        data = _parse_simple_yaml(text)
    else:
        data = yaml.safe_load(text)

    if not isinstance(data, dict):
        raise ValueError("Exercise state config must contain a mapping at the top level")
    return data


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    lines = _meaningful_yaml_lines(text)
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any] | list[Any]]] = [(-1, root)]

    for index, raw_line in enumerate(lines):
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]

        if line.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"List item without list parent: {line}")
            parent.append(_parse_scalar(line[2:]))
            continue

        key, separator, raw_value = line.partition(":")
        if not separator:
            raise ValueError(f"Invalid YAML line: {line}")
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            raise ValueError("YAML mapping keys must not be empty")
        if not isinstance(parent, dict):
            raise ValueError(f"Mapping item without mapping parent: {line}")

        if raw_value:
            parent[key] = _parse_scalar(raw_value)
            continue

        child: dict[str, Any] | list[Any]
        child = [] if _next_line_is_list(lines, index, indent) else {}
        parent[key] = child
        stack.append((indent, child))

    return root


def _meaningful_yaml_lines(text: str) -> list[str]:
    return [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _next_line_is_list(lines: list[str], index: int, indent: int) -> bool:
    if index + 1 >= len(lines):
        return False
    next_line = lines[index + 1]
    next_indent = len(next_line) - len(next_line.lstrip(" "))
    return next_indent > indent and next_line.strip().startswith("- ")


def _parse_scalar(value: str) -> str | int | bool | None:
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def _required_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return value


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _optional_str_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a list of strings")
    return list(value)
