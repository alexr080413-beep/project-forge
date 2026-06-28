from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class IntegrationSourceType(str, Enum):
    """Supported external and internal source types."""

    RSS = "rss"
    WEBSITE = "website"
    MANUAL_UPLOAD = "manual_upload"
    LOCAL_FILE = "local_file"
    EMAIL_PLACEHOLDER = "email_placeholder"
    SOCIAL_MEDIA_PLACEHOLDER = "social_media_placeholder"
    SHAREPOINT_PLACEHOLDER = "sharepoint_placeholder"
    API_PLACEHOLDER = "api_placeholder"


class IntegrationStatus(str, Enum):
    """Lifecycle states for integration collection results."""

    PENDING = "pending"
    DRY_RUN = "dry_run"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PLACEHOLDER = "placeholder"


@dataclass(frozen=True, slots=True)
class IntegrationSource:
    """A configured source that can be collected by an integration connector."""

    source_id: str
    name: str
    source_type: IntegrationSourceType
    location: str
    enabled: bool = True
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("source_id", self.source_id)
        _validate_non_empty("name", self.name)
        _validate_non_empty("location", self.location)
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class IntegrationRequest:
    """A request to collect or inspect one source."""

    request_id: str
    source: IntegrationSource
    dry_run: bool = True
    requested_by: str = "Project Forge"
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("request_id", self.request_id)
        _validate_non_empty("requested_by", self.requested_by)
        if not isinstance(self.dry_run, bool):
            raise ValueError("dry_run must be a boolean")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class IntegrationResult:
    """Result and audit metadata for one integration collection request."""

    request_id: str
    source_id: str
    connector_identifier: str
    status: IntegrationStatus
    message: str = ""
    collected_items: list[dict[str, Any]] = field(default_factory=list)
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    audit_log: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("request_id", self.request_id)
        _validate_non_empty("source_id", self.source_id)
        _validate_non_empty("connector_identifier", self.connector_identifier)
        if not isinstance(self.collected_items, list) or not all(
            isinstance(item, dict) for item in self.collected_items
        ):
            raise ValueError("collected_items must be a list of dictionaries")
        if not isinstance(self.audit_log, list) or not all(
            isinstance(entry, str) for entry in self.audit_log
        ):
            raise ValueError("audit_log must be a list of strings")
        _validate_metadata(self.metadata)


ConnectorHandler = Callable[["IntegrationConnector", IntegrationRequest], IntegrationResult]


@dataclass(slots=True)
class IntegrationConnector:
    """A registerable local connector for an integration source type."""

    identifier: str
    name: str
    source_type: IntegrationSourceType
    placeholder: bool = False
    handler: ConnectorHandler | None = field(default=None, repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        if not isinstance(self.placeholder, bool):
            raise ValueError("placeholder must be a boolean")
        if self.handler is not None and not callable(self.handler):
            raise ValueError("handler must be callable")
        _validate_metadata(self.metadata)

    def collect(self, request: IntegrationRequest) -> IntegrationResult:
        handler = self.handler or dry_run_connector_handler
        return handler(self, request)


def dry_run_connector_handler(
    connector: IntegrationConnector,
    request: IntegrationRequest,
) -> IntegrationResult:
    audit_log = _base_audit_log(connector, request)
    if not request.source.enabled:
        audit_log.append("source disabled")
        return _result(
            connector,
            request,
            IntegrationStatus.FAILED,
            "integration source is disabled",
            audit_log=audit_log,
        )
    if request.dry_run:
        audit_log.append(f"dry-run collection for {request.source.source_type.value}")
        return _result(
            connector,
            request,
            IntegrationStatus.DRY_RUN,
            "dry-run collection succeeded",
            audit_log=audit_log,
        )
    if connector.placeholder:
        audit_log.append(f"{connector.source_type.value} connector is a placeholder")
        return _result(
            connector,
            request,
            IntegrationStatus.PLACEHOLDER,
            "connector is registered as a placeholder; no external action performed",
            audit_log=audit_log,
        )
    audit_log.append("active collection is not implemented")
    return _result(
        connector,
        request,
        IntegrationStatus.PLACEHOLDER,
        "active collection is not implemented",
        audit_log=audit_log,
    )


def _base_audit_log(
    connector: IntegrationConnector,
    request: IntegrationRequest,
) -> list[str]:
    return [
        f"request {request.request_id} started",
        f"connector {connector.identifier} selected",
        f"source {request.source.source_id} validated",
        f"dry_run={request.dry_run}",
    ]


def _result(
    connector: IntegrationConnector,
    request: IntegrationRequest,
    status: IntegrationStatus,
    message: str,
    *,
    audit_log: list[str],
) -> IntegrationResult:
    metadata = dict(request.metadata)
    metadata.update(
        {
            "dry_run": request.dry_run,
            "source_type": request.source.source_type.value,
            "source_location": request.source.location,
        }
    )
    return IntegrationResult(
        request_id=request.request_id,
        source_id=request.source.source_id,
        connector_identifier=connector.identifier,
        status=status,
        message=message,
        audit_log=audit_log,
        metadata=metadata,
    )


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
