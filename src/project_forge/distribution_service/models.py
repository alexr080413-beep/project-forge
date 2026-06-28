from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class DistributionStatus(str, Enum):
    """Lifecycle states for distribution requests and results."""

    PENDING = "pending"
    DRY_RUN = "dry_run"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PLACEHOLDER = "placeholder"


@dataclass(frozen=True, slots=True)
class DistributionTarget:
    """A validated destination for a distribution channel."""

    identifier: str
    target_type: str
    destination: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("target_type", self.target_type)
        _validate_non_empty("destination", self.destination)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class DistributionItem:
    """An approved product output ready for distribution handling."""

    item_id: str
    product_identifier: str
    product_type: str
    content: str
    output_format: str = "text"
    approved: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("item_id", self.item_id)
        _validate_non_empty("product_identifier", self.product_identifier)
        _validate_non_empty("product_type", self.product_type)
        _validate_non_empty("output_format", self.output_format)
        if self.content is None:
            raise ValueError("content must not be None")
        if not isinstance(self.approved, bool):
            raise ValueError("approved must be a boolean")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class DistributionRequest:
    """A request to distribute an approved product through one channel."""

    request_id: str
    item: DistributionItem
    channel_identifier: str
    target: DistributionTarget
    dry_run: bool = True
    requested_by: str = "Project Forge"
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("request_id", self.request_id)
        _validate_non_empty("channel_identifier", self.channel_identifier)
        _validate_non_empty("requested_by", self.requested_by)
        if not isinstance(self.dry_run, bool):
            raise ValueError("dry_run must be a boolean")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class DistributionResult:
    """Result and audit metadata for one distribution request."""

    request_id: str
    channel_identifier: str
    status: DistributionStatus
    target_identifier: str
    message: str = ""
    artifact_path: str = ""
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    audit_log: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("request_id", self.request_id)
        _validate_non_empty("channel_identifier", self.channel_identifier)
        _validate_non_empty("target_identifier", self.target_identifier)
        if not isinstance(self.audit_log, list) or not all(
            isinstance(entry, str) for entry in self.audit_log
        ):
            raise ValueError("audit_log must be a list of strings")
        _validate_metadata(self.metadata)


ChannelHandler = Callable[["DistributionChannel", DistributionRequest], DistributionResult]


@dataclass(slots=True)
class DistributionChannel:
    """A registerable local distribution channel."""

    identifier: str
    name: str
    channel_type: str
    supported_formats: list[str] = field(default_factory=list)
    placeholder: bool = False
    handler: ChannelHandler | None = field(default=None, repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("channel_type", self.channel_type)
        _validate_str_list("supported_formats", self.supported_formats)
        if not isinstance(self.placeholder, bool):
            raise ValueError("placeholder must be a boolean")
        if self.handler is not None and not callable(self.handler):
            raise ValueError("handler must be callable")
        _validate_metadata(self.metadata)

    def distribute(self, request: DistributionRequest) -> DistributionResult:
        handler = self.handler or _default_channel_handler
        return handler(self, request)


def local_file_handler(
    channel: DistributionChannel,
    request: DistributionRequest,
) -> DistributionResult:
    audit_log = _base_audit_log(channel, request)
    output_path = Path(request.target.destination)
    if request.dry_run:
        audit_log.append(f"dry-run local file export to {output_path}")
        return _result(
            channel,
            request,
            DistributionStatus.DRY_RUN,
            "dry-run distribution succeeded",
            artifact_path=str(output_path),
            audit_log=audit_log,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(request.item.content, encoding="utf-8")
    audit_log.append(f"wrote local file export to {output_path}")
    return _result(
        channel,
        request,
        DistributionStatus.SUCCEEDED,
        "local file export succeeded",
        artifact_path=str(output_path),
        audit_log=audit_log,
    )


def archive_folder_handler(
    channel: DistributionChannel,
    request: DistributionRequest,
) -> DistributionResult:
    audit_log = _base_audit_log(channel, request)
    archive_dir = Path(request.target.destination)
    artifact_path = archive_dir / f"{request.item.product_identifier}.{request.item.output_format}"
    if request.dry_run:
        audit_log.append(f"dry-run archive copy to {artifact_path}")
        return _result(
            channel,
            request,
            DistributionStatus.DRY_RUN,
            "dry-run distribution succeeded",
            artifact_path=str(artifact_path),
            audit_log=audit_log,
        )

    archive_dir.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(request.item.content, encoding="utf-8")
    audit_log.append(f"wrote archive artifact to {artifact_path}")
    return _result(
        channel,
        request,
        DistributionStatus.SUCCEEDED,
        "archive folder distribution succeeded",
        artifact_path=str(artifact_path),
        audit_log=audit_log,
    )


def dry_run_only_handler(
    channel: DistributionChannel,
    request: DistributionRequest,
) -> DistributionResult:
    audit_log = _base_audit_log(channel, request)
    if request.dry_run:
        audit_log.append(f"dry-run {channel.channel_type} distribution")
        return _result(
            channel,
            request,
            DistributionStatus.DRY_RUN,
            "dry-run distribution succeeded",
            audit_log=audit_log,
        )
    audit_log.append(f"{channel.channel_type} is a placeholder channel")
    return _result(
        channel,
        request,
        DistributionStatus.PLACEHOLDER,
        "channel is registered as a placeholder; no external action performed",
        audit_log=audit_log,
    )


def _default_channel_handler(
    channel: DistributionChannel,
    request: DistributionRequest,
) -> DistributionResult:
    audit_log = _base_audit_log(channel, request)
    if request.dry_run:
        audit_log.append(f"dry-run {channel.channel_type} distribution")
        return _result(
            channel,
            request,
            DistributionStatus.DRY_RUN,
            "dry-run distribution succeeded",
            audit_log=audit_log,
        )
    audit_log.append(f"no handler implemented for {channel.channel_type}")
    return _result(
        channel,
        request,
        DistributionStatus.PLACEHOLDER,
        "channel has no active distribution handler",
        audit_log=audit_log,
    )


def _base_audit_log(
    channel: DistributionChannel,
    request: DistributionRequest,
) -> list[str]:
    return [
        f"request {request.request_id} started",
        f"channel {channel.identifier} selected",
        f"target {request.target.identifier} validated",
        f"dry_run={request.dry_run}",
    ]


def _result(
    channel: DistributionChannel,
    request: DistributionRequest,
    status: DistributionStatus,
    message: str,
    *,
    artifact_path: str = "",
    audit_log: list[str],
) -> DistributionResult:
    metadata = dict(request.metadata)
    metadata.update(
        {
            "channel_type": channel.channel_type,
            "dry_run": request.dry_run,
            "product_identifier": request.item.product_identifier,
        }
    )
    return DistributionResult(
        request_id=request.request_id,
        channel_identifier=channel.identifier,
        status=status,
        target_identifier=request.target.identifier,
        message=message,
        artifact_path=artifact_path,
        audit_log=audit_log,
        metadata=metadata,
    )


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError(f"{name} must be a list of non-empty strings")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
