from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import (
    EventImpact,
    EventSeverity,
    EventSource,
    EventStatus,
    EventType,
    ExerciseEvent,
)
from .registry import EventRegistry


class EventLoader:
    """Loads exercise events from a local YAML file."""

    def __init__(self, path: str | Path = "config/events.yaml") -> None:
        self.path = Path(path)

    def load(self) -> EventRegistry:
        config_path = self.path.resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Event config does not exist: {config_path}")
        if not config_path.is_file():
            raise IsADirectoryError(f"Event config is not a file: {config_path}")

        data = _load_yaml_mapping(config_path)
        return event_registry_from_mapping(data)


def load_events(path: str | Path = "config/events.yaml") -> EventRegistry:
    """Load an event registry from a local YAML file."""

    return EventLoader(path).load()


def event_registry_from_mapping(data: dict[str, Any]) -> EventRegistry:
    """Build an EventRegistry from parsed event configuration data."""

    events = [_load_event(item) for item in _required_mapping_list(data, "events")]
    return EventRegistry(events=events)


def _load_event(data: dict[str, Any]) -> ExerciseEvent:
    return ExerciseEvent(
        identifier=_required_str(data, "identifier"),
        title=_required_str(data, "title"),
        summary=_required_str(data, "summary"),
        event_type=EventType(_required_str(data, "event_type")),
        originating_source=EventSource(_required_str(data, "originating_source")),
        scenario_actors_involved=_optional_str_list(data, "scenario_actors_involved"),
        locations_involved=_optional_str_list(data, "locations_involved"),
        timestamp=_parse_datetime(_required_str(data, "timestamp")),
        exercise_day=_required_int(data, "exercise_day"),
        exercise_phase=_required_str(data, "exercise_phase"),
        confidence=_required_float(data, "confidence"),
        impacts=[_load_impact(item) for item in _optional_mapping_list(data, "impacts")],
        related_entities=_optional_str_list(data, "related_entities"),
        supporting_source_references=_optional_str_list(
            data,
            "supporting_source_references",
        ),
        tags=_optional_str_list(data, "tags"),
        metadata=_optional_dict(data, "metadata"),
        status=EventStatus(data.get("status", EventStatus.DRAFT.value)),
    )


def _load_impact(data: dict[str, Any]) -> EventImpact:
    return EventImpact(
        area=_required_str(data, "area"),
        severity=EventSeverity(_required_str(data, "severity")),
        summary=_required_str(data, "summary"),
        affected_entities=_optional_str_list(data, "affected_entities"),
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
        raise ValueError("Event config must contain a mapping at the top level")
    return data


def _parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"timestamp must be an ISO 8601 datetime: {value}") from error


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


def _required_float(data: dict[str, Any], key: str) -> float:
    value = data.get(key)
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
