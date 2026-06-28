from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .loader import ProductPluginLoader
from .registry import ProductRegistry


@dataclass(slots=True)
class ProductPluginDiscovery:
    """Discovers product plugins from local manifest files."""

    plugin_directory: str | Path = "config/product_plugins"
    loader: ProductPluginLoader = field(default_factory=ProductPluginLoader)

    def discover(self) -> ProductRegistry:
        root = Path(self.plugin_directory)
        if not root.exists():
            raise FileNotFoundError(f"Product plugin directory does not exist: {root}")
        if not root.is_dir():
            raise NotADirectoryError(f"Product plugin path is not a directory: {root}")

        plugins = [
            self.loader.load(path)
            for path in sorted(root.glob("*.yaml"), key=lambda item: item.name)
        ]
        return ProductRegistry(plugins=plugins)


def discover_product_plugins(
    plugin_directory: str | Path = "config/product_plugins",
) -> ProductRegistry:
    """Discover product plugins from a local directory."""

    return ProductPluginDiscovery(plugin_directory=plugin_directory).discover()
