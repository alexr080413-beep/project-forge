from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Workflow, WorkflowStep
from .registry import WorkflowRegistry


class WorkflowLoader:
    """Loads workflow definitions from a local YAML file."""

    def __init__(self, path: str | Path = "config/workflows.yaml") -> None:
        self.path = Path(path)

    def load(self) -> WorkflowRegistry:
        config_path = self.path.resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Workflow config does not exist: {config_path}")
        if not config_path.is_file():
            raise IsADirectoryError(f"Workflow config is not a file: {config_path}")

        data = _load_yaml_mapping(config_path)
        return workflow_registry_from_mapping(data)


def load_workflows(path: str | Path = "config/workflows.yaml") -> WorkflowRegistry:
    """Load a workflow registry from a local YAML file."""

    return WorkflowLoader(path).load()


def workflow_registry_from_mapping(data: dict[str, Any]) -> WorkflowRegistry:
    workflows = [
        _load_workflow(item) for item in _required_mapping_list(data, "workflows")
    ]
    return WorkflowRegistry(workflows=workflows)


def _load_workflow(data: dict[str, Any]) -> Workflow:
    return Workflow(
        identifier=_required_str(data, "identifier"),
        name=_required_str(data, "name"),
        description=_required_str(data, "description"),
        steps=[_load_step(item) for item in _required_mapping_list(data, "steps")],
        metadata=_optional_dict(data, "metadata"),
    )


def _load_step(data: dict[str, Any]) -> WorkflowStep:
    return WorkflowStep(
        identifier=_required_str(data, "identifier"),
        name=_required_str(data, "name"),
        action=_required_str(data, "action"),
        dependencies=_optional_str_list(data, "dependencies"),
        condition_key=_optional_str(data, "condition_key"),
        condition_equals=data.get("condition_equals"),
        max_attempts=_optional_int(data, "max_attempts", default=1),
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
        raise ValueError("Workflow config must contain a mapping at the top level")
    return data


def _required_mapping_list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{key} must be a list of mappings")
    return value


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _optional_str(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _optional_int(data: dict[str, Any], key: str, *, default: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


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
