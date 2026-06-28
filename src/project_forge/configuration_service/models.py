from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ConfigurationScope(str, Enum):
    """Supported configuration ownership scopes."""

    PLATFORM = "platform"
    SERVICE = "service"
    PROFILE = "profile"
    WORKFLOW = "workflow"
    PLUGIN = "plugin"
    ENVIRONMENT = "environment"
    USER = "user"


@dataclass(frozen=True, slots=True)
class ConfigurationSource:
    """A local configuration source with deterministic precedence."""

    source_id: str
    path: str
    precedence: int = 100
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("source_id", self.source_id)
        _validate_non_empty("path", self.path)
        if self.precedence < 0:
            raise ValueError("precedence must not be negative")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ConfigurationItem:
    """One resolved configuration value."""

    key: str
    value: Any
    scope: ConfigurationScope
    source_id: str = "default"
    required: bool = False
    default: Any = None
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("key", self.key)
        _validate_non_empty("source_id", self.source_id)
        if not isinstance(self.required, bool):
            raise ValueError("required must be a boolean")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ConfigurationProfile:
    """A named configuration profile composed from resolved items."""

    profile_id: str
    display_name: str
    items: list[ConfigurationItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("profile_id", self.profile_id)
        _validate_non_empty("display_name", self.display_name)
        if not all(isinstance(item, ConfigurationItem) for item in self.items):
            raise ValueError("items must be a list of ConfigurationItem instances")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ConfigurationChangeRecord:
    """Audit-ready record of a resolved configuration change."""

    key: str
    scope: ConfigurationScope
    source_id: str
    previous_value: Any
    new_value: Any
    reason: str = "override"
    changed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("key", self.key)
        _validate_non_empty("source_id", self.source_id)
        _validate_non_empty("reason", self.reason)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ConfigurationResult:
    """Result of loading and resolving configuration sources."""

    items: list[ConfigurationItem]
    sources: list[ConfigurationSource] = field(default_factory=list)
    changes: list[ConfigurationChangeRecord] = field(default_factory=list)
    loaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all(isinstance(item, ConfigurationItem) for item in self.items):
            raise ValueError("items must be a list of ConfigurationItem instances")
        if not all(isinstance(source, ConfigurationSource) for source in self.sources):
            raise ValueError("sources must be a list of ConfigurationSource instances")
        if not all(isinstance(change, ConfigurationChangeRecord) for change in self.changes):
            raise ValueError("changes must be a list of ConfigurationChangeRecord instances")
        _validate_metadata(self.metadata)


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
