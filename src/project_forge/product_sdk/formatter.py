from __future__ import annotations

from string import Formatter
from typing import Any, Protocol

from .models import ProductOutput, ProductPlugin
from .validator import ProductValidator


class ProductFormatterInterface(Protocol):
    """Formatter interface for future product plugins."""

    def format(self, plugin: ProductPlugin, data: dict[str, Any]) -> ProductOutput:
        """Format validated data into a product output container."""


class ProductFormatter:
    """Basic deterministic formatter interface implementation."""

    def __init__(self, validator: ProductValidator | None = None) -> None:
        self.validator = validator or ProductValidator()

    def format(self, plugin: ProductPlugin, data: dict[str, Any]) -> ProductOutput:
        self.validator.validate_plugin(plugin)
        self.validator.validate_input(plugin, data)
        template = plugin.get_template(plugin.definition.template_identifier)
        if template is None:
            raise ValueError("plugin template is missing")
        allowed_fields = {
            field_name
            for _, field_name, _, _ in Formatter().parse(template.content)
        }
        values = {field: data.get(field, "") for field in allowed_fields if field}
        content = template.content.format(**values)
        output_format = (
            plugin.definition.output_formats[0]
            if plugin.definition.output_formats
            else "text"
        )
        return ProductOutput(
            plugin_identifier=plugin.identifier,
            product_identifier=plugin.definition.identifier,
            content=content,
            output_format=output_format,
            metadata={"template_key": template.template_key},
        )
