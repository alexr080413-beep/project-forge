from __future__ import annotations

from dataclasses import dataclass, field

from .models import ProductPlugin
from .validator import ProductValidator


@dataclass(slots=True)
class ProductRegistry:
    """In-memory registry for validated product plugins."""

    plugins: list[ProductPlugin] = field(default_factory=list)
    validator: ProductValidator = field(default_factory=ProductValidator)

    def __post_init__(self) -> None:
        self._validate_unique_plugins()
        for plugin in self.plugins:
            self.validator.validate_plugin(plugin)
        self.plugins.sort(key=lambda plugin: plugin.identifier)

    def register_plugin(self, plugin: ProductPlugin) -> None:
        if self.get_plugin(plugin.identifier) is not None:
            raise ValueError(f"plugin identifier already exists: {plugin.identifier}")
        self.validator.validate_plugin(plugin)
        self.plugins.append(plugin)
        self.plugins.sort(key=lambda item: item.identifier)

    def get_plugin(self, identifier: str) -> ProductPlugin | None:
        for plugin in self.plugins:
            if plugin.identifier == identifier:
                return plugin
        return None

    def list_plugins(self) -> list[ProductPlugin]:
        return list(self.plugins)

    def _validate_unique_plugins(self) -> None:
        identifiers = [plugin.identifier for plugin in self.plugins]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("product plugin identifiers must be unique")
