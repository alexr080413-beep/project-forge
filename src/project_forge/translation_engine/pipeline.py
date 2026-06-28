from __future__ import annotations

import re

from .models import (
    TranslationContext,
    TranslationDictionary,
    TranslationResult,
    TranslationRule,
    TranslationRuleType,
)
from .validator import TranslationValidator


class TranslationPipeline:
    """Runs deterministic translation rules in priority order."""

    def __init__(
        self,
        dictionary: TranslationDictionary,
        validator: TranslationValidator | None = None,
    ) -> None:
        self.dictionary = dictionary
        self.validator = validator or TranslationValidator()
        self.validator.validate_dictionary(dictionary)

    def translate(self, context: TranslationContext | str) -> TranslationResult:
        translation_context = (
            TranslationContext(text=context) if isinstance(context, str) else context
        )
        rules = self._rules_for_context(translation_context)
        translated = translation_context.text
        applied: list[str] = []
        for rule in rules:
            updated = _apply_rule(translated, rule)
            if updated != translated:
                translated = updated
                applied.append(rule.identifier)

        return TranslationResult(
            original_text=translation_context.text,
            translated_text=translated,
            applied_rule_identifiers=applied,
            metadata={
                "dictionary_identifier": self.dictionary.identifier,
                "profile_identifier": translation_context.profile_identifier,
            },
        )

    def _rules_for_context(self, context: TranslationContext) -> list[TranslationRule]:
        categories = set(context.categories)
        if context.profile_identifier:
            profile = self.dictionary.profile(context.profile_identifier)
            if profile is None:
                raise ValueError(f"translation profile not found: {context.profile_identifier}")
            categories.update(profile.categories)

        rules = self.dictionary.rules
        if categories:
            rules = [rule for rule in rules if rule.category in categories]
        return sorted(rules, key=lambda rule: (rule.priority, rule.category, rule.identifier))


def _apply_rule(text: str, rule: TranslationRule) -> str:
    if rule.rule_type is TranslationRuleType.REGEX:
        return re.sub(rule.source, rule.target, text, flags=_regex_flags(rule.flags))

    translated = _replace_literal(text, rule.source, rule.target)
    for alias in sorted(rule.aliases, key=lambda value: (-len(value), value)):
        translated = _replace_literal(translated, alias, rule.target)
    return translated


def _replace_literal(text: str, source: str, target: str) -> str:
    pattern = re.compile(rf"\b{re.escape(source)}\b")
    return pattern.sub(target, text)


def _regex_flags(flags: list[str]) -> int:
    value = 0
    for flag in flags:
        normalized = flag.strip().lower()
        if normalized == "ignorecase":
            value |= re.IGNORECASE
        elif normalized == "multiline":
            value |= re.MULTILINE
        elif normalized == "dotall":
            value |= re.DOTALL
    return value
