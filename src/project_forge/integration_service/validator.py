from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from .models import (
    IntegrationConnector,
    IntegrationRequest,
    IntegrationResult,
    IntegrationSource,
    IntegrationSourceType,
    IntegrationStatus,
)


class IntegrationValidator:
    """Validates integration sources, connectors, requests, and results."""

    def __init__(self, path_base: str | Path = ".") -> None:
        self.path_base = Path(path_base)

    def validate_source(self, source: IntegrationSource) -> None:
        if source.source_type in {
            IntegrationSourceType.RSS,
            IntegrationSourceType.WEBSITE,
            IntegrationSourceType.API_PLACEHOLDER,
            IntegrationSourceType.SHAREPOINT_PLACEHOLDER,
        }:
            self._validate_url(source.location)
        elif source.source_type is IntegrationSourceType.LOCAL_FILE:
            resolved = self._resolve_path(source.location)
            if not resolved.exists() or not resolved.is_file():
                raise FileNotFoundError(f"local file source does not exist: {resolved}")
        elif source.source_type is IntegrationSourceType.MANUAL_UPLOAD:
            self._validate_non_blank_location(source)
        elif source.source_type in {
            IntegrationSourceType.EMAIL_PLACEHOLDER,
            IntegrationSourceType.SOCIAL_MEDIA_PLACEHOLDER,
        }:
            self._validate_non_blank_location(source)

    def validate_sources(self, sources: list[IntegrationSource]) -> None:
        identifiers = [source.source_id for source in sources]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("integration source identifiers must be unique")
        for source in sources:
            self.validate_source(source)

    def validate_connector(self, connector: IntegrationConnector) -> None:
        if connector.placeholder and connector.source_type in {
            IntegrationSourceType.RSS,
            IntegrationSourceType.WEBSITE,
            IntegrationSourceType.MANUAL_UPLOAD,
            IntegrationSourceType.LOCAL_FILE,
        }:
            raise ValueError("core source connectors must not be placeholders")

    def validate_connectors(self, connectors: list[IntegrationConnector]) -> None:
        identifiers = [connector.identifier for connector in connectors]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("integration connector identifiers must be unique")
        for connector in connectors:
            self.validate_connector(connector)

    def validate_request(
        self,
        request: IntegrationRequest,
        connector: IntegrationConnector,
    ) -> None:
        self.validate_source(request.source)
        if request.source.source_type is not connector.source_type:
            raise ValueError("request source type must match connector source type")

    def validate_result(self, result: IntegrationResult) -> None:
        if result.status is IntegrationStatus.FAILED and not result.message.strip():
            raise ValueError("failed integration results must include a message")
        if not result.audit_log:
            raise ValueError("integration results must include audit metadata")

    def _validate_url(self, value: str) -> None:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source location must be an http or https URL")

    def _validate_non_blank_location(self, source: IntegrationSource) -> None:
        if not source.location.strip():
            raise ValueError("source location must not be blank")

    def _resolve_path(self, path_value: str) -> Path:
        path = Path(path_value)
        if path.is_absolute():
            return path
        return (self.path_base / path).resolve()
