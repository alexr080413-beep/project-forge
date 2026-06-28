from pathlib import Path

import pytest

from project_forge.distribution_service import (
    DistributionChannel,
    DistributionItem,
    DistributionRegistry,
    DistributionRequest,
    DistributionStatus,
    DistributionTarget,
    DistributionValidator,
    create_default_distribution_registry,
    create_sample_distribution_request,
)


def approved_item(output_format: str = "markdown") -> DistributionItem:
    return DistributionItem(
        item_id="item-1",
        product_identifier="product-1",
        product_type="intelligence_summary",
        content="# Approved\n\nNotional content.",
        output_format=output_format,
        approved=True,
    )


def request_for(
    channel_identifier: str,
    target_type: str,
    *,
    item: DistributionItem | None = None,
    destination: str = "outputs/product.md",
    dry_run: bool = True,
) -> DistributionRequest:
    return DistributionRequest(
        request_id="request-1",
        item=item or approved_item(),
        channel_identifier=channel_identifier,
        target=DistributionTarget(
            identifier="target-1",
            target_type=target_type,
            destination=destination,
        ),
        dry_run=dry_run,
        requested_by="EXCON",
        metadata={"notional": True},
    )


def test_default_distribution_channels_are_registered() -> None:
    registry = create_default_distribution_registry()

    assert [channel.identifier for channel in registry.list_channels()] == [
        "archive-folder",
        "docx-placeholder",
        "email-ready",
        "html",
        "local-file",
        "markdown",
        "pdf-placeholder",
        "powerpoint-placeholder",
        "sharepoint-placeholder",
        "teams-placeholder",
    ]


def test_distribution_channels_can_be_registered() -> None:
    registry = DistributionRegistry()
    channel = DistributionChannel(
        identifier="custom",
        name="Custom",
        channel_type="custom",
        supported_formats=["text"],
    )

    registry.register_channel(channel)

    assert registry.get_channel("custom") is channel


def test_dry_run_distribution_succeeds_with_audit_metadata() -> None:
    registry = create_default_distribution_registry()
    result = registry.distribute(create_sample_distribution_request())

    assert result.status is DistributionStatus.DRY_RUN
    assert result.message == "dry-run distribution succeeded"
    assert result.metadata["dry_run"] is True
    assert result.metadata["product_identifier"] == "product-intsum-001"
    assert result.audit_log[-1] == "dry-run markdown distribution"


def test_target_validation_rejects_mismatched_channel_type() -> None:
    registry = create_default_distribution_registry()

    with pytest.raises(ValueError):
        registry.distribute(request_for("markdown", "html"))


def test_distribution_rejects_unapproved_items() -> None:
    registry = create_default_distribution_registry()
    item = DistributionItem(
        item_id="item-2",
        product_identifier="product-2",
        product_type="spotrep",
        content="Notional content.",
        output_format="markdown",
        approved=False,
    )

    with pytest.raises(ValueError):
        registry.distribute(request_for("markdown", "markdown", item=item))


def test_distribution_rejects_unsupported_output_format() -> None:
    registry = create_default_distribution_registry()

    with pytest.raises(ValueError):
        registry.distribute(
            request_for(
                "markdown",
                "markdown",
                item=approved_item(output_format="pdf"),
            )
        )


def test_placeholder_channel_returns_placeholder_status_when_not_dry_run() -> None:
    registry = create_default_distribution_registry()
    request = request_for(
        "teams-placeholder",
        "teams",
        item=approved_item(output_format="markdown"),
        dry_run=False,
    )

    result = registry.distribute(request)

    assert result.status is DistributionStatus.PLACEHOLDER
    assert "no external action performed" in result.message
    assert result.metadata["channel_type"] == "teams"


def test_local_file_export_writes_when_not_dry_run(tmp_path: Path) -> None:
    registry = create_default_distribution_registry()
    output_path = tmp_path / "product.md"

    result = registry.distribute(
        request_for(
            "local-file",
            "local_file",
            destination=str(output_path),
            dry_run=False,
        )
    )

    assert result.status is DistributionStatus.SUCCEEDED
    assert output_path.read_text(encoding="utf-8") == "# Approved\n\nNotional content."


def test_archive_folder_export_writes_when_not_dry_run(tmp_path: Path) -> None:
    registry = create_default_distribution_registry()

    result = registry.distribute(
        request_for(
            "archive-folder",
            "archive_folder",
            destination=str(tmp_path),
            dry_run=False,
        )
    )

    assert result.status is DistributionStatus.SUCCEEDED
    assert (tmp_path / "product-1.markdown").exists()


def test_validator_requires_audit_metadata() -> None:
    with pytest.raises(ValueError):
        DistributionValidator().validate_result(
            result_without_audit()
        )


def result_without_audit():
    from project_forge.distribution_service import DistributionResult

    return DistributionResult(
        request_id="request",
        channel_identifier="channel",
        status=DistributionStatus.SUCCEEDED,
        target_identifier="target",
        audit_log=[],
    )
