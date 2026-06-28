from __future__ import annotations

from .models import ConfigurationItem, ConfigurationScope
from .registry import ConfigurationRegistry


def create_sample_configuration_registry() -> ConfigurationRegistry:
    """Create a small safe sample configuration registry."""

    return ConfigurationRegistry(
        items=[
            ConfigurationItem(
                key="environment",
                value="development",
                scope=ConfigurationScope.PLATFORM,
                source_id="sample",
                metadata={"notional": True},
            ),
            ConfigurationItem(
                key="enabled",
                value=True,
                scope=ConfigurationScope.SERVICE,
                source_id="sample",
                metadata={"service": "audit_service"},
            ),
        ]
    )
