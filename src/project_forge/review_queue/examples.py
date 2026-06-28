from __future__ import annotations

from datetime import datetime, timezone

from .models import ReviewItem, ReviewQueue


def create_sample_review_items() -> list[ReviewItem]:
    """Create safe notional review items for tests and documentation examples."""

    return [
        ReviewItem(
            item_id="review-001",
            product_identifier="product-intsum-001",
            product_type="intelligence_summary",
            title="Daily Intelligence Summary Draft",
            priority=90,
            submitted_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
            metadata={"notional": True},
        ),
        ReviewItem(
            item_id="review-002",
            product_identifier="product-spotrep-001",
            product_type="spotrep",
            title="Border Activity SPOTREP Draft",
            priority=100,
            submitted_at=datetime(2026, 1, 1, 12, 5, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, 12, 5, tzinfo=timezone.utc),
            metadata={"notional": True},
        ),
        ReviewItem(
            item_id="review-003",
            product_identifier="product-media-001",
            product_type="social_media",
            title="Notional Social Media Post Draft",
            priority=50,
            submitted_at=datetime(2026, 1, 1, 12, 10, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, 12, 10, tzinfo=timezone.utc),
            metadata={"notional": True},
        ),
    ]


def create_sample_review_queue() -> ReviewQueue:
    """Create a sample review queue with ordered notional review items."""

    return ReviewQueue(
        identifier="sample-review-queue",
        name="Sample Review Queue",
        items=create_sample_review_items(),
        metadata={"notional": True},
    )
