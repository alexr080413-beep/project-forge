from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    ProductDefinition,
    ProductMetadata,
    ProductPlugin,
    ProductTemplate,
)
from .validator import ProductValidator


class ProductPluginLoader:
    """Loads product plugin manifests from local YAML files."""

    def __init__(self, validator: ProductValidator | None = None) -> None:
        self.validator = validator or ProductValidator()

    def load(self, path: str | Path) -> ProductPlugin:
        plugin_path = Path(path).resolve()
        if not plugin_path.exists():
            raise FileNotFoundError(f"Product plugin config does not exist: {plugin_path}")
        if not plugin_path.is_file():
            raise IsADirectoryError(f"Product plugin config is not a file: {plugin_path}")

        data = _load_yaml_mapping(plugin_path)
        plugin = product_plugin_from_mapping(data, plugin_path=plugin_path)
        self.validator.validate_plugin(plugin)
        return plugin


def load_product_plugin(path: str | Path) -> ProductPlugin:
    """Load a product plugin from a local manifest file."""

    return ProductPluginLoader().load(path)


def product_plugin_from_mapping(
    data: dict[str, Any],
    *,
    plugin_path: Path | None = None,
) -> ProductPlugin:
    return ProductPlugin(
        metadata=_load_metadata(_required_mapping(data, "metadata")),
        definition=_load_definition(_required_mapping(data, "definition")),
        templates=[_load_template(item) for item in _required_mapping_list(data, "templates")],
        plugin_path=str(plugin_path or ""),
    )


def _load_metadata(data: dict[str, Any]) -> ProductMetadata:
    return ProductMetadata(
        identifier=_required_str(data, "identifier"),
        name=_required_str(data, "name"),
        version=_required_str(data, "version"),
        description=_required_str(data, "description"),
        owner=str(data.get("owner", "Project Forge")),
        tags=_optional_str_list(data, "tags"),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_definition(data: dict[str, Any]) -> ProductDefinition:
    return ProductDefinition(
        identifier=_required_str(data, "identifier"),
        product_type=_required_str(data, "product_type"),
        display_name=_required_str(data, "display_name"),
        template_identifier=_required_str(data, "template_identifier"),
        output_formats=_optional_str_list(data, "output_formats"),
        required_context=_optional_str_list(data, "required_context"),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_template(data: dict[str, Any]) -> ProductTemplate:
    return ProductTemplate(
        identifier=_required_str(data, "identifier"),
        version=_required_str(data, "version"),
        content=_required_str(data, "content"),
        required_fields=_optional_str_list(data, "required_fields"),
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
        raise ValueError("Product plugin config must contain a mapping at the top level")
    return data


def _required_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return value


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
