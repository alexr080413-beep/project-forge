from __future__ import annotations

from project_forge.forge_studio.models import TimelineEvent
from project_forge.forge_studio.registry import ForgeStudioRegistry


def list_timeline_events(
    registry: ForgeStudioRegistry,
    exercise_id: str | None = None,
) -> list[TimelineEvent]:
    return registry.list_timeline_events(exercise_id=exercise_id)


def get_timeline_event(
    registry: ForgeStudioRegistry,
    event_id: str,
) -> TimelineEvent | None:
    return registry.get_timeline_event(event_id)


def create_timeline_event(
    registry: ForgeStudioRegistry,
    event: TimelineEvent,
) -> TimelineEvent:
    registry.register_timeline_event(event)
    return event
