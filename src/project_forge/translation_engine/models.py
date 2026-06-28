from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TranslationRuleType(str, Enum):
    """Supported deterministic translation rule types."""

    ONE_TO_ONE = "one_to_one"
    ALIAS = "alias"
    REGEX = "regex"


@dataclass(frozen=True, slots=True)
class TranslationRule:
    """A deterministic rule used by a translation dictionary."""

    identifier: str
    category: str
    source: str
    target: str
    rule_type: TranslationRuleType = TranslationRuleType.ONE_TO_ONE
    priority: int = 100
    aliases: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("category", self.category)
        _validate_non_empty("source", self.source)
        _validate_non_empty("target", self.target)
        if self.priority < 0:
            raise ValueError("priority must be greater than or equal to zero")
        _validate_str_list("aliases", self.aliases)
        _validate_str_list("flags", self.flags)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(slots=True)
class TranslationProfile:
    """A named subset of translation categories."""

    identifier: str
    name: str
    categories: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_str_list("categories", self.categories)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(slots=True)
class TranslationDictionary:
    """A collection of deterministic translation rules and profiles."""

    identifier: str
    name: str
    rules: list[TranslationRule] = field(default_factory=list)
    profiles: list[TranslationProfile] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")
        self.rules = sorted(
            self.rules,
            key=lambda rule: (rule.priority, rule.category, rule.identifier),
        )
        self.profiles = sorted(self.profiles, key=lambda profile: profile.identifier)

    def profile(self, identifier: str) -> TranslationProfile | None:
        for profile in self.profiles:
            if profile.identifier == identifier:
                return profile
        return None


@dataclass(slots=True)
class TranslationContext:
    """Inputs controlling a deterministic translation operation."""

    text: str
    profile_identifier: str | None = None
    categories: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.text is None:
            raise ValueError("text must not be None")
        _validate_str_list("categories", self.categories)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(frozen=True, slots=True)
class TranslationResult:
    """Result from deterministic translation."""

    original_text: str
    translated_text: str
    applied_rule_identifiers: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.original_text is None:
            raise ValueError("original_text must not be None")
        if self.translated_text is None:
            raise ValueError("translated_text must not be None")
        _validate_str_list("applied_rule_identifiers", self.applied_rule_identifiers)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")
