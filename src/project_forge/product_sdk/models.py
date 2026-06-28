from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class ProductMetadata:
    """Human-readable metadata for a product plugin."""

    identifier: str
    name: str
    version: str
    description: str
    owner: str = "Project Forge"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("version", self.version)
        _validate_non_empty("description", self.description)
        _validate_non_empty("owner", self.owner)
        _validate_str_list("tags", self.tags)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ProductTemplate:
    """A reusable template definition for a product plugin."""

    identifier: str
    version: str
    content: str
    required_fields: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("version", self.version)
        _validate_non_empty("content", self.content)
        _validate_str_list("required_fields", self.required_fields)
        _validate_metadata(self.metadata)

    @property
    def template_key(self) -> str:
        return f"{self.identifier}:{self.version}"


@dataclass(frozen=True, slots=True)
class ProductDefinition:
    """Structured product definition exposed by a plugin."""

    identifier: str
    product_type: str
    display_name: str
    template_identifier: str
    output_formats: list[str] = field(default_factory=list)
    required_context: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("product_type", self.product_type)
        _validate_non_empty("display_name", self.display_name)
        _validate_non_empty("template_identifier", self.template_identifier)
        _validate_str_list("output_formats", self.output_formats)
        _validate_str_list("required_context", self.required_context)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ProductOutput:
    """Formatter output container. This is not report generation."""

    plugin_identifier: str
    product_identifier: str
    content: str
    output_format: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("plugin_identifier", self.plugin_identifier)
        _validate_non_empty("product_identifier", self.product_identifier)
        _validate_non_empty("output_format", self.output_format)
        if self.content is None:
            raise ValueError("content must not be None")
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class ProductPlugin:
    """A loaded product plugin definition."""

    metadata: ProductMetadata
    definition: ProductDefinition
    templates: list[ProductTemplate] = field(default_factory=list)
    plugin_path: str = ""

    def __post_init__(self) -> None:
        if self.definition.template_identifier not in {
            template.identifier for template in self.templates
        }:
            raise ValueError("definition template_identifier must match a template")
        self.templates = sorted(self.templates, key=lambda template: template.template_key)

    @property
    def identifier(self) -> str:
        return self.metadata.identifier

    def get_template(self, identifier: str, version: str | None = None) -> ProductTemplate | None:
        candidates = [
            template
            for template in self.templates
            if template.identifier == identifier
            and (version is None or template.version == version)
        ]
        if not candidates:
            return None
        return sorted(candidates, key=lambda template: template.version)[-1]


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
