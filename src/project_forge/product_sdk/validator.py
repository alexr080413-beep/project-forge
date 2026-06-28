from __future__ import annotations

from .models import ProductPlugin


class ProductValidator:
    """Validator interface for product plugins and product input payloads."""

    def validate_plugin(self, plugin: ProductPlugin) -> None:
        if plugin.metadata.identifier != plugin.definition.identifier:
            raise ValueError("metadata and definition identifiers must match")
        if len(plugin.templates) != len({template.template_key for template in plugin.templates}):
            raise ValueError("template keys must be unique")
        template = plugin.get_template(plugin.definition.template_identifier)
        if template is None:
            raise ValueError("definition template_identifier must resolve")
        for output_format in plugin.definition.output_formats:
            if not output_format.strip():
                raise ValueError("output formats must not contain blank values")

    def validate_input(self, plugin: ProductPlugin, data: dict[str, object]) -> None:
        template = plugin.get_template(plugin.definition.template_identifier)
        if template is None:
            raise ValueError("plugin template is missing")
        missing = sorted(set(template.required_fields) - set(data))
        if missing:
            raise ValueError(f"missing required product fields: {missing}")
