from __future__ import annotations

from dataclasses import dataclass, field

from .models import ReviewItem, Reviewer, ReviewQueue
from .registry import ReviewRegistry
from .validator import ReviewValidator


@dataclass(slots=True)
class ReviewQueueManager:
    """High-level local interface for review queue operations."""

    registry: ReviewRegistry = field(default_factory=ReviewRegistry)
    validator: ReviewValidator = field(default_factory=ReviewValidator)

    def create_queue(
        self,
        identifier: str,
        name: str,
        *,
        metadata: dict[str, object] | None = None,
    ) -> ReviewQueue:
        queue = ReviewQueue(
            identifier=identifier,
            name=name,
            metadata=dict(metadata or {}),
        )
        self.registry.register_queue(queue)
        return queue

    def add_item(self, queue_id: str, item: ReviewItem) -> ReviewItem:
        queue = self._required_queue(queue_id)
        queue.add_item(item)
        self.validator.validate_queue(queue)
        return item

    def remove_item(self, queue_id: str, item_id: str) -> ReviewItem:
        queue = self._required_queue(queue_id)
        item = queue.remove_item(item_id)
        self.validator.validate_queue(queue)
        return item

    def update_item(self, queue_id: str, item: ReviewItem) -> ReviewItem:
        queue = self._required_queue(queue_id)
        queue.update_item(item)
        self.validator.validate_queue(queue)
        return item

    def assign_reviewer(
        self,
        queue_id: str,
        item_id: str,
        reviewer: Reviewer,
        note: str = "",
    ) -> ReviewItem:
        item = self._required_queue(queue_id).assign_reviewer(
            item_id,
            reviewer,
            note=note,
        )
        self.validator.validate_item(item)
        return item

    def approve(
        self,
        queue_id: str,
        item_id: str,
        reviewer: Reviewer,
        note: str = "",
    ) -> ReviewItem:
        item = self._required_queue(queue_id).approve(item_id, reviewer, note=note)
        self.validator.validate_item(item)
        return item

    def reject(
        self,
        queue_id: str,
        item_id: str,
        reviewer: Reviewer,
        note: str = "",
    ) -> ReviewItem:
        item = self._required_queue(queue_id).reject(item_id, reviewer, note=note)
        self.validator.validate_item(item)
        return item

    def request_revision(
        self,
        queue_id: str,
        item_id: str,
        reviewer: Reviewer,
        note: str = "",
    ) -> ReviewItem:
        item = self._required_queue(queue_id).request_revision(
            item_id,
            reviewer,
            note=note,
        )
        self.validator.validate_item(item)
        return item

    def _required_queue(self, queue_id: str) -> ReviewQueue:
        queue = self.registry.get_queue(queue_id)
        if queue is None:
            raise ValueError(f"review queue not found: {queue_id}")
        return queue
