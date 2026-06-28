from __future__ import annotations

from .models import ReviewItem, ReviewQueue, ReviewStatus


class ReviewValidator:
    """Validates review queue state and transition records."""

    def validate_item(self, item: ReviewItem) -> None:
        if item.status is ReviewStatus.ASSIGNED and item.assigned_reviewer is None:
            raise ValueError("assigned review items must include an assigned reviewer")
        if item.status in {
            ReviewStatus.APPROVED,
            ReviewStatus.REJECTED,
            ReviewStatus.REVISION_REQUESTED,
        } and not item.audit_history:
            raise ValueError("completed review items must retain audit history")
        if item.status in {
            ReviewStatus.APPROVED,
            ReviewStatus.REJECTED,
            ReviewStatus.REVISION_REQUESTED,
        }:
            if item.audit_history[-1].status is not item.status:
                raise ValueError("latest review decision must match item status")
        if item.updated_at < item.submitted_at:
            raise ValueError("updated_at must not be earlier than submitted_at")

    def validate_queue(self, queue: ReviewQueue) -> None:
        identifiers = [item.item_id for item in queue.items]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("review item identifiers must be unique")
        for item in queue.items:
            self.validate_item(item)

    def validate_queues(self, queues: list[ReviewQueue]) -> None:
        identifiers = [queue.identifier for queue in queues]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("review queue identifiers must be unique")
        for queue in queues:
            self.validate_queue(queue)
