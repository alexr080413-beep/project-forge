from pathlib import Path

import pytest

from project_forge.product_sdk import (
    ProductDefinition,
    ProductFormatter,
    ProductMetadata,
    ProductPlugin,
    ProductPluginDiscovery,
    ProductPluginLoader,
    ProductRegistry,
    ProductTemplate,
    ProductValidator,
    discover_product_plugins,
    load_product_plugin,
)


def test_plugins_discovered_automatically() -> None:
    registry = discover_product_plugins("config/product_plugins")

    assert [plugin.identifier for plugin in registry.list_plugins()] == [
        "iir",
        "intelligence-summary",
        "news-article",
        "social-media",
        "spotrep",
    ]


def test_registry_functions_correctly() -> None:
    registry = ProductRegistry()
    plugin = ProductPlugin(
        metadata=ProductMetadata(
            identifier="custom-product",
            name="Custom Product",
            version="0.1.0",
            description="Custom test product.",
        ),
        definition=ProductDefinition(
            identifier="custom-product",
            product_type="custom",
            display_name="Custom Product",
            template_identifier="custom-template",
            output_formats=["text"],
        ),
        templates=[
            ProductTemplate(
                identifier="custom-template",
                version="0.1.0",
                content="{body}",
                required_fields=["body"],
            )
        ],
    )

    registry.register_plugin(plugin)

    assert registry.get_plugin("custom-product") is plugin
    assert registry.list_plugins() == [plugin]


def test_templates_load() -> None:
    plugin = load_product_plugin("config/product_plugins/intelligence_summary.yaml")
    template = plugin.get_template("intelligence-summary-template")

    assert template is not None
    assert template.required_fields == ["title", "summary", "key_judgments"]
    assert "{summary}" in template.content


def test_formatter_interface_formats_validated_payload() -> None:
    plugin = load_product_plugin("config/product_plugins/social_media.yaml")

    output = ProductFormatter().format(
        plugin,
        {"handle": "@notional", "post_text": "Exercise update."},
    )

    assert output.plugin_identifier == "social-media"
    assert output.output_format == "text"
    assert output.content == "@notional: Exercise update."


def test_validator_rejects_missing_required_template_fields() -> None:
    plugin = load_product_plugin("config/product_plugins/spotrep.yaml")

    with pytest.raises(ValueError):
        ProductValidator().validate_input(plugin, {"title": "SPOTREP"})


def test_validator_rejects_metadata_definition_identifier_mismatch() -> None:
    plugin = ProductPlugin(
        metadata=ProductMetadata(
            identifier="metadata-id",
            name="Mismatch",
            version="0.1.0",
            description="Mismatch test.",
        ),
        definition=ProductDefinition(
            identifier="definition-id",
            product_type="mismatch",
            display_name="Mismatch",
            template_identifier="template",
        ),
        templates=[
            ProductTemplate(
                identifier="template",
                version="0.1.0",
                content="{body}",
            )
        ],
    )

    with pytest.raises(ValueError):
        ProductValidator().validate_plugin(plugin)


def test_discovery_rejects_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ProductPluginDiscovery(tmp_path / "missing").discover()


def test_loader_rejects_missing_plugin(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ProductPluginLoader().load(tmp_path / "missing.yaml")
