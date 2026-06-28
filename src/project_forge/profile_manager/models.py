from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ProfileMetadata:
    """Human-readable identity and governance data for a Forge profile."""

    profile_id: str
    display_name: str
    description: str
    exercise_type: str
    version: str = "0.1.0"
    owner: str = "Project Forge"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("profile_id", self.profile_id)
        _validate_non_empty("display_name", self.display_name)
        _validate_non_empty("description", self.description)
        _validate_non_empty("exercise_type", self.exercise_type)
        _validate_non_empty("version", self.version)
        _validate_non_empty("owner", self.owner)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ProfileComponent:
    """A profile-managed service, plugin, path, or future extension."""

    identifier: str
    component_type: str
    display_name: str = ""
    path: str = ""
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("component_type", self.component_type)
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ForgeProfile:
    """Configuration profile for one exercise environment."""

    metadata: ProfileMetadata
    enabled_services: list[str] = field(default_factory=list)
    enabled_plugins: list[str] = field(default_factory=list)
    knowledge_base_path: str = ""
    template_path: str = ""
    translation_dictionary_path: str = ""
    workflow_path: str = ""
    default_scenario: str = ""
    components: list[ProfileComponent] = field(default_factory=list)
    metadata_values: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_str_list("enabled_services", self.enabled_services)
        _validate_str_list("enabled_plugins", self.enabled_plugins)
        _validate_non_empty("knowledge_base_path", self.knowledge_base_path)
        _validate_non_empty("template_path", self.template_path)
        _validate_non_empty(
            "translation_dictionary_path",
            self.translation_dictionary_path,
        )
        _validate_non_empty("workflow_path", self.workflow_path)
        _validate_non_empty("default_scenario", self.default_scenario)
        _validate_metadata(self.metadata_values)

    @property
    def profile_id(self) -> str:
        return self.metadata.profile_id

    @property
    def display_name(self) -> str:
        return self.metadata.display_name

    @property
    def description(self) -> str:
        return self.metadata.description

    @property
    def exercise_type(self) -> str:
        return self.metadata.exercise_type


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError(f"{name} must be a list of non-empty strings")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
