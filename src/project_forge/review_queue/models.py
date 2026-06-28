from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ReviewStatus(str, Enum):
    """Lifecycle states for a product awaiting human review."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


@dataclass(frozen=True, slots=True)
class Reviewer:
    """A human reviewer eligible to make review decisions."""

    reviewer_id: str
    display_name: str
    role: str = "reviewer"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("reviewer_id", self.reviewer_id)
        _validate_non_empty("display_name", self.display_name)
        _validate_non_empty("role", self.role)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ReviewComment:
    """A reviewer note attached to a review item."""

    author_id: str
    note: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("author_id", self.author_id)
        _validate_non_empty("note", self.note)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class ReviewDecision:
    """An auditable review action."""

    reviewer_id: str
    status: ReviewStatus
    note: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("reviewer_id", self.reviewer_id)
        if self.status not in {
            ReviewStatus.APPROVED,
            ReviewStatus.REJECTED,
            ReviewStatus.REVISION_REQUESTED,
            ReviewStatus.ASSIGNED,
        }:
            raise ValueError("review decision status must be an action status")
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class ReviewItem:
    """A generated product held for human review before release."""

    item_id: str
    product_identifier: str
    product_type: str
    title: str
    priority: int = 100
    status: ReviewStatus = ReviewStatus.PENDING
    assigned_reviewer: Reviewer | None = None
    notes: list[ReviewComment] = field(default_factory=list)
    audit_history: list[ReviewDecision] = field(default_factory=list)
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("item_id", self.item_id)
        _validate_non_empty("product_identifier", self.product_identifier)
        _validate_non_empty("product_type", self.product_type)
        _validate_non_empty("title", self.title)
        if self.priority < 0:
            raise ValueError("priority must be greater than or equal to zero")
        _validate_metadata(self.metadata)

    def assign_reviewer(self, reviewer: Reviewer, note: str = "") -> None:
        self.assigned_reviewer = reviewer
        self.status = ReviewStatus.ASSIGNED
        self._record_decision(
            ReviewDecision(
                reviewer_id=reviewer.reviewer_id,
                status=ReviewStatus.ASSIGNED,
                note=note,
            )
        )

    def add_comment(self, comment: ReviewComment) -> None:
        self.notes.append(comment)
        self.updated_at = datetime.now(timezone.utc)

    def approve(self, reviewer: Reviewer, note: str = "") -> None:
        self._apply_terminal_decision(reviewer, ReviewStatus.APPROVED, note)

    def reject(self, reviewer: Reviewer, note: str = "") -> None:
        self._apply_terminal_decision(reviewer, ReviewStatus.REJECTED, note)

    def request_revision(self, reviewer: Reviewer, note: str = "") -> None:
        self._apply_terminal_decision(
            reviewer,
            ReviewStatus.REVISION_REQUESTED,
            note,
        )

    def sort_key(self) -> tuple[int, datetime, str]:
        return (-self.priority, self.submitted_at, self.item_id)

    def _apply_terminal_decision(
        self,
        reviewer: Reviewer,
        status: ReviewStatus,
        note: str,
    ) -> None:
        self.assigned_reviewer = reviewer
        self.status = status
        self._record_decision(
            ReviewDecision(
                reviewer_id=reviewer.reviewer_id,
                status=status,
                note=note,
            )
        )

    def _record_decision(self, decision: ReviewDecision) -> None:
        self.audit_history.append(decision)
        if decision.note.strip():
            self.notes.append(
                ReviewComment(
                    author_id=decision.reviewer_id,
                    note=decision.note,
                    created_at=decision.created_at,
                )
            )
        self.updated_at = decision.created_at


@dataclass(slots=True)
class ReviewQueue:
    """Ordered local queue for products awaiting review."""

    identifier: str = "default"
    name: str = "Default Review Queue"
    items: list[ReviewItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_metadata(self.metadata)
        self._validate_unique_items()
        self._sort_items()

    def add_item(self, item: ReviewItem) -> None:
        if self.get_item(item.item_id) is not None:
            raise ValueError(f"review item identifier already exists: {item.item_id}")
        self.items.append(item)
        self._sort_items()

    def remove_item(self, item_id: str) -> ReviewItem:
        item = self.get_item(item_id)
        if item is None:
            raise ValueError(f"review item not found: {item_id}")
        self.items.remove(item)
        return item

    def update_item(self, item: ReviewItem) -> None:
        for index, existing in enumerate(self.items):
            if existing.item_id == item.item_id:
                self.items[index] = item
                self._sort_items()
                return
        raise ValueError(f"review item not found: {item.item_id}")

    def get_item(self, item_id: str) -> ReviewItem | None:
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def list_items(self) -> list[ReviewItem]:
        return list(self.items)

    def assign_reviewer(
        self,
        item_id: str,
        reviewer: Reviewer,
        note: str = "",
    ) -> ReviewItem:
        item = self._required_item(item_id)
        item.assign_reviewer(reviewer, note=note)
        self._sort_items()
        return item

    def approve(self, item_id: str, reviewer: Reviewer, note: str = "") -> ReviewItem:
        item = self._required_item(item_id)
        item.approve(reviewer, note=note)
        self._sort_items()
        return item

    def reject(self, item_id: str, reviewer: Reviewer, note: str = "") -> ReviewItem:
        item = self._required_item(item_id)
        item.reject(reviewer, note=note)
        self._sort_items()
        return item

    def request_revision(
        self,
        item_id: str,
        reviewer: Reviewer,
        note: str = "",
    ) -> ReviewItem:
        item = self._required_item(item_id)
        item.request_revision(reviewer, note=note)
        self._sort_items()
        return item

    def _required_item(self, item_id: str) -> ReviewItem:
        item = self.get_item(item_id)
        if item is None:
            raise ValueError(f"review item not found: {item_id}")
        return item

    def _sort_items(self) -> None:
        self.items.sort(key=lambda item: item.sort_key())

    def _validate_unique_items(self) -> None:
        identifiers = [item.item_id for item in self.items]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("review item identifiers must be unique")


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
