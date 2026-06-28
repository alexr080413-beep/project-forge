from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .models import (
    ConfigurationChangeRecord,
    ConfigurationItem,
    ConfigurationProfile,
    ConfigurationResult,
    ConfigurationScope,
    ConfigurationSource,
)
from .registry import ConfigurationRegistry
from .validator import ConfigurationValidator

_ENV_PATTERN = re.compile(r"^\$\{([A-Z0-9_]+)(?::-(.*))?\}$")


class ConfigurationLoader:
    """Loads and resolves local YAML or JSON configuration files."""

    def __init__(
        self,
        sources: list[ConfigurationSource] | None = None,
        *,
        validator: ConfigurationValidator | None = None,
    ) -> None:
        self.sources = sources or []
        self.validator = validator or ConfigurationValidator()

    def load(self) -> ConfigurationResult:
        resolved: dict[tuple[ConfigurationScope, str], ConfigurationItem] = {}
        changes: list[ConfigurationChangeRecord] = []
        sorted_sources = sorted(self.sources, key=lambda source: source.precedence)
        profiles: list[ConfigurationProfile] = []

        for source in sorted_sources:
            data = _load_mapping(Path(source.path))
            source_items = _load_items(data, source.source_id)
            for item in source_items:
                key = (item.scope, item.key)
                if key in resolved:
                    previous = resolved[key]
                    changes.append(
                        ConfigurationChangeRecord(
                            key=item.key,
                            scope=item.scope,
                            source_id=item.source_id,
                            previous_value=previous.value,
                            new_value=item.value,
                            metadata={"previous_source_id": previous.source_id},
                        )
                    )
                resolved[key] = item
            profiles.extend(_load_profiles(data, source.source_id))

        result = ConfigurationResult(
            items=list(resolved.values()),
            sources=sorted_sources,
            changes=changes,
            metadata={"source_count": len(sorted_sources)},
        )
        self.validator.validate_result(result)
        return result

    def load_registry(self) -> ConfigurationRegistry:
        result = self.load()
        profiles = _profiles_with_resolved_items(
            _load_all_profiles(self.sources),
            result.items,
        )
        return ConfigurationRegistry(
            items=result.items,
            profiles=profiles,
            validator=self.validator,
        )


def load_configuration(
    sources: list[ConfigurationSource],
) -> ConfigurationRegistry:
    """Load a configuration registry from ordered local sources."""

    return ConfigurationLoader(sources).load_registry()


def configuration_registry_from_mapping(
    data: dict[str, Any],
    *,
    source_id: str = "mapping",
) -> ConfigurationRegistry:
    items = _resolve_defaults(_load_items(data, source_id))
    profiles = _profiles_with_resolved_items(_load_profiles(data, source_id), items)
    return ConfigurationRegistry(items=items, profiles=profiles)


def _load_all_profiles(sources: list[ConfigurationSource]) -> list[ConfigurationProfile]:
    profiles: list[ConfigurationProfile] = []
    for source in sorted(sources, key=lambda item: item.precedence):
        profiles.extend(_load_profiles(_load_mapping(Path(source.path)), source.source_id))
    return profiles


def _profiles_with_resolved_items(
    profiles: list[ConfigurationProfile],
    items: list[ConfigurationItem],
) -> list[ConfigurationProfile]:
    by_scope_key = {(item.scope, item.key): item for item in items}
    resolved_profiles: list[ConfigurationProfile] = []
    for profile in profiles:
        resolved_items = [
            by_scope_key.get((item.scope, item.key), item) for item in profile.items
        ]
        resolved_profiles.append(
            ConfigurationProfile(
                profile_id=profile.profile_id,
                display_name=profile.display_name,
                items=resolved_items,
                metadata=profile.metadata,
            )
        )
    return resolved_profiles


def _load_items(data: dict[str, Any], source_id: str) -> list[ConfigurationItem]:
    return _resolve_defaults([
        _load_item(item, source_id)
        for item in _required_mapping_list(data, "items")
    ])


def _resolve_defaults(items: list[ConfigurationItem]) -> list[ConfigurationItem]:
    resolved: list[ConfigurationItem] = []
    for item in items:
        value = item.value if item.value is not None else item.default
        resolved.append(
            ConfigurationItem(
                key=item.key,
                value=_resolve_env_placeholders(value),
                scope=item.scope,
                source_id=item.source_id,
                required=item.required,
                default=_resolve_env_placeholders(item.default),
                description=item.description,
                metadata=item.metadata,
            )
        )
    return resolved


def _load_item(data: dict[str, Any], source_id: str) -> ConfigurationItem:
    return ConfigurationItem(
        key=_required_str(data, "key"),
        value=data.get("value"),
        scope=ConfigurationScope(_required_str(data, "scope")),
        source_id=source_id,
        required=_optional_bool(data, "required", default=False),
        default=data.get("default"),
        description=str(data.get("description", "")),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_profiles(data: dict[str, Any], source_id: str) -> list[ConfigurationProfile]:
    return [
        ConfigurationProfile(
            profile_id=_required_str(profile, "profile_id"),
            display_name=_required_str(profile, "display_name"),
            items=[
                _load_profile_reference(item, source_id)
                for item in _optional_mapping_list(profile, "items")
            ],
            metadata=_optional_dict(profile, "metadata"),
        )
        for profile in _optional_mapping_list(data, "profiles")
    ]


def _load_profile_reference(data: dict[str, Any], source_id: str) -> ConfigurationItem:
    return ConfigurationItem(
        key=_required_str(data, "key"),
        value=None,
        scope=ConfigurationScope(_required_str(data, "scope")),
        source_id=source_id,
    )


def _resolve_env_placeholders(value):
    if isinstance(value, str):
        match = _ENV_PATTERN.match(value)
        if match:
            env_name, fallback = match.groups()
            return os.environ.get(env_name, fallback if fallback is not None else "")
    if isinstance(value, list):
        return [_resolve_env_placeholders(item) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_env_placeholders(item) for key, item in value.items()}
    return value


def _load_mapping(path: Path) -> dict[str, Any]:
    config_path = path.resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {config_path}")
    if not config_path.is_file():
        raise IsADirectoryError(f"Configuration path is not a file: {config_path}")
    text = config_path.read_text(encoding="utf-8")
    if config_path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        try:
            import yaml  # type: ignore[import-not-found]
        except ModuleNotFoundError:
            data = json.loads(text)
        else:
            data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a mapping at the top level")
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


def _optional_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a dictionary")
    return dict(value)
