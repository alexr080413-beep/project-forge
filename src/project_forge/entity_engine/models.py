from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Affiliation(str, Enum):
    """Exercise affiliation for a scenario entity."""

    FRIENDLY = "friendly"
    ADVERSARY = "adversary"
    NEUTRAL = "neutral"
    CIVILIAN = "civilian"
    EXERCISE_CONTROL = "exercise_control"


class EntityCategory(str, Enum):
    """Supported entity categories."""

    UNIT = "unit"
    ORGANIZATION = "organization"
    INSTALLATION = "installation"
    INDIVIDUAL = "individual"
    PLATFORM = "platform"
    CAPABILITY = "capability"


class RelationshipType(str, Enum):
    """Supported relationships between entities."""

    SUPPORTS = "supports"
    COMMANDS = "commands"
    ATTACHED_TO = "attached_to"
    LOCATED_AT = "located_at"
    COMMUNICATES_WITH = "communicates_with"
    OPPOSES = "opposes"


@dataclass(slots=True)
class Entity:
    """A scenario entity known to Project Forge."""

    identifier: str
    display_name: str
    affiliation: Affiliation
    category: EntityCategory
    description: str = ""
    aliases: list[str] = field(default_factory=list)
    parent_organization: str | None = None
    location: str | None = None
    status: str = "active"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("display_name", self.display_name)
        _validate_non_empty("status", self.status)
        _validate_str_list("aliases", self.aliases)
        _validate_str_list("tags", self.tags)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(slots=True)
class Unit(Entity):
    """A military or exercise unit."""

    category: EntityCategory = EntityCategory.UNIT


@dataclass(slots=True)
class Organization(Entity):
    """A formal organization represented in the scenario."""

    category: EntityCategory = EntityCategory.ORGANIZATION


@dataclass(slots=True)
class Installation(Entity):
    """A site, base, facility, or installation."""

    category: EntityCategory = EntityCategory.INSTALLATION


@dataclass(slots=True)
class Individual(Entity):
    """A named individual or role in the scenario."""

    category: EntityCategory = EntityCategory.INDIVIDUAL


@dataclass(slots=True)
class Platform(Entity):
    """A vehicle, system, or other operational platform."""

    category: EntityCategory = EntityCategory.PLATFORM


@dataclass(slots=True)
class Capability(Entity):
    """A capability available to a scenario actor."""

    category: EntityCategory = EntityCategory.CAPABILITY


@dataclass(frozen=True, slots=True)
class Relationship:
    """A typed relationship between two scenario entities."""

    source_identifier: str
    target_identifier: str
    relationship_type: RelationshipType
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("source_identifier", self.source_identifier)
        _validate_non_empty("target_identifier", self.target_identifier)
        if self.source_identifier == self.target_identifier:
            raise ValueError("relationship source and target must be different")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def validate_entity_references(self, entity_identifiers: set[str]) -> None:
        """Validate that both relationship endpoints exist in an entity set."""

        if self.source_identifier not in entity_identifiers:
            raise ValueError(f"relationship source not found: {self.source_identifier}")
        if self.target_identifier not in entity_identifiers:
            raise ValueError(f"relationship target not found: {self.target_identifier}")


@dataclass(slots=True)
class EntityCatalog:
    """Loaded entities and their validated relationships."""

    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_unique_entity_identifiers()
        self._validate_relationship_references()

    def get_entity(self, identifier: str) -> Entity | None:
        for entity in self.entities:
            if entity.identifier == identifier:
                return entity
        return None

    def relationships_for(
        self,
        identifier: str,
        relationship_type: RelationshipType | None = None,
    ) -> list[Relationship]:
        relationships = [
            relationship
            for relationship in self.relationships
            if relationship.source_identifier == identifier
            or relationship.target_identifier == identifier
        ]
        if relationship_type is None:
            return relationships
        return [
            relationship
            for relationship in relationships
            if relationship.relationship_type is relationship_type
        ]

    def _validate_unique_entity_identifiers(self) -> None:
        identifiers = [entity.identifier for entity in self.entities]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("entity identifiers must be unique")

    def _validate_relationship_references(self) -> None:
        identifiers = {entity.identifier for entity in self.entities}
        for relationship in self.relationships:
            relationship.validate_entity_references(identifiers)


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")
