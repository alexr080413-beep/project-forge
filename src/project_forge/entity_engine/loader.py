from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    Affiliation,
    Capability,
    Entity,
    EntityCatalog,
    EntityCategory,
    Individual,
    Installation,
    Organization,
    Platform,
    Relationship,
    RelationshipType,
    Unit,
)


_ENTITY_TYPES: dict[EntityCategory, type[Entity]] = {
    EntityCategory.UNIT: Unit,
    EntityCategory.ORGANIZATION: Organization,
    EntityCategory.INSTALLATION: Installation,
    EntityCategory.INDIVIDUAL: Individual,
    EntityCategory.PLATFORM: Platform,
    EntityCategory.CAPABILITY: Capability,
}


class EntityLoader:
    """Loads scenario entities and relationships from a local YAML file."""

    def __init__(self, path: str | Path = "config/entities.yaml") -> None:
        self.path = Path(path)

    def load(self) -> EntityCatalog:
        config_path = self.path.resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Entity config does not exist: {config_path}")
        if not config_path.is_file():
            raise IsADirectoryError(f"Entity config is not a file: {config_path}")

        data = _load_yaml_mapping(config_path)
        return entity_catalog_from_mapping(data)


def load_entities(path: str | Path = "config/entities.yaml") -> EntityCatalog:
    """Load an entity catalog from a local YAML file."""

    return EntityLoader(path).load()


def entity_catalog_from_mapping(data: dict[str, Any]) -> EntityCatalog:
    """Build an EntityCatalog from parsed entity configuration data."""

    entities = [_load_entity(item) for item in _required_mapping_list(data, "entities")]
    relationships = [
        _load_relationship(item) for item in _optional_mapping_list(data, "relationships")
    ]
    return EntityCatalog(entities=entities, relationships=relationships)


def _load_entity(data: dict[str, Any]) -> Entity:
    category = EntityCategory(_required_str(data, "category"))
    entity_type = _ENTITY_TYPES[category]
    return entity_type(
        identifier=_required_str(data, "identifier"),
        display_name=_required_str(data, "display_name"),
        affiliation=Affiliation(_required_str(data, "affiliation")),
        description=str(data.get("description", "")),
        aliases=_optional_str_list(data, "aliases"),
        parent_organization=_optional_str(data, "parent_organization"),
        location=_optional_str(data, "location"),
        status=str(data.get("status", "active")),
        tags=_optional_str_list(data, "tags"),
        metadata=_optional_dict(data, "metadata"),
    )


def _load_relationship(data: dict[str, Any]) -> Relationship:
    return Relationship(
        source_identifier=_required_str(data, "source_identifier"),
        target_identifier=_required_str(data, "target_identifier"),
        relationship_type=RelationshipType(_required_str(data, "relationship_type")),
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
        raise ValueError("Entity config must contain a mapping at the top level")
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


def _optional_str(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
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
