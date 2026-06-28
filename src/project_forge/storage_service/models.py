from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class StorageStatus(str, Enum):
    """Lifecycle states for storage operations."""

    PENDING = "pending"
    DRY_RUN = "dry_run"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PLACEHOLDER = "placeholder"


@dataclass(frozen=True, slots=True)
class StorageLocation:
    """A configured storage location owned by one provider."""

    location_id: str
    provider_identifier: str
    path: str
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("location_id", self.location_id)
        _validate_non_empty("provider_identifier", self.provider_identifier)
        _validate_non_empty("path", self.path)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class StorageItem:
    """A project artifact or folder discovered through storage."""

    item_id: str
    location: StorageLocation
    relative_path: str
    item_type: str = "file"
    size_bytes: int = 0
    modified_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("item_id", self.item_id)
        _validate_non_empty("relative_path", self.relative_path)
        _validate_non_empty("item_type", self.item_type)
        if self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class StorageRequest:
    """A request to read, write, list, or archive storage artifacts."""

    request_id: str
    operation: str
    location: StorageLocation
    relative_path: str = ""
    content: str = ""
    archive_location: StorageLocation | None = None
    dry_run: bool = True
    requested_by: str = "Project Forge"
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("request_id", self.request_id)
        _validate_non_empty("operation", self.operation)
        _validate_non_empty("requested_by", self.requested_by)
        if self.operation not in {"read_metadata", "write", "list", "archive"}:
            raise ValueError("operation must be read_metadata, write, list, or archive")
        if self.operation in {"read_metadata", "write", "archive"}:
            _validate_non_empty("relative_path", self.relative_path)
        if self.operation == "archive" and self.archive_location is None:
            raise ValueError("archive operations require archive_location")
        if not isinstance(self.dry_run, bool):
            raise ValueError("dry_run must be a boolean")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class StorageResult:
    """Result and audit metadata for one storage operation."""

    request_id: str
    provider_identifier: str
    status: StorageStatus
    operation: str
    message: str = ""
    item: StorageItem | None = None
    items: list[StorageItem] = field(default_factory=list)
    artifact_path: str = ""
    content: str = ""
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    audit_log: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("request_id", self.request_id)
        _validate_non_empty("provider_identifier", self.provider_identifier)
        _validate_non_empty("operation", self.operation)
        if not isinstance(self.items, list) or not all(
            isinstance(item, StorageItem) for item in self.items
        ):
            raise ValueError("items must be a list of StorageItem instances")
        if not isinstance(self.audit_log, list) or not all(
            isinstance(entry, str) for entry in self.audit_log
        ):
            raise ValueError("audit_log must be a list of strings")
        _validate_metadata(self.metadata)


ProviderHandler = Callable[["StorageProvider", StorageRequest], StorageResult]


