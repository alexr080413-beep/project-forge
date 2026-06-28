from __future__ import annotations

from .models import IntegrationRequest
from .registry import create_default_integration_registry


def create_sample_integration_registry():
    """Create a registry with safe local example integration sources."""

    return create_default_integration_registry()


def create_sample_dry_run_request(source):
    """Create a dry-run request for an integration source."""

    return IntegrationRequest(
        request_id=f"{source.source_id}:dry-run",
        source=source,
        dry_run=True,
        requested_by="EXCON",
        metadata={"notional": True},
    )
