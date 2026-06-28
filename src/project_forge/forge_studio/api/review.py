from __future__ import annotations

from project_forge.forge_studio.models import StudioReviewItem
from project_forge.forge_studio.registry import ForgeStudioRegistry


def list_review_items(
    registry: ForgeStudioRegistry,
    exercise_id: str | None = None,
) -> list[StudioReviewItem]:
    return registry.list_review_items(exercise_id=exercise_id)


def get_review_item(
    registry: ForgeStudioRegistry,
    item_id: str,
) -> StudioReviewItem | None:
    return registry.get_review_item(item_id)


def create_review_item(
    registry: ForgeStudioRegistry,
    item: StudioReviewItem,
) -> StudioReviewItem:
    registry.register_review_item(item)
    return item


def approve_review_item(
    registry: ForgeStudioRegistry,
    item_id: str,
    reviewer_id: str,
    *,
    comments: str = "",
) -> StudioReviewItem:
    return registry.approve_review_item(item_id, reviewer_id, comments=comments)


def reject_review_item(
    registry: ForgeStudioRegistry,
    item_id: str,
    reviewer_id: str,
    *,
    comments: str = "",
) -> StudioReviewItem:
    return registry.reject_review_item(item_id, reviewer_id, comments=comments)
