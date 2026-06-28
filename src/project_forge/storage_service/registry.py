from __future__ import annotations

from dataclasses import dataclass, field

from .models import (
    StorageLocation,
    StorageProvider,
    StorageRequest,
    StorageResult,
    dry_run_storage_handler,
    local_storage_handler,
)
from .validator import StorageValidator


@dataclass(slots=True)
class StorageRegistry:
    """In-memory registry and operation surface for storage providers."""

    providers: list[StorageProvider] = field(default_factory=list)
    validator: StorageValidator = field(default_factory=StorageValidator)

    def __post_init__(self) -> None:
        self.validator.validate_providers(self.providers)
        self.providers.sort(key=lambda provider: provider.identifier)

    def register_provider(self, provider: StorageProvider) -> None:
        if self.get_provider(provider.identifier) is not None:
            raise ValueError(f"storage provider identifier already exists: {provider.identifier}")
        self.validator.validate_provider(provider)
        self.providers.append(provider)
        self.providers.sort(key=lambda item: item.identifier)

    def get_provider(self, identifier: str) -> StorageProvider | None:
        for provider in self.providers:
            if provider.identifier == identifier:
                return provider
        return None

    def list_providers(self) -> list[StorageProvider]:
        return list(self.providers)

    def execute(self, request: StorageRequest) -> StorageResult:
        provider = self.get_provider(request.location.provider_identifier)
        if provider is None:
            raise ValueError(
                f"storage provider not found: {request.location.provider_identifier}"
            )
        self.validator.validate_request(request, provider)
        result = provider.handle(request)
        self.validator.validate_result(result)
        return result

    def read_metadata(
        self,
        location: StorageLocation,
        relative_path: str,
        *,
        requested_by: str = "Project Forge",
    ) -> StorageResult:
        return self.execute(
            StorageRequest(
                request_id=f"{location.location_id}:{relative_path}:metadata",
                operation="read_metadata",
                location=location,
                relative_path=relative_path,
                requested_by=requested_by,
            )
        )

    def write(
        self,
        location: StorageLocation,
        relative_path: str,
        content: str,
        *,
        dry_run: bool = True,
        requested_by: str = "Project Forge",
    ) -> StorageResult:
        return self.execute(
            StorageRequest(
                request_id=f"{location.location_id}:{relative_path}:write",
                operation="write",
                location=location,
                relative_path=relative_path,
                content=content,
                dry_run=dry_run,
                requested_by=requested_by,
            )
        )

    def list_items(
        self,
        location: StorageLocation,
        *,
        requested_by: str = "Project Forge",
    ) -> StorageResult:
        return self.execute(
            StorageRequest(
                request_id=f"{location.location_id}:list",
                operation="list",
                location=location,
                dry_run=False,
                requested_by=requested_by,
            )
        )

    def archive_item(
        self,
        location: StorageLocation,
        relative_path: str,
        archive_location: StorageLocation,
        *,
        dry_run: bool = True,
        requested_by: str = "Project Forge",
    ) -> StorageResult:
        return self.execute(
            StorageRequest(
                request_id=f"{location.location_id}:{relative_path}:archive",
                operation="archive",
                location=location,
                relative_path=relative_path,
                archive_location=archive_location,
                dry_run=dry_run,
                requested_by=requested_by,
            )
        )


def create_default_storage_providers() -> list[StorageProvider]:
    """Create the default local and placeholder storage providers."""

    return [
        StorageProvider(
            identifier="archive-folder",
            name="Archive Folder",
            provider_type="archive_folder",
            root_path="outputs",
            handler=local_storage_handler,
        ),
        StorageProvider(
            identifier="azure-blob-placeholder",
            name="Azure Blob Placeholder",
            provider_type="azure_blob",
            root_path="azure://project-forge",
            placeholder=True,
            handler=dry_run_storage_handler,
        ),
        StorageProvider(
            identifier="knowledge-base-folder",
            name="Knowledge Base Folder",
            provider_type="knowledge_base_folder",
            root_path="knowledge_base",
            handler=local_storage_handler,
        ),
        StorageProvider(
            identifier="local-file-system",
            name="Local File System",
            provider_type="local_file_system",
            root_path=".",
            handler=local_storage_handler,
        ),
        StorageProvider(
            identifier="output-folder",
            name="Output Folder",
            provider_type="output_folder",
            root_path="outputs",
            handler=local_storage_handler,
        ),
        StorageProvider(
            identifier="s3-placeholder",
            name="S3 Placeholder",
            provider_type="s3",
            root_path="s3://project-forge",
            placeholder=True,
            handler=dry_run_storage_handler,
        ),
        StorageProvider(
            identifier="sharepoint-placeholder",
            name="SharePoint Placeholder",
            provider_type="sharepoint",
            root_path="sharepoint://project-forge",
            placeholder=True,
            handler=dry_run_storage_handler,
        ),
        StorageProvider(
            identifier="template-folder",
            name="Template Folder",
            provider_type="template_folder",
            root_path="assets",
            handler=local_storage_handler,
        ),
    ]


def create_default_storage_registry() -> StorageRegistry:
    """Create a registry with default local and placeholder providers."""

    return StorageRegistry(providers=create_default_storage_providers())
