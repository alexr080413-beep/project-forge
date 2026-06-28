from __future__ import annotations

import re

from .models import TranslationDictionary, TranslationRuleType


class TranslationValidator:
    """Validates dictionaries and rules before pipeline use."""

    def validate_dictionary(self, dictionary: TranslationDictionary) -> None:
        rule_identifiers = [rule.identifier for rule in dictionary.rules]
        if len(rule_identifiers) != len(set(rule_identifiers)):
            raise ValueError("translation rule identifiers must be unique")

        profile_identifiers = [profile.identifier for profile in dictionary.profiles]
        if len(profile_identifiers) != len(set(profile_identifiers)):
            raise ValueError("translation profile identifiers must be unique")

        valid_categories = {rule.category for rule in dictionary.rules}
        for profile in dictionary.profiles:
            unknown = sorted(set(profile.categories) - valid_categories)
            if unknown:
                raise ValueError(
                    f"profile references unknown translation categories: {unknown}"
                )

        for rule in dictionary.rules:
            self.validate_rule(rule)

    def validate_rule(self, rule: object) -> None:
        rule_type = getattr(rule, "rule_type", None)
        if rule_type is TranslationRuleType.REGEX:
            flags = _regex_flags(getattr(rule, "flags", []))
            try:
                re.compile(getattr(rule, "source"), flags)
            except re.error as error:
                raise ValueError(f"invalid regex rule {getattr(rule, 'identifier')}") from error


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
        else:
            raise ValueError(f"unsupported regex flag: {flag}")
    return value
