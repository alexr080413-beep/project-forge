"""AI Reasoning Engine foundation for Project Forge.

This package builds deterministic prompts and provider interfaces only. It does
not perform live API calls.
"""

from .models import (
    AIContext,
    AIRequest,
    AIResponse,
    ModelConfiguration,
    PromptTemplate,
)
from .prompt_builder import PromptBuilder
from .providers import (
    AIProvider,
    AzureOpenAIProvider,
    GovernmentHostedLLMProvider,
    OfflineStubProvider,
    OpenAIProvider,
)
from .registry import PromptRegistry, TemplateRegistry
from .validator import PromptValidator

__all__ = [
    "AIContext",
    "AIProvider",
    "AIRequest",
    "AIResponse",
    "AzureOpenAIProvider",
    "GovernmentHostedLLMProvider",
    "ModelConfiguration",
    "OfflineStubProvider",
    "OpenAIProvider",
    "PromptBuilder",
    "PromptRegistry",
    "PromptTemplate",
    "PromptValidator",
    "TemplateRegistry",
]
