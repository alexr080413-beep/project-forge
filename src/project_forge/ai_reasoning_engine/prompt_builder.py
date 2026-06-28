from __future__ import annotations

from typing import Any

from .models import AIContext, AIRequest, ModelConfiguration, PromptTemplate
from .validator import PromptValidator


class PromptBuilder:
    """Builds deterministic prompts from Context Engine snapshots."""

    def __init__(self, validator: PromptValidator | None = None) -> None:
        self.validator = validator or PromptValidator()

    def build_request(
        self,
        *,
        template: PromptTemplate,
        ai_context: AIContext,
        model_configuration: ModelConfiguration,
    ) -> AIRequest:
        self.validator.validate_template(template)
        context_summary = _context_summary(ai_context)
        instructions = _instructions_summary(ai_context.instructions)
        user_prompt = template.user_template.format(
            context_summary=context_summary,
            instructions=instructions,
        )
        request = AIRequest(
            identifier=_request_identifier(template, ai_context),
            prompt_template_id=template.identifier,
            prompt_template_version=template.version,
            system_prompt=template.system_prompt,
            user_prompt=user_prompt,
            model_configuration=model_configuration,
            metadata={
                "context_identifier": str(getattr(ai_context.context_snapshot, "identifier", "")),
                "context_type": str(getattr(ai_context.context_snapshot, "context_type", "")),
                "template_key": template.template_key,
            },
        )
        self.validator.validate_request(request)
        return request


def _request_identifier(template: PromptTemplate, ai_context: AIContext) -> str:
    snapshot = ai_context.context_snapshot
    snapshot_identifier = str(getattr(snapshot, "identifier", "context"))
    return f"{template.identifier}:{template.version}:{snapshot_identifier}"


def _context_summary(ai_context: AIContext) -> str:
    snapshot = ai_context.context_snapshot
    context = getattr(snapshot, "exercise_context", None)
    lines = [
        f"Context Snapshot: {getattr(snapshot, 'identifier', '')}",
        f"Context Type: {getattr(snapshot, 'context_type', '')}",
    ]
    if context is None:
        return "\n".join(lines)

    scenario = getattr(context, "scenario", None)
    exercise_state = getattr(context, "exercise_state", None)
    lines.extend(
        [
            f"Exercise: {getattr(exercise_state, 'exercise_name', '')}",
            f"Scenario: {getattr(scenario, 'scenario_name', '')}",
            f"Training Objectives: {', '.join(getattr(context, 'training_objectives', []))}",
            f"Entities: {_identifiers(getattr(context, 'entities', []))}",
            f"Events: {_identifiers(getattr(context, 'events', []))}",
            f"Knowledge Documents: {_document_identifiers(context)}",
            f"Decision Results: {_decision_identifiers(context)}",
            f"References: {_reference_identifiers(context)}",
        ]
    )

    translation_result = ai_context.translation_result
    if translation_result is not None:
        lines.extend(
            [
                "Translation Original: "
                f"{getattr(translation_result, 'original_text', '')}",
                "Translation Applied Rules: "
                f"{', '.join(getattr(translation_result, 'applied_rule_identifiers', []))}",
                "Translation Text: "
                f"{getattr(translation_result, 'translated_text', '')}",
            ]
        )

    return "\n".join(lines)


def _instructions_summary(instructions: list[str]) -> str:
    if not instructions:
        return "No additional instructions."
    return "\n".join(f"- {instruction}" for instruction in sorted(instructions))


def _identifiers(items: list[Any]) -> str:
    identifiers = [
        str(getattr(item, "identifier", ""))
        for item in items
        if str(getattr(item, "identifier", "")).strip()
    ]
    return ", ".join(sorted(identifiers))


def _document_identifiers(context: Any) -> str:
    documents = getattr(context, "knowledge_documents", [])
    identifiers = [str(getattr(document, "relative_path", "")) for document in documents]
    return ", ".join(sorted(identifier for identifier in identifiers if identifier))


def _decision_identifiers(context: Any) -> str:
    results = getattr(context, "decision_results", [])
    identifiers = [
        f"{getattr(result, 'decision_identifier', '')}:"
        f"{getattr(getattr(result, 'outcome', ''), 'value', '')}"
        for result in results
    ]
    return ", ".join(sorted(identifier for identifier in identifiers if identifier))


def _reference_identifiers(context: Any) -> str:
    references = getattr(context, "references", [])
    identifiers = [
        f"{reference.reference_type}:{reference.identifier}"
        for reference in references
        if getattr(reference, "identifier", "")
    ]
    return ", ".join(sorted(identifiers))
