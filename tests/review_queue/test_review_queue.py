from datetime import datetime, timezone

import pytest

from project_forge.review_queue import (
    ReviewComment,
    ReviewItem,
    ReviewQueue,
    ReviewQueueManager,
    ReviewRegistry,
    ReviewStatus,
    ReviewValidator,
    Reviewer,
    create_sample_review_queue,
)


def reviewer() -> Reviewer:
    return Reviewer(
        reviewer_id="controller-1",
        display_name="Controller One",
        role="EXCON",
    )


def review_item(
    item_id: str,
    *,
    priority: int = 100,
    submitted_at: datetime | None = None,
) -> ReviewItem:
    timestamp = submitted_at or datetime(2026, 1, 1, tzinfo=timezone.utc)
    return ReviewItem(
        item_id=item_id,
        product_identifier=f"product-{item_id}",
        product_type="spotrep",
        title=f"Review {item_id}",
        priority=priority,
        submitted_at=timestamp,
        updated_at=timestamp,
    )


def test_queue_orders_by_priority_then_submission_time() -> None:
    queue = ReviewQueue(
        items=[
            review_item(
                "low",
                priority=10,
                submitted_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
            ),
            review_item(
                "high-late",
                priority=100,
                submitted_at=datetime(2026, 1, 1, 12, 5, tzinfo=timezone.utc),
            ),
            review_item(
                "high-early",
                priority=100,
                submitted_at=datetime(2026, 1, 1, 12, 1, tzinfo=timezone.utc),
            ),
        ]
    )

    assert [item.item_id for item in queue.list_items()] == [
        "high-early",
        "high-late",
        "low",
    ]


def test_queue_supports_add_remove_update() -> None:
    queue = ReviewQueue()
    first = review_item("first", priority=10)
    updated = review_item("first", priority=99)

    queue.add_item(first)
    queue.update_item(updated)
    removed = queue.remove_item("first")

    assert removed is updated
    assert queue.list_items() == []


def test_reviewer_assignment_records_history_and_notes() -> None:
    queue = ReviewQueue(items=[review_item("assign")])
    assigned = queue.assign_reviewer("assign", reviewer(), note="Taking review.")

    assert assigned.status is ReviewStatus.ASSIGNED
    assert assigned.assigned_reviewer.reviewer_id == "controller-1"
    assert assigned.audit_history[-1].status is ReviewStatus.ASSIGNED
    assert assigned.notes[-1].note == "Taking review."


def test_approval_rejection_and_revision_request_record_history() -> None:
    queue = ReviewQueue(
        items=[
            review_item("approve"),
            review_item("reject"),
            review_item("revise"),
        ]
    )
    controller = reviewer()

    approved = queue.approve("approve", controller, note="Approved for use.")
    rejected = queue.reject("reject", controller, note="Scenario mismatch.")
    revision = queue.request_revision("revise", controller, note="Add source note.")

    assert approved.status is ReviewStatus.APPROVED
    assert rejected.status is ReviewStatus.REJECTED
    assert revision.status is ReviewStatus.REVISION_REQUESTED
    assert [decision.status for decision in approved.audit_history] == [
        ReviewStatus.APPROVED
    ]
    assert rejected.notes[-1].note == "Scenario mismatch."
    assert revision.audit_history[-1].reviewer_id == "controller-1"


def test_comments_can_be_added_without_decision() -> None:
    item = review_item("comment")

    item.add_comment(ReviewComment(author_id="controller-1", note="Check references."))

    assert item.notes[0].note == "Check references."
    assert item.status is ReviewStatus.PENDING


def test_review_registry_registers_named_queues() -> None:
    queue = ReviewQueue(identifier="white-cell", name="White Cell")
    registry = ReviewRegistry()

    registry.register_queue(queue)

    assert registry.get_queue("white-cell") is queue
    assert registry.list_queues() == [queue]


def test_review_queue_manager_routes_operations() -> None:
    manager = ReviewQueueManager()
    manager.create_queue("default", "Default")
    manager.add_item("default", review_item("managed"))

    item = manager.approve("default", "managed", reviewer(), note="Ready.")

    assert item.status is ReviewStatus.APPROVED
    assert item.audit_history[-1].note == "Ready."


def test_validator_rejects_completed_item_without_history() -> None:
    item = review_item("invalid")
    item.status = ReviewStatus.APPROVED

    with pytest.raises(ValueError):
        ReviewValidator().validate_item(item)


def test_duplicate_review_items_are_rejected() -> None:
    item = review_item("duplicate")

    with pytest.raises(ValueError):
        ReviewQueue(items=[item, item])


def test_sample_review_queue_contains_ordered_notional_items() -> None:
    queue = create_sample_review_queue()

    assert [item.item_id for item in queue.list_items()] == [
        "review-002",
        "review-001",
        "review-003",
    ]
    assert all(item.metadata["notional"] is True for item in queue.list_items())
