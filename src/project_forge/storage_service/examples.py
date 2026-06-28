from __future__ import annotations

from .models import StorageLocation, StorageRequest
from .registry import create_default_storage_registry


def create_sample_storage_registry():
    """Create a registry with default safe storage providers."""

    return create_default_storage_registry()


def create_sample_output_location() -> StorageLocation:
    """Create a local output folder location."""

    return StorageLocation(
        location_id="outputs",
        provider_identifier="output-folder",
        path="outputs",
        description="Local generated output folder.",
        metadata={"notional": True},
    )


def create_sample_storage_request() -> StorageRequest:
    """Create a dry-run write request for the local output folder."""

    return StorageRequest(
        request_id="storage-request-001",
        operation="write",
        location=create_sample_output_location(),
        relative_path="storage-service/sample.txt",
        content="Notional storage service sample.",
        dry_run=True,
        requested_by="EXCON",
        metadata={"notional": True},
    )
