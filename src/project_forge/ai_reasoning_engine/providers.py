from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .models import AIRequest, AIResponse, ProviderType
from .validator import PromptValidator


class AIProvider(Protocol):
    """Provider interface for future AI implementations."""

    provider_type: ProviderType

    def generate(self, request: AIRequest) -> AIResponse:
        """Generate an AI response for a request."""


@dataclass(slots=True)
class BaseProvider:
    """Base provider interface implementation."""

    provider_type: ProviderType
    validator: PromptValidator = field(default_factory=PromptValidator)

    def generate(self, request: AIRequest) -> AIResponse:
        self.validator.validate_request(request)
        raise NotImplementedError("live provider calls are not implemented")


class OpenAIProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__(provider_type=ProviderType.OPENAI)


class AzureOpenAIProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__(provider_type=ProviderType.AZURE_OPENAI)


class GovernmentHostedLLMProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__(provider_type=ProviderType.GOVERNMENT_HOSTED_LLM)


@dataclass(slots=True)
class OfflineStubProvider:
    """Offline provider for deterministic local tests."""

    content: str = "Offline stub response."
    provider_type: ProviderType = ProviderType.OFFLINE_STUB
    validator: PromptValidator = field(default_factory=PromptValidator)

    def generate(self, request: AIRequest) -> AIResponse:
        self.validator.validate_request(request)
        response = AIResponse(
            request_identifier=request.identifier,
            provider_type=self.provider_type,
            content=self.content,
            model_name=request.model_configuration.model_name,
            metadata={"offline": True},
        )
        self.validator.validate_response(response)
        return response
