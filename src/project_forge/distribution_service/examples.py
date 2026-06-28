from __future__ import annotations

from .models import DistributionItem, DistributionRequest, DistributionTarget


def create_sample_distribution_item() -> DistributionItem:
    """Create a safe notional approved product output for examples and tests."""

    return DistributionItem(
        item_id="distribution-item-001",
        product_identifier="product-intsum-001",
        product_type="intelligence_summary",
        content="# Daily Intelligence Summary\n\nNotional approved content.",
        output_format="markdown",
        approved=True,
        metadata={"notional": True, "approved_by": "EXCON"},
    )


def create_sample_distribution_request() -> DistributionRequest:
    """Create a dry-run markdown distribution request."""

    return DistributionRequest(
        request_id="distribution-request-001",
        item=create_sample_distribution_item(),
        channel_identifier="markdown",
        target=DistributionTarget(
            identifier="markdown-preview",
            target_type="markdown",
            destination="outputs/daily-intelligence-summary.md",
            metadata={"notional": True},
        ),
        dry_run=True,
        requested_by="EXCON",
        metadata={"ticket": "forge-romeo-001"},
    )
