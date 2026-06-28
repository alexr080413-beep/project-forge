from __future__ import annotations

from dataclasses import dataclass, field

from .models import EventType, ExerciseEvent
from .validator import EventValidator


@dataclass(slots=True)
class EventRegistry:
    """In-memory registry for validated exercise events."""

    events: list[ExerciseEvent] = field(default_factory=list)
    validator: EventValidator = field(default_factory=EventValidator)

    def __post_init__(self) -> None:
        self.validator.validate_events(self.events)

    def get_event(self, identifier: str) -> ExerciseEvent | None:
        for event in self.events:
            if event.identifier == identifier:
                return event
        return None

    def list_by_type(self, event_type: EventType) -> list[ExerciseEvent]:
        return [event for event in self.events if event.event_type is event_type]

    def add_event(self, event: ExerciseEvent) -> None:
        self.validator.validate_event(event)
        if self.get_event(event.identifier) is not None:
            raise ValueError(f"event identifier already exists: {event.identifier}")
        self.events.append(event)
