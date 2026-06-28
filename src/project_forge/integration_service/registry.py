from __future__ import annotations

from dataclasses import dataclass, field

from .models import (
    IntegrationConnector,
    IntegrationRequest,
    IntegrationResult,
    IntegrationSource,
    IntegrationSourceType,
    dry_run_connector_handler,
)
from .validator import IntegrationValidator


@dataclass(slots=True)
class IntegrationRegistry:
    """In-memory registry and dry-run collection surface for integrations."""

    sources: list[IntegrationSource] = field(default_factory=list)
    connectors: list[IntegrationConnector] = field(default_factory=list)
    validator: IntegrationValidator = field(default_factory=IntegrationValidator)

    def __post_init__(self) -> None:
        self.validator.validate_sources(self.sources)
        self.validator.validate_connectors(self.connectors)
        self.sources.sort(key=lambda source: source.source_id)
        self.connectors.sort(key=lambda connector: connector.identifier)

    def register_source(self, source: IntegrationSource) -> None:
        if self.get_source(source.source_id) is not None:
            raise ValueError(f"integration source identifier already exists: {source.source_id}")
        self.validator.validate_source(source)
        self.sources.append(source)
        self.sources.sort(key=lambda item: item.source_id)

    def register_connector(self, connector: IntegrationConnector) -> None:
        if self.get_connector(connector.identifier) is not None:
            raise ValueError(
                f"integration connector identifier already exists: {connector.identifier}"
            )
        self.validator.validate_connector(connector)
        self.connectors.append(connector)
        self.connectors.sort(key=lambda item: item.identifier)

    def get_source(self, source_id: str) -> IntegrationSource | None:
        for source in self.sources:
            if source.source_id == source_id:
                return source
        return None

    def get_connector(self, identifier: str) -> IntegrationConnector | None:
        for connector in self.connectors:
            if connector.identifier == identifier:
                return connector
        return None

    def get_connector_for_source(
        self,
        source: IntegrationSource,
    ) -> IntegrationConnector | None:
        for connector in self.connectors:
            if connector.source_type is source.source_type:
                return connector
        return None

    def list_sources(self) -> list[IntegrationSource]:
        return list(self.sources)

    def list_connectors(self) -> list[IntegrationConnector]:
        return list(self.connectors)

    def collect(self, request: IntegrationRequest) -> IntegrationResult:
        connector = self.get_connector_for_source(request.source)
        if connector is None:
            raise ValueError(
                f"integration connector not found for source type: {request.source.source_type.value}"
            )
        self.validator.validate_request(request, connector)
        result = connector.collect(request)
        self.validator.validate_result(result)
        return result

    def collect_source(
        self,
        source_id: str,
        *,
        dry_run: bool = True,
        requested_by: str = "Project Forge",
    ) -> IntegrationResult:
        source = self.get_source(source_id)
        if source is None:
            raise ValueError(f"integration source not found: {source_id}")
        request = IntegrationRequest(
            request_id=f"{source.source_id}:collection",
            source=source,
            dry_run=dry_run,
            requested_by=requested_by,
        )
        return self.collect(request)


def create_default_integration_connectors() -> list[IntegrationConnector]:
    """Create local dry-run connectors for every supported source type."""

    return [
        IntegrationConnector(
            identifier="rss",
            name="RSS Connector",
            source_type=IntegrationSourceType.RSS,
            handler=dry_run_connector_handler,
        ),
        IntegrationConnector(
            identifier="website",
            name="Website Connector",
            source_type=IntegrationSourceType.WEBSITE,
            handler=dry_run_connector_handler,
        ),
        IntegrationConnector(
            identifier="manual-upload",
            name="Manual Upload Connector",
            source_type=IntegrationSourceType.MANUAL_UPLOAD,
            handler=dry_run_connector_handler,
        ),
        IntegrationConnector(
            identifier="local-file",
            name="Local File Connector",
            source_type=IntegrationSourceType.LOCAL_FILE,
            handler=dry_run_connector_handler,
        ),
        IntegrationConnector(
            identifier="email-placeholder",
            name="Email Placeholder Connector",
            source_type=IntegrationSourceType.EMAIL_PLACEHOLDER,
            placeholder=True,
            handler=dry_run_connector_handler,
        ),
        IntegrationConnector(
            identifier="social-media-placeholder",
            name="Social Media Placeholder Connector",
            source_type=IntegrationSourceType.SOCIAL_MEDIA_PLACEHOLDER,
            placeholder=True,
            handler=dry_run_connector_handler,
        ),
        IntegrationConnector(
            identifier="sharepoint-placeholder",
            name="SharePoint Placeholder Connector",
            source_type=IntegrationSourceType.SHAREPOINT_PLACEHOLDER,
            placeholder=True,
            handler=dry_run_connector_handler,
        ),
        IntegrationConnector(
            identifier="api-placeholder",
            name="API Placeholder Connector",
            source_type=IntegrationSourceType.API_PLACEHOLDER,
            placeholder=True,
            handler=dry_run_connector_handler,
        ),
    ]


def create_default_integration_registry(
    *,
    sources: list[IntegrationSource] | None = None,
    validator: IntegrationValidator | None = None,
) -> IntegrationRegistry:
    """Create a registry with default dry-run connectors."""

    return IntegrationRegistry(
        sources=sources or [],
        connectors=create_default_integration_connectors(),
        validator=validator or IntegrationValidator(),
    )
