from __future__ import annotations

from .models import ExerciseEvent


class EventValidator:
    """Validates event collections for registry use."""

    def validate_event(self, event: ExerciseEvent) -> None:
        if not event.scenario_actors_involved:
            raise ValueError("scenario_actors_involved must include at least one actor")
        if not event.locations_involved:
            raise ValueError("locations_involved must include at least one location")
        if not event.impacts:
            raise ValueError("impacts must include at least one impact")

    def validate_events(self, events: list[ExerciseEvent]) -> None:
        identifiers = [event.identifier for event in events]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("event identifiers must be unique")
        for event in events:
            self.validate_event(event)
