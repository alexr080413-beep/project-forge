from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import IntegrationSource, IntegrationSourceType
from .registry import IntegrationRegistry, create_default_integration_connectors
from .validator import IntegrationValidator


class IntegrationSourceLoader:
    """Loads integration source definitions from a local YAML file."""

    def __init__(
        self,
        path: str | Path = "config/integration_sources.yaml",
        *,
        path_base: str | Path = ".",
        validator: IntegrationValidator | None = None,
    ) -> None:
        self.path = Path(path)
        self.validator = validator or IntegrationValidator(path_base=path_base)

    def load(self) -> IntegrationRegistry:
        config_path = self.path.resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Integration source config does not exist: {config_path}")
        if not config_path.is_file():
            raise IsADirectoryError(f"Integration source config is not a file: {config_path}")

        data = _load_yaml_mapping(config_path)
        return integration_registry_from_mapping(data, validator=self.validator)


def load_integration_sources(
    path: str | Path = "config/integration_sources.yaml",
    *,
    path_base: str | Path = ".",
) -> IntegrationRegistry:
    """Load integration sources with default dry-run connectors."""

    return IntegrationSourceLoader(path, path_base=path_base).load()


def integration_registry_from_mapping(
    data: dict[str, Any],
    *,
    validator: IntegrationValidator | None = None,
) -> IntegrationRegistry:
    sources = [_load_source(item) for item in _required_mapping_list(data, "sources")]
    return IntegrationRegistry(
        sources=sources,
        connectors=create_default_integration_connectors(),
        validator=validator or IntegrationValidator(),
    )


def _load_source(data: dict[str, Any]) -> IntegrationSource:
    return IntegrationSource(
        source_id=_required_str(data, "source_id"),
        name=_required_str(data, "name"),
        source_type=IntegrationSourceType(_required_str(data, "source_type")),
        location=_required_str(data, "location"),
        enabled=_optional_bool(data, "enabled", default=True),
        description=str(data.get("description", "")),
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
        raise ValueError("Integration source config must contain a mapping at the top level")
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


def _optional_bool(data: dict[str, Any], key: str, *, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _optional_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a dictionary")
    return dict(value)
