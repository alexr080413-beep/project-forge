"""Product SDK foundation for Project Forge."""

from .discovery import ProductPluginDiscovery, discover_product_plugins
from .formatter import ProductFormatter
from .loader import ProductPluginLoader, load_product_plugin
from .models import (
    ProductDefinition,
    ProductMetadata,
    ProductOutput,
    ProductPlugin,
    ProductTemplate,
)
from .registry import ProductRegistry
from .validator import ProductValidator

__all__ = [
    "ProductDefinition",
    "ProductFormatter",
    "ProductMetadata",
    "ProductOutput",
    "ProductPlugin",
    "ProductPluginDiscovery",
    "ProductPluginLoader",
    "ProductRegistry",
    "ProductTemplate",
    "ProductValidator",
    "discover_product_plugins",
    "load_product_plugin",
]
