from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ForgeProfile, ProfileComponent, ProfileMetadata
from .registry import ProfileRegistry
from .validator import ProfileValidator


class ProfileLoader:
    """Loads Forge profiles from a local YAML file."""

    def __init__(
        self,
        path: str | Path = "config/profiles.yaml",
        *,
        path_base: str | Path = ".",
        validator: ProfileValidator | None = None,
    ) -> None:
        self.path = Path(path)
        self.path_base = Path(path_base)
        self.validator = validator or ProfileValidator(path_base=self.path_base)

    def load(self) -> ProfileRegistry:
        config_path = self.path.resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Profile config does not exist: {config_path}")
        if not config_path.is_file():
            raise IsADirectoryError(f"Profile config is not a file: {config_path}")

        data = _load_yaml_mapping(config_path)
        return profile_registry_from_mapping(data, validator=self.validator)


def load_profiles(
    path: str | Path = "config/profiles.yaml",
    *,
    path_base: str | Path = ".",
) -> ProfileRegistry:
    """Load a profile registry from a local YAML file."""

    return ProfileLoader(path, path_base=path_base).load()


def profile_registry_from_mapping(
    data: dict[str, Any],
    *,
    validator: ProfileValidator | None = None,
) -> ProfileRegistry:
    profiles = [
        _load_profile(item) for item in _required_mapping_list(data, "profiles")
    ]
    return ProfileRegistry(
        profiles=profiles,
        validator=validator or ProfileValidator(),
    )


def _load_profile(data: dict[str, Any]) -> ForgeProfile:
    profile_metadata = ProfileMetadata(
        profile_id=_required_str(data, "profile_id"),
        display_name=_required_str(data, "display_name"),
        description=_required_str(data, "description"),
        exercise_type=_required_str(data, "exercise_type"),
        version=str(data.get("version", "0.1.0")),
        owner=str(data.get("owner", "Project Forge")),
        metadata=_optional_dict(data, "metadata"),
    )
    return ForgeProfile(
        metadata=profile_metadata,
        enabled_services=_optional_str_list(data, "enabled_services"),
        enabled_plugins=_optional_str_list(data, "enabled_plugins"),
        knowledge_base_path=_required_str(data, "knowledge_base_path"),
        template_path=_required_str(data, "template_path"),
        translation_dictionary_path=_required_str(
            data,
            "translation_dictionary_path",
        ),
        workflow_path=_required_str(data, "workflow_path"),
        default_scenario=_required_str(data, "default_scenario"),
        components=[
            _load_component(item)
            for item in _optional_mapping_list(data, "components")
        ],
        metadata_values=_optional_dict(data, "profile_metadata"),
    )


def _load_component(data: dict[str, Any]) -> ProfileComponent:
    return ProfileComponent(
        identifier=_required_str(data, "identifier"),
        component_type=_required_str(data, "component_type"),
        display_name=str(data.get("display_name", "")),
        path=str(data.get("path", "")),
        enabled=_optional_bool(data, "enabled", default=True),
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
        raise ValueError("Profile config must contain a mapping at the top level")
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
    return list(value)


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
