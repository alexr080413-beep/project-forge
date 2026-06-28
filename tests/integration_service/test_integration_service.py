from pathlib import Path

import pytest

from project_forge.integration_service import (
    IntegrationConnector,
    IntegrationRequest,
    IntegrationRegistry,
    IntegrationSource,
    IntegrationSourceLoader,
    IntegrationSourceType,
    IntegrationStatus,
    IntegrationValidator,
    create_default_integration_registry,
    load_integration_sources,
)


def source(
    source_id: str = "source-1",
    source_type: IntegrationSourceType = IntegrationSourceType.RSS,
    location: str = "https://example.com/rss.xml",
) -> IntegrationSource:
    return IntegrationSource(
        source_id=source_id,
        name="Source",
        source_type=source_type,
        location=location,
    )


def test_integration_sources_load_from_yaml() -> None:
    registry = load_integration_sources("config/integration_sources.example.yaml")

    assert [item.source_id for item in registry.list_sources()] == [
        "api-placeholder-example",
        "email-placeholder-example",
        "local-file-example",
        "manual-upload-example",
        "rss-public-example",
        "sharepoint-placeholder-example",
        "social-media-placeholder-example",
        "website-public-example",
    ]
    assert registry.get_source("local-file-example").source_type is (
        IntegrationSourceType.LOCAL_FILE
    )


def test_connectors_can_be_registered() -> None:
    registry = IntegrationRegistry()
    connector = IntegrationConnector(
        identifier="custom-rss",
        name="Custom RSS",
        source_type=IntegrationSourceType.RSS,
    )

    registry.register_connector(connector)

    assert registry.get_connector("custom-rss") is connector


def test_default_connectors_cover_supported_source_types() -> None:
    registry = create_default_integration_registry()

    assert [connector.identifier for connector in registry.list_connectors()] == [
        "api-placeholder",
        "email-placeholder",
        "local-file",
        "manual-upload",
        "rss",
        "sharepoint-placeholder",
        "social-media-placeholder",
        "website",
    ]


def test_dry_run_collection_succeeds_with_audit_metadata() -> None:
    registry = create_default_integration_registry(sources=[source()])

    result = registry.collect_source("source-1", dry_run=True, requested_by="EXCON")

    assert result.status is IntegrationStatus.DRY_RUN
    assert result.message == "dry-run collection succeeded"
    assert result.metadata["dry_run"] is True
    assert result.metadata["source_type"] == "rss"
    assert result.audit_log[-1] == "dry-run collection for rss"


def test_placeholder_connector_returns_placeholder_when_not_dry_run() -> None:
    registry = create_default_integration_registry(
        sources=[
            source(
                source_type=IntegrationSourceType.EMAIL_PLACEHOLDER,
                location="mailbox://exercise-control",
            )
        ]
    )

    result = registry.collect_source("source-1", dry_run=False)

    assert result.status is IntegrationStatus.PLACEHOLDER
    assert "no external action performed" in result.message


def test_invalid_source_url_fails_validation() -> None:
    with pytest.raises(ValueError):
        IntegrationValidator().validate_source(
            source(location="not-a-url")
        )


def test_invalid_local_file_fails_validation(tmp_path: Path) -> None:
    validator = IntegrationValidator(path_base=tmp_path)

    with pytest.raises(FileNotFoundError):
        validator.validate_source(
            source(
                source_type=IntegrationSourceType.LOCAL_FILE,
                location="missing.txt",
            )
        )


def test_disabled_source_fails_collection_with_audit_metadata() -> None:
    disabled = IntegrationSource(
        source_id="disabled",
        name="Disabled",
        source_type=IntegrationSourceType.MANUAL_UPLOAD,
        location="manual://upload",
        enabled=False,
    )
    registry = create_default_integration_registry(sources=[disabled])

    result = registry.collect_source("disabled")

    assert result.status is IntegrationStatus.FAILED
    assert result.audit_log[-1] == "source disabled"


def test_request_source_type_must_match_connector() -> None:
    registry = IntegrationRegistry(
        connectors=[
            IntegrationConnector(
                identifier="rss",
                name="RSS",
                source_type=IntegrationSourceType.RSS,
            )
        ]
    )
    request = IntegrationRequest(
        request_id="request",
        source=source(source_type=IntegrationSourceType.WEBSITE, location="https://example.com"),
    )

    with pytest.raises(ValueError):
        registry.collect(request)


def test_duplicate_sources_are_rejected() -> None:
    item = source()

    with pytest.raises(ValueError):
        IntegrationRegistry(sources=[item, item])


def test_loader_rejects_missing_config(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        IntegrationSourceLoader(tmp_path / "missing.yaml").load()
