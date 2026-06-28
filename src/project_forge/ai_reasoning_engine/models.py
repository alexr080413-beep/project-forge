from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderType(str, Enum):
    """Supported provider abstractions."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    GOVERNMENT_HOSTED_LLM = "government_hosted_llm"
    OFFLINE_STUB = "offline_stub"


@dataclass(frozen=True, slots=True)
class ModelConfiguration:
    """Model configuration for future provider implementations."""

    provider_type: ProviderType
    model_name: str
    temperature: float = 0.0
    max_tokens: int = 1000
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("model_name", self.model_name)
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be greater than zero")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    """Versioned prompt template used by the prompt builder."""

    identifier: str
    version: str
    system_prompt: str
    user_template: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("version", self.version)
        _validate_non_empty("system_prompt", self.system_prompt)
        _validate_non_empty("user_template", self.user_template)
        if "{context_summary}" not in self.user_template:
            raise ValueError("user_template must include {context_summary}")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    @property
    def template_key(self) -> str:
        return f"{self.identifier}:{self.version}"


@dataclass(frozen=True, slots=True)
class AIContext:
    """Deterministic context consumed by the AI reasoning prompt builder."""

    context_snapshot: Any
    translation_result: Any | None = None
    instructions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.context_snapshot is None:
            raise ValueError("context_snapshot must not be None")
        _validate_str_list("instructions", self.instructions)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(frozen=True, slots=True)
class AIRequest:
    """A deterministic request prepared for a provider."""

    identifier: str
    prompt_template_id: str
    prompt_template_version: str
    system_prompt: str
    user_prompt: str
    model_configuration: ModelConfiguration
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("prompt_template_id", self.prompt_template_id)
        _validate_non_empty("prompt_template_version", self.prompt_template_version)
        _validate_non_empty("system_prompt", self.system_prompt)
        _validate_non_empty("user_prompt", self.user_prompt)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(frozen=True, slots=True)
class AIResponse:
    """A provider response container."""

    request_identifier: str
    provider_type: ProviderType
    content: str
    model_name: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("request_identifier", self.request_identifier)
        _validate_non_empty("content", self.content)
        _validate_non_empty("model_name", self.model_name)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")
