from pathlib import Path

import pytest

from project_forge.translation_engine import (
    TranslationContext,
    TranslationDictionary,
    TranslationDictionaryLoader,
    TranslationPipeline,
    TranslationProfile,
    TranslationRegistry,
    TranslationRule,
    TranslationRuleType,
    TranslationValidator,
    load_translation_dictionary,
)


def test_dictionary_loads_from_yaml() -> None:
    registry = load_translation_dictionary("config/translation_dictionaries.example.yaml")
    dictionary = registry.get_dictionary("forge-example-translation")

    assert dictionary is not None
    assert dictionary.name == "Forge Example Translation Dictionary"
    assert dictionary.profile("exercise-products") is not None
    assert len(dictionary.rules) == 10


def test_translation_pipeline_is_deterministic() -> None:
    dictionary = load_translation_dictionary(
        "config/translation_dictionaries.example.yaml"
    ).get_dictionary("forge-example-translation")
    pipeline = TranslationPipeline(dictionary)
    context = TranslationContext(
        text=(
            "Host Nation leaders met JTF HQ at the Capital Operations Center "
            "near the northern border region."
        ),
        profile_identifier="exercise-products",
    )

    first = pipeline.translate(context)
    second = pipeline.translate(context)

    assert first.translated_text == second.translated_text
    assert first.applied_rule_identifiers == second.applied_rule_identifiers
    assert "Asteria leaders" in first.translated_text
    assert "CRG Headquarters" in first.translated_text
    assert "Asteria Coordination Center" in first.translated_text
    assert "northern training corridor" in first.translated_text


def test_pipeline_supports_category_filtering() -> None:
    dictionary = load_translation_dictionary(
        "config/translation_dictionaries.example.yaml"
    ).get_dictionary("forge-example-translation")
    pipeline = TranslationPipeline(dictionary)
    result = pipeline.translate(
        TranslationContext(
            text="Host Nation and Joint Task Force Headquarters.",
            categories=["countries"],
        )
    )

    assert result.translated_text == "Asteria and Joint Task Force Headquarters."
    assert result.applied_rule_identifiers == ["country-host-nation"]


def test_aliases_are_translated() -> None:
    dictionary = load_translation_dictionary(
        "config/translation_dictionaries.example.yaml"
    ).get_dictionary("forge-example-translation")
    result = TranslationPipeline(dictionary).translate("EXCON briefed JTF HQ.")

    assert result.translated_text == "Scenario Control Cell briefed CRG Headquarters."
    assert result.applied_rule_identifiers == ["unit-jtf-hq", "agency-excon"]


def test_rules_validate_successfully() -> None:
    dictionary = TranslationDictionary(
        identifier="test-dictionary",
        name="Test Dictionary",
        rules=[
            TranslationRule(
                identifier="country",
                category="countries",
                source="Country A",
                target="Country B",
            ),
            TranslationRule(
                identifier="regex",
                category="units",
                source="Unit ([0-9]+)",
                target="Unit-\\1",
                rule_type=TranslationRuleType.REGEX,
            ),
        ],
        profiles=[
            TranslationProfile(
                identifier="profile",
                name="Profile",
                categories=["countries", "units"],
            )
        ],
    )

    TranslationValidator().validate_dictionary(dictionary)


def test_validator_rejects_invalid_regex() -> None:
    dictionary = TranslationDictionary(
        identifier="bad-regex",
        name="Bad Regex",
        rules=[
            TranslationRule(
                identifier="bad",
                category="units",
                source="[",
                target="x",
                rule_type=TranslationRuleType.REGEX,
            )
        ],
    )

    with pytest.raises(ValueError):
        TranslationValidator().validate_dictionary(dictionary)


def test_validator_rejects_unknown_profile_category() -> None:
    dictionary = TranslationDictionary(
        identifier="bad-profile",
        name="Bad Profile",
        rules=[
            TranslationRule(
                identifier="country",
                category="countries",
                source="Country A",
                target="Country B",
            )
        ],
        profiles=[
            TranslationProfile(
                identifier="profile",
                name="Profile",
                categories=["unknown"],
            )
        ],
    )

    with pytest.raises(ValueError):
        TranslationValidator().validate_dictionary(dictionary)


def test_registry_supports_modular_dictionary_registration() -> None:
    registry = TranslationRegistry()
    dictionary = TranslationDictionary(
        identifier="custom",
        name="Custom",
        rules=[
            TranslationRule(
                identifier="agency",
                category="government_agencies",
                source="Agency A",
                target="Agency B",
            )
        ],
    )

    registry.register_dictionary(dictionary)

    assert registry.get_dictionary("custom") is dictionary


def test_loader_rejects_missing_dictionary(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        TranslationDictionaryLoader(tmp_path / "missing.yaml").load()
