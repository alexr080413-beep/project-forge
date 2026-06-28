"""Integration Service foundation for Project Forge."""

from .examples import create_sample_dry_run_request, create_sample_integration_registry
from .loader import (
    IntegrationSourceLoader,
    integration_registry_from_mapping,
    load_integration_sources,
)
from .models import (
    IntegrationConnector,
    IntegrationRequest,
    IntegrationResult,
    IntegrationSource,
    IntegrationSourceType,
    IntegrationStatus,
)
from .registry import (
    IntegrationRegistry,
    create_default_integration_connectors,
    create_default_integration_registry,
)
from .validator import IntegrationValidator

__all__ = [
    "IntegrationConnector",
    "IntegrationRegistry",
    "IntegrationRequest",
    "IntegrationResult",
    "IntegrationSource",
    "IntegrationSourceLoader",
    "IntegrationSourceType",
    "IntegrationStatus",
    "IntegrationValidator",
    "create_default_integration_connectors",
    "create_default_integration_registry",
    "create_sample_dry_run_request",
    "create_sample_integration_registry",
    "integration_registry_from_mapping",
    "load_integration_sources",
]
