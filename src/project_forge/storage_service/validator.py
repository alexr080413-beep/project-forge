from __future__ import annotations

from pathlib import Path

from .models import (
    StorageLocation,
    StorageProvider,
    StorageRequest,
    StorageResult,
    StorageStatus,
)


class StorageValidator:
    """Validates storage providers, locations, requests, and results."""

    def validate_provider(self, provider: StorageProvider) -> None:
        if provider.placeholder:
            return
        if provider.provider_type not in {
            "local_file_system",
            "archive_folder",
            "output_folder",
            "knowledge_base_folder",
            "template_folder",
        }:
            raise ValueError("non-placeholder storage providers must be local provider types")
        self._validate_folder_path(provider.root_path)

    def validate_providers(self, providers: list[StorageProvider]) -> None:
        identifiers = [provider.identifier for provider in providers]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("storage provider identifiers must be unique")
        for provider in providers:
            self.validate_provider(provider)

    def validate_location(
        self,
        location: StorageLocation,
        provider: StorageProvider,
    ) -> None:
        if location.provider_identifier != provider.identifier:
            raise ValueError("storage location provider identifier must match provider")
        if provider.placeholder:
            return
        self._validate_folder_path(location.path)
        provider_root = Path(provider.root_path).resolve()
        location_root = Path(location.path).resolve()
        if provider_root != location_root and provider_root not in location_root.parents:
            raise ValueError("storage location must be within the provider root path")

    def validate_request(
        self,
        request: StorageRequest,
        provider: StorageProvider,
    ) -> None:
        self.validate_location(request.location, provider)
        if request.operation == "archive":
            if request.archive_location is None:
                raise ValueError("archive operations require archive_location")
            self._validate_folder_path(request.archive_location.path)
        if request.relative_path:
            self._validate_relative_path(request.relative_path)
            if request.operation in {"read_metadata", "archive"} and not provider.placeholder:
                item_path = Path(request.location.path) / request.relative_path
                if not item_path.exists() or not item_path.is_file():
                    raise FileNotFoundError(f"storage item does not exist: {item_path}")

    def validate_result(self, result: StorageResult) -> None:
        if result.status is StorageStatus.FAILED and not result.message.strip():
            raise ValueError("failed storage results must include a message")
        if not result.audit_log:
            raise ValueError("storage results must include audit metadata")

    def _validate_folder_path(self, value: str) -> None:
        path = Path(value)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"storage folder does not exist: {path}")

    def _validate_relative_path(self, value: str) -> None:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("storage relative_path must be relative and stay within location")
