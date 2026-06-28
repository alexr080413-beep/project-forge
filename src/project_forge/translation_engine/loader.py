from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    TranslationDictionary,
    TranslationProfile,
    TranslationRule,
    TranslationRuleType,
)
from .registry import TranslationRegistry


class TranslationDictionaryLoader:
    """Loads translation dictionaries from a local YAML file."""

    def __init__(self, path: str | Path = "config/translation_dictionaries.yaml") -> None:
        self.path = Path(path)

    def load(self) -> TranslationRegistry:
        config_path = self.path.resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Translation config does not exist: {config_path}")
        if not config_path.is_file():
            raise IsADirectoryError(f"Translation config is not a file: {config_path}")

        data = _load_yaml_mapping(config_path)
        return translation_registry_from_mapping(data)


def load_translation_dictionary(
    path: str | Path = "config/translation_dictionaries.yaml",
) -> TranslationRegistry:
    """Load a translation registry from a local YAML file."""

    return TranslationDictionaryLoader(path).load()


def translation_registry_from_mapping(data: dict[str, Any]) -> TranslationRegistry:
    dictionaries = [
        _load_dictionary(item) for item in _required_mapping_list(data, "dictionaries")
    ]
    return TranslationRegistry(dictionaries=dictionaries)


def _load_dictionary(data: dict[str, Any]) -> TranslationDictionary:
    return TranslationDictionary(
        identifier=_required_str(data, "identifier"),
        name=_required_str(data, "name"),
        rules=[_load_rule(item) for item in _optional_mapping_list(data, "rules")],
        profiles=[
            _load_profile(item) for item in _optional_mapping_list(data, "profiles")
        ],
        metadata=_optional_dict(data, "metadata"),
    )


def _load_rule(data: dict[str, Any]) -> TranslationRule:
    return TranslationRule(
        identifier=_required_str(data, "identifier"),
        category=_required_str(data, "category"),
        source=_required_str(data, "source"),
        target=_required_str(data, "target"),
        rule_type=TranslationRuleType(data.get("rule_type", TranslationRuleType.ONE_TO_ONE.value)),
        priority=_optional_int(data, "priority", default=100),
        aliases=_optional_str_list(data, "aliases"),
        flags=_optional_str_list(data, "flags"),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_profile(data: dict[str, Any]) -> TranslationProfile:
    return TranslationProfile(
        identifier=_required_str(data, "identifier"),
        name=_required_str(data, "name"),
        categories=_optional_str_list(data, "categories"),
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
        raise ValueError("Translation config must contain a mapping at the top level")
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
