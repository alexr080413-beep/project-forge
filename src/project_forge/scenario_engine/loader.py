from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
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
from .registry import ScenarioRegistry


class ScenarioLoader:
    """Loads scenarios from a local YAML file."""

    def __init__(self, path: str | Path = "config/scenario.yaml") -> None:
        self.path = Path(path)

    def load(self) -> ScenarioRegistry:
        config_path = self.path.resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Scenario config does not exist: {config_path}")
        if not config_path.is_file():
            raise IsADirectoryError(f"Scenario config is not a file: {config_path}")

        data = _load_yaml_mapping(config_path)
        return scenario_registry_from_mapping(data)


def load_scenarios(path: str | Path = "config/scenario.yaml") -> ScenarioRegistry:
    """Load a scenario registry from a local YAML file."""

    return ScenarioLoader(path).load()


def scenario_registry_from_mapping(data: dict[str, Any]) -> ScenarioRegistry:
    """Build a ScenarioRegistry from parsed scenario configuration data."""

    scenarios = [_load_scenario(item) for item in _required_mapping_list(data, "scenarios")]
    return ScenarioRegistry(scenarios=scenarios)


def _load_scenario(data: dict[str, Any]) -> Scenario:
    return Scenario(
        identifier=_required_str(data, "identifier"),
        scenario_name=_required_str(data, "scenario_name"),
        description=_required_str(data, "description"),
        current_exercise_day=_required_int(data, "current_exercise_day"),
        current_phase=ScenarioPhase(_required_str(data, "current_phase")),
        active_objectives=[
            _load_objective(item)
            for item in _optional_mapping_list(data, "active_objectives")
        ],
        active_constraints=[
            _load_constraint(item)
            for item in _optional_mapping_list(data, "active_constraints")
        ],
        active_assumptions=[
            _load_assumption(item)
            for item in _optional_mapping_list(data, "active_assumptions")
        ],
        active_control_measures=[
            _load_control_measure(item)
            for item in _optional_mapping_list(data, "active_control_measures")
        ],
        escalation_level=ScenarioEscalationLevel(
            data.get("escalation_level", ScenarioEscalationLevel.LOW.value)
        ),
        tempo=ScenarioTempo(data.get("tempo", ScenarioTempo.STEADY.value)),
        related_entities=_optional_str_list(data, "related_entities"),
        related_events=_optional_str_list(data, "related_events"),
        related_knowledge_documents=_optional_str_list(
            data,
            "related_knowledge_documents",
        ),
        metadata=_optional_dict(data, "metadata"),
        status=ScenarioStatus(data.get("status", ScenarioStatus.DRAFT.value)),
    )


def _load_objective(data: dict[str, Any]) -> ScenarioObjective:
    return ScenarioObjective(
        identifier=_required_str(data, "identifier"),
        title=_required_str(data, "title"),
        description=str(data.get("description", "")),
        status=str(data.get("status", "active")),
        tags=_optional_str_list(data, "tags"),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_constraint(data: dict[str, Any]) -> ScenarioConstraint:
    return ScenarioConstraint(
        identifier=_required_str(data, "identifier"),
        description=_required_str(data, "description"),
        severity=str(data.get("severity", "standard")),
        tags=_optional_str_list(data, "tags"),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_assumption(data: dict[str, Any]) -> ScenarioAssumption:
    return ScenarioAssumption(
        identifier=_required_str(data, "identifier"),
        description=_required_str(data, "description"),
        confidence=_required_float(data, "confidence", default=1.0),
        tags=_optional_str_list(data, "tags"),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_control_measure(data: dict[str, Any]) -> ScenarioControlMeasure:
    return ScenarioControlMeasure(
        identifier=_required_str(data, "identifier"),
        title=_required_str(data, "title"),
        description=_required_str(data, "description"),
        owner=str(data.get("owner", "EXCON")),
        tags=_optional_str_list(data, "tags"),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)

    if not isinstance(data, dict):
        raise ValueError("Scenario config must contain a mapping at the top level")
    return data


def _required_mapping_list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{key} must be a list of mappings")
    return value


def _optional_mapping_list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{key} must be a list of mappings")
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


def _required_float(
    data: dict[str, Any],
    key: str,
    *,
    default: float | None = None,
) -> float:
    value = data.get(key, default)
    if not isinstance(value, int | float):
        raise ValueError(f"{key} must be a number")
    return float(value)


def _optional_str_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a list of strings")
    return list(value)


def _optional_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a dictionary")
    return dict(value)
