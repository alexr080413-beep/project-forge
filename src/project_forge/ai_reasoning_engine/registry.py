from __future__ import annotations

from dataclasses import dataclass, field

from .models import AIRequest, PromptTemplate
from .validator import PromptValidator


@dataclass(slots=True)
class TemplateRegistry:
    """Registry for versioned prompt templates."""

    templates: list[PromptTemplate] = field(default_factory=list)
    validator: PromptValidator = field(default_factory=PromptValidator)

    def __post_init__(self) -> None:
        self._validate_unique_templates()
        for template in self.templates:
            self.validator.validate_template(template)
        self.templates.sort(key=lambda template: template.template_key)

    def register_template(self, template: PromptTemplate) -> None:
        if self.get_template(template.identifier, template.version) is not None:
            raise ValueError(f"template already exists: {template.template_key}")
        self.validator.validate_template(template)
        self.templates.append(template)
        self.templates.sort(key=lambda item: item.template_key)

    def get_template(
        self,
        identifier: str,
        version: str | None = None,
    ) -> PromptTemplate | None:
        candidates = [
            template
            for template in self.templates
            if template.identifier == identifier
            and (version is None or template.version == version)
        ]
        if not candidates:
            return None
        return sorted(candidates, key=lambda template: template.version)[-1]

    def _validate_unique_templates(self) -> None:
        keys = [template.template_key for template in self.templates]
        if len(keys) != len(set(keys)):
            raise ValueError("prompt template keys must be unique")


@dataclass(slots=True)
class PromptRegistry:
    """Registry for deterministic AI requests."""

    requests: list[AIRequest] = field(default_factory=list)
    validator: PromptValidator = field(default_factory=PromptValidator)

    def __post_init__(self) -> None:
        self._validate_unique_requests()
        for request in self.requests:
            self.validator.validate_request(request)
        self.requests.sort(key=lambda request: request.identifier)

    def register_request(self, request: AIRequest) -> None:
        if self.get_request(request.identifier) is not None:
            raise ValueError(f"request already exists: {request.identifier}")
        self.validator.validate_request(request)
        self.requests.append(request)
        self.requests.sort(key=lambda item: item.identifier)

    def get_request(self, identifier: str) -> AIRequest | None:
        for request in self.requests:
            if request.identifier == identifier:
                return request
        return None

    def _validate_unique_requests(self) -> None:
        identifiers = [request.identifier for request in self.requests]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("AI request identifiers must be unique")
