"""Configuration Service foundation for Project Forge."""

from .examples import create_sample_configuration_registry
from .loader import (
    ConfigurationLoader,
    configuration_registry_from_mapping,
    load_configuration,
)
from .models import (
    ConfigurationChangeRecord,
    ConfigurationItem,
    ConfigurationProfile,
    ConfigurationResult,
    ConfigurationScope,
    ConfigurationSource,
)
from .registry import ConfigurationRegistry, configuration_registry_from_items
from .validator import ConfigurationValidator

__all__ = [
    "ConfigurationChangeRecord",
    "ConfigurationItem",
    "ConfigurationLoader",
    "ConfigurationProfile",
    "ConfigurationRegistry",
    "ConfigurationResult",
    "ConfigurationScope",
    "ConfigurationSource",
    "ConfigurationValidator",
    "configuration_registry_from_items",
    "configuration_registry_from_mapping",
    "create_sample_configuration_registry",
    "load_configuration",
]
