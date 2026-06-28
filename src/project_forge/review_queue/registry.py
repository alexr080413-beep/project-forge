from __future__ import annotations

from dataclasses import dataclass, field

from .models import ReviewQueue
from .validator import ReviewValidator


@dataclass(slots=True)
class ReviewRegistry:
    """In-memory registry for named review queues."""

    queues: list[ReviewQueue] = field(default_factory=list)
    validator: ReviewValidator = field(default_factory=ReviewValidator)

    def __post_init__(self) -> None:
        self.validator.validate_queues(self.queues)
        self.queues.sort(key=lambda queue: queue.identifier)

    def register_queue(self, queue: ReviewQueue) -> None:
        if self.get_queue(queue.identifier) is not None:
            raise ValueError(f"review queue identifier already exists: {queue.identifier}")
        self.validator.validate_queue(queue)
        self.queues.append(queue)
        self.queues.sort(key=lambda item: item.identifier)

    def get_queue(self, identifier: str) -> ReviewQueue | None:
        for queue in self.queues:
            if queue.identifier == identifier:
                return queue
        return None

    def list_queues(self) -> list[ReviewQueue]:
        return list(self.queues)