@dataclass(slots=True)
class StorageProvider:
    """A registerable storage provider."""

    identifier: str
    name: str
    provider_type: str
    root_path: str
    placeholder: bool = False
    handler: ProviderHandler | None = field(default=None, repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("provider_type", self.provider_type)
        _validate_non_empty("root_path", self.root_path)
        if not isinstance(self.placeholder, bool):
            raise ValueError("placeholder must be a boolean")
        if self.handler is not None and not callable(self.handler):
            raise ValueError("handler must be callable")
        _validate_metadata(self.metadata)

    def handle(self, request: StorageRequest) -> StorageResult:
        handler = self.handler
        if handler is None and not self.placeholder and self.provider_type in {
            "local_file_system",
            "archive_folder",
            "output_folder",
            "knowledge_base_folder",
            "template_folder",
        }:
            handler = local_storage_handler
        handler = handler or dry_run_storage_handler
        return handler(self, request)


def local_storage_handler(
    provider: StorageProvider,
    request: StorageRequest,
) -> StorageResult:
    audit_log = _base_audit_log(provider, request)
    root = Path(request.location.path)

    if request.operation == "list":
        items = _list_local_items(request.location)
        audit_log.append(f"listed {len(items)} item(s) from {root}")
        return _result(
            provider,
            request,
            StorageStatus.SUCCEEDED,
            "storage items listed",
            items=items,
            audit_log=audit_log,
        )

    target_path = root / request.relative_path
    if request.operation == "read_metadata":
        item = _local_item_from_path(request.location, target_path, request.relative_path)
        audit_log.append(f"read metadata for {target_path}")
        return _result(
            provider,
            request,
            StorageStatus.SUCCEEDED,
            "storage metadata read",
            item=item,
            artifact_path=str(target_path),
            audit_log=audit_log,
        )

    if request.operation == "write":
        if request.dry_run:
            audit_log.append(f"dry-run write to {target_path}")
            return _result(
                provider,
                request,
                StorageStatus.DRY_RUN,
                "dry-run storage write succeeded",
                artifact_path=str(target_path),
                audit_log=audit_log,
            )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(request.content, encoding="utf-8")
        audit_log.append(f"wrote storage item to {target_path}")
        return _result(
            provider,
            request,
            StorageStatus.SUCCEEDED,
            "storage write succeeded",
            artifact_path=str(target_path),
            audit_log=audit_log,
        )

    if request.operation == "archive":
        archive_path = Path(request.archive_location.path) / request.relative_path
        if request.dry_run:
            audit_log.append(f"dry-run archive from {target_path} to {archive_path}")
            return _result(
                provider,
                request,
                StorageStatus.DRY_RUN,
                "dry-run storage archive succeeded",
                artifact_path=str(archive_path),
                audit_log=audit_log,
            )
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(target_path.read_text(encoding="utf-8"), encoding="utf-8")
        audit_log.append(f"archived storage item to {archive_path}")
        return _result(
            provider,
            request,
            StorageStatus.SUCCEEDED,
            "storage archive succeeded",
            artifact_path=str(archive_path),
            audit_log=audit_log,
        )

    return _result(
        provider,
        request,
        StorageStatus.FAILED,
        f"unsupported storage operation: {request.operation}",
        audit_log=audit_log,
    )


def dry_run_storage_handler(
    provider: StorageProvider,
    request: StorageRequest,
) -> StorageResult:
    audit_log = _base_audit_log(provider, request)
    if request.dry_run:
        audit_log.append(f"dry-run {request.operation} for {provider.provider_type}")
        return _result(
            provider,
            request,
            StorageStatus.DRY_RUN,
            "dry-run storage operation succeeded",
            audit_log=audit_log,
        )
    if provider.placeholder:
        audit_log.append(f"{provider.provider_type} provider is a placeholder")
        return _result(
            provider,
            request,
            StorageStatus.PLACEHOLDER,
            "provider is registered as a placeholder; no external action performed",
            audit_log=audit_log,
        )
    audit_log.append(f"no active handler for {provider.provider_type}")
    return _result(
        provider,
        request,
        StorageStatus.PLACEHOLDER,
        "provider has no active storage handler",
        audit_log=audit_log,
    )


def _list_local_items(location: StorageLocation) -> list[StorageItem]:
    root = Path(location.path)
    items: list[StorageItem] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            relative_path = path.relative_to(root).as_posix()
            items.append(_local_item_from_path(location, path, relative_path))
    return items


def _local_item_from_path(
    location: StorageLocation,
    path: Path,
    relative_path: str,
) -> StorageItem:
    stat = path.stat()
    return StorageItem(
        item_id=f"{location.location_id}:{relative_path}",
        location=location,
        relative_path=relative_path,
        item_type="file" if path.is_file() else "folder",
        size_bytes=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
        metadata={"absolute_path": str(path)},
    )


def _base_audit_log(
    provider: StorageProvider,
    request: StorageRequest,
) -> list[str]:
    return [
        f"request {request.request_id} started",
        f"provider {provider.identifier} selected",
        f"location {request.location.location_id} validated",
        f"operation={request.operation}",
        f"dry_run={request.dry_run}",
    ]


def _result(
    provider: StorageProvider,
    request: StorageRequest,
    status: StorageStatus,
    message: str,
    *,
    item: StorageItem | None = None,
    items: list[StorageItem] | None = None,
    artifact_path: str = "",
    audit_log: list[str],
) -> StorageResult:
    metadata = dict(request.metadata)
    metadata.update(
        {
            "dry_run": request.dry_run,
            "provider_type": provider.provider_type,
            "location_path": request.location.path,
        }
    )
    return StorageResult(
        request_id=request.request_id,
        provider_identifier=provider.identifier,
        status=status,
        operation=request.operation,
        message=message,
        item=item,
        items=items or [],
        artifact_path=artifact_path,
        audit_log=audit_log,
        metadata=metadata,
    )


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
