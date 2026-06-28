import json
from pathlib import Path

import pytest

from project_forge.configuration_service import (
    ConfigurationItem,
    ConfigurationLoader,
    ConfigurationRegistry,
    ConfigurationScope,
    ConfigurationSource,
    ConfigurationValidator,
    configuration_registry_from_mapping,
    create_sample_configuration_registry,
    load_configuration,
)


def item(
    key: str = "environment",
    *,
    value="development",
    scope: ConfigurationScope = ConfigurationScope.PLATFORM,
    source_id: str = "test",
    required: bool = False,
):
    return ConfigurationItem(
        key=key,
        value=value,
        scope=scope,
        source_id=source_id,
        required=required,
    )


def write_config(path: Path, items: list[dict], profiles: list[dict] | None = None) -> None:
    path.write_text(
        json.dumps({"items": items, "profiles": profiles or []}),
        encoding="utf-8",
    )


def test_configuration_files_load_successfully() -> None:
    registry = load_configuration(
        [
            ConfigurationSource(
                source_id="example",
                path="config/configuration.example.yaml",
            )
        ]
    )

    assert registry.get_value(ConfigurationScope.PLATFORM, "environment") == "development"
    assert registry.get_value(ConfigurationScope.PROFILE, "default_profile") == "mwtc"


def test_json_configuration_loads_successfully(tmp_path: Path) -> None:
    config = tmp_path / "config.json"
    write_config(
        config,
        [
            {
                "scope": "service",
                "key": "review_queue.enabled",
                "value": True,
                "required": True,
            }
        ],
    )

    registry = load_configuration(
        [ConfigurationSource(source_id="json", path=str(config))]
    )

    assert registry.get_value(ConfigurationScope.SERVICE, "review_queue.enabled") is True


def test_overrides_apply_in_deterministic_order(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    override = tmp_path / "override.yaml"
    write_config(
        base,
        [{"scope": "platform", "key": "environment", "value": "development"}],
    )
    write_config(
        override,
        [{"scope": "platform", "key": "environment", "value": "exercise"}],
    )

    loader = ConfigurationLoader(
        [
            ConfigurationSource("override", str(override), precedence=20),
            ConfigurationSource("base", str(base), precedence=10),
        ]
    )
    result = loader.load()
    registry = loader.load_registry()

    assert registry.get_value(ConfigurationScope.PLATFORM, "environment") == "exercise"
    assert result.changes[0].previous_value == "development"
    assert result.changes[0].new_value == "exercise"


def test_required_fields_validate() -> None:
    with pytest.raises(ValueError):
        ConfigurationValidator().validate_item(
            item("default_profile", value="", scope=ConfigurationScope.PROFILE, required=True)
        )


def test_default_values_are_applied() -> None:
    registry = configuration_registry_from_mapping(
        {
            "items": [
                {
                    "scope": "workflow",
                    "key": "path",
                    "default": "config/workflows.example.yaml",
                    "required": True,
                }
            ]
        }
    )

    assert registry.get_value(ConfigurationScope.WORKFLOW, "path") == (
        "config/workflows.example.yaml"
    )


def test_environment_variable_placeholder_support(monkeypatch) -> None:
    monkeypatch.setenv("FORGE_PROFILE", "joint")
    registry = configuration_registry_from_mapping(
        {
            "items": [
                {
                    "scope": "profile",
                    "key": "active",
                    "value": "${FORGE_PROFILE:-mwtc}",
                    "required": True,
                }
            ]
        }
    )

    assert registry.get_value(ConfigurationScope.PROFILE, "active") == "joint"


def test_environment_variable_placeholder_fallback() -> None:
    registry = configuration_registry_from_mapping(
        {
            "items": [
                {
                    "scope": "profile",
                    "key": "active",
                    "value": "${FORGE_MISSING_PROFILE:-mwtc}",
                    "required": True,
                }
            ]
        }
    )

    assert registry.get_value(ConfigurationScope.PROFILE, "active") == "mwtc"


def test_registry_supports_lookup_by_scope_and_key() -> None:
    registry = ConfigurationRegistry(items=[item()])

    assert registry.get_item(ConfigurationScope.PLATFORM, "environment") is not None
    assert registry.list_by_scope(ConfigurationScope.PLATFORM)[0].key == "environment"


def test_registry_rejects_duplicate_scope_key_pairs() -> None:
    config_item = item()

    with pytest.raises(ValueError):
        ConfigurationRegistry(items=[config_item, config_item])


def test_all_configuration_scopes_are_supported() -> None:
    assert {scope.value for scope in ConfigurationScope} == {
        "platform",
        "service",
        "profile",
        "workflow",
        "plugin",
        "environment",
        "user",
    }


def test_configuration_profiles_resolve_items() -> None:
    registry = configuration_registry_from_mapping(
        {
            "items": [
                {"scope": "platform", "key": "environment", "value": "dev"}
            ],
            "profiles": [
                {
                    "profile_id": "dev",
                    "display_name": "Dev",
                    "items": [{"scope": "platform", "key": "environment"}],
                }
            ],
        }
    )

    profile = registry.get_profile("dev")

    assert profile is not None
    assert profile.items[0].value == "dev"


def test_missing_configuration_file_fails(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_configuration(
            [ConfigurationSource(source_id="missing", path=str(tmp_path / "missing.yaml"))]
        )


def test_sample_configuration_registry() -> None:
    registry = create_sample_configuration_registry()

    assert registry.get_value(ConfigurationScope.SERVICE, "enabled") is True
