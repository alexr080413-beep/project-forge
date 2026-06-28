from __future__ import annotations

from dataclasses import dataclass, field

from .models import (
    DistributionChannel,
    DistributionRequest,
    DistributionResult,
    archive_folder_handler,
    dry_run_only_handler,
    local_file_handler,
)
from .validator import DistributionValidator


@dataclass(slots=True)
class DistributionRegistry:
    """In-memory registry and execution surface for distribution channels."""

    channels: list[DistributionChannel] = field(default_factory=list)
    validator: DistributionValidator = field(default_factory=DistributionValidator)

    def __post_init__(self) -> None:
        self.validator.validate_channels(self.channels)
        self.channels.sort(key=lambda channel: channel.identifier)

    def register_channel(self, channel: DistributionChannel) -> None:
        if self.get_channel(channel.identifier) is not None:
            raise ValueError(
                f"distribution channel identifier already exists: {channel.identifier}"
            )
        self.validator.validate_channel(channel)
        self.channels.append(channel)
        self.channels.sort(key=lambda item: item.identifier)

    def get_channel(self, identifier: str) -> DistributionChannel | None:
        for channel in self.channels:
            if channel.identifier == identifier:
                return channel
        return None

    def list_channels(self) -> list[DistributionChannel]:
        return list(self.channels)

    def distribute(self, request: DistributionRequest) -> DistributionResult:
        channel = self.get_channel(request.channel_identifier)
        if channel is None:
            raise ValueError(f"distribution channel not found: {request.channel_identifier}")
        self.validator.validate_request(request, channel)
        result = channel.distribute(request)
        self.validator.validate_result(result)
        return result


def create_default_distribution_registry() -> DistributionRegistry:
    """Create the default local and placeholder distribution channels."""

    return DistributionRegistry(
        channels=[
            DistributionChannel(
                identifier="local-file",
                name="Local File Export",
                channel_type="local_file",
                supported_formats=["text", "markdown", "html", "docx", "pdf", "pptx"],
                handler=local_file_handler,
            ),
            DistributionChannel(
                identifier="archive-folder",
                name="Archive Folder",
                channel_type="archive_folder",
                supported_formats=["text", "markdown", "html", "docx", "pdf", "pptx"],
                handler=archive_folder_handler,
            ),
            DistributionChannel(
                identifier="email-ready",
                name="Email-Ready Output",
                channel_type="email_ready",
                supported_formats=["text", "markdown", "html"],
                handler=dry_run_only_handler,
            ),
            DistributionChannel(
                identifier="markdown",
                name="Markdown Export",
                channel_type="markdown",
                supported_formats=["markdown"],
                handler=dry_run_only_handler,
            ),
            DistributionChannel(
                identifier="html",
                name="HTML Export",
                channel_type="html",
                supported_formats=["html"],
                handler=dry_run_only_handler,
            ),
            DistributionChannel(
                identifier="docx-placeholder",
                name="DOCX Placeholder",
                channel_type="docx",
                supported_formats=["docx"],
                placeholder=True,
                handler=dry_run_only_handler,
            ),
            DistributionChannel(
                identifier="pdf-placeholder",
                name="PDF Placeholder",
                channel_type="pdf",
                supported_formats=["pdf"],
                placeholder=True,
                handler=dry_run_only_handler,
            ),
            DistributionChannel(
                identifier="powerpoint-placeholder",
                name="PowerPoint Placeholder",
                channel_type="powerpoint",
                supported_formats=["pptx"],
                placeholder=True,
                handler=dry_run_only_handler,
            ),
            DistributionChannel(
                identifier="sharepoint-placeholder",
                name="SharePoint Placeholder",
                channel_type="sharepoint",
                supported_formats=["text", "markdown", "html", "docx", "pdf", "pptx"],
                placeholder=True,
                handler=dry_run_only_handler,
            ),
            DistributionChannel(
                identifier="teams-placeholder",
                name="Teams Placeholder",
                channel_type="teams",
                supported_formats=["text", "markdown", "html"],
                placeholder=True,
                handler=dry_run_only_handler,
            ),
        ]
    )
