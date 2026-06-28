from __future__ import annotations

from .models import AIRequest, AIResponse, PromptTemplate


class PromptValidator:
    """Validates prompt templates, requests, and responses."""

    def validate_template(self, template: PromptTemplate) -> None:
        if "{context_summary}" not in template.user_template:
            raise ValueError("prompt template must include {context_summary}")

    def validate_request(self, request: AIRequest) -> None:
        if request.model_configuration.temperature != 0.0:
            raise ValueError("foundation AI requests must use deterministic temperature 0.0")
        if request.prompt_template_id not in request.identifier:
            raise ValueError("request identifier must include prompt template identifier")

    def validate_response(self, response: AIResponse) -> None:
        if not response.content.strip():
            raise ValueError("AI response content must not be empty")
