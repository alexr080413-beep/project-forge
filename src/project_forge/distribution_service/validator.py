from __future__ import annotations

from .models import (
    DistributionChannel,
    DistributionRequest,
    DistributionResult,
    DistributionStatus,
)


class DistributionValidator:
    """Validates distribution channels, targets, requests, and results."""

    def validate_channel(self, channel: DistributionChannel) -> None:
        if not channel.supported_formats:
            raise ValueError("distribution channel must support at least one format")

    def validate_channels(self, channels: list[DistributionChannel]) -> None:
        identifiers = [channel.identifier for channel in channels]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("distribution channel identifiers must be unique")
        for channel in channels:
            self.validate_channel(channel)

    def validate_request(
        self,
        request: DistributionRequest,
        channel: DistributionChannel,
    ) -> None:
        if not request.item.approved:
            raise ValueError("distribution item must be approved before distribution")
        if request.channel_identifier != channel.identifier:
            raise ValueError("request channel identifier must match channel")
        if request.item.output_format not in channel.supported_formats:
            raise ValueError("item output format is not supported by channel")
        self.validate_target(request, channel)

    def validate_target(
        self,
        request: DistributionRequest,
        channel: DistributionChannel,
    ) -> None:
        expected_type = channel.channel_type
        if request.target.target_type != expected_type:
            raise ValueError("target type must match distribution channel type")

    def validate_result(self, result: DistributionResult) -> None:
        if result.status is DistributionStatus.FAILED and not result.message.strip():
            raise ValueError("failed distribution results must include a message")
        if not result.audit_log:
            raise ValueError("distribution results must include audit metadata")
