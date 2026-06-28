from pathlib import Path

import pytest

from project_forge.profile_manager import (
    ForgeProfile,
    ProfileComponent,
    ProfileLoader,
    ProfileMetadata,
    ProfileRegistry,
    ProfileValidator,
    load_profiles,
)


def test_profiles_load_from_yaml() -> None:
    registry = load_profiles("config/profiles.example.yaml")

    assert [profile.profile_id for profile in registry.list_profiles()] == [
        "itx",
        "joint-exercise",
        "mwtc",
    ]
    mwtc = registry.get_profile("mwtc")
    assert mwtc is not None
    assert mwtc.display_name == "MWTC"
    assert mwtc.knowledge_base_path == "knowledge_base"
    assert "translation_engine" in mwtc.enabled_services
    assert "spotrep" in mwtc.enabled_plugins


def test_profile_registry_supports_lookup_by_id() -> None:
    profile = _valid_profile("custom")
    registry = ProfileRegistry()

    registry.register_profile(profile)

    assert registry.get_profile("custom") is profile
    assert registry.get_profile("missing") is None


def test_validator_checks_required_paths(tmp_path: Path) -> None:
    profile = _valid_profile("bad-path")

    with pytest.raises(FileNotFoundError):
        ProfileValidator(path_base=tmp_path).validate_profile(profile)


def test_validator_rejects_blank_required_fields() -> None:
    with pytest.raises(ValueError):
        ForgeProfile(
            metadata=ProfileMetadata(
                profile_id="blank",
                display_name="Blank",
                description="Missing workflow path.",
                exercise_type="test",
            ),
            enabled_services=["context_engine"],
            enabled_plugins=["spotrep"],
            knowledge_base_path="knowledge_base",
            template_path="config/product_plugins",
            translation_dictionary_path="config/translation_dictionaries.example.yaml",
            workflow_path="",
            default_scenario="scenario-forge-example",
        )


def test_validator_rejects_empty_services() -> None:
    profile = ForgeProfile(
        metadata=ProfileMetadata(
            profile_id="empty-services",
            display_name="Empty Services",
            description="No services enabled.",
            exercise_type="test",
        ),
        enabled_services=[],
        enabled_plugins=["spotrep"],
        knowledge_base_path="knowledge_base",
        template_path="config/product_plugins",
        translation_dictionary_path="config/translation_dictionaries.example.yaml",
        workflow_path="config/workflows.example.yaml",
        default_scenario="scenario-forge-example",
    )

    with pytest.raises(ValueError):
        ProfileValidator().validate_profile(profile)


def test_duplicate_profile_ids_are_rejected() -> None:
    profile = _valid_profile("duplicate")

    with pytest.raises(ValueError):
        ProfileRegistry(profiles=[profile, profile])


def test_duplicate_components_are_rejected() -> None:
    component = ProfileComponent(
        identifier="component",
        component_type="workflow",
    )
    profile = _valid_profile(
        "duplicate-components",
        components=[component, component],
    )

    with pytest.raises(ValueError):
        ProfileValidator().validate_profile(profile)


def test_loader_rejects_missing_config(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ProfileLoader(tmp_path / "missing.yaml").load()


def _valid_profile(
    profile_id: str,
    *,
    components: list[ProfileComponent] | None = None,
) -> ForgeProfile:
    return ForgeProfile(
        metadata=ProfileMetadata(
            profile_id=profile_id,
            display_name="Valid Profile",
            description="A valid test profile.",
            exercise_type="test",
        ),
        enabled_services=["context_engine", "translation_engine"],
        enabled_plugins=["spotrep"],
        knowledge_base_path="knowledge_base",
        template_path="config/product_plugins",
        translation_dictionary_path="config/translation_dictionaries.example.yaml",
        workflow_path="config/workflows.example.yaml",
        default_scenario="scenario-forge-example",
        components=components or [],
    )
