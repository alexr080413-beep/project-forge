from datetime import datetime, timezone
from pathlib import Path

import pytest

from project_forge.event_engine import (
    EventImpact,
    EventLoader,
    EventRegistry,
    EventSeverity,
    EventSource,
    EventStatus,
    EventType,
    EventValidator,
    ExerciseEvent,
    load_events,
)


def make_event(identifier: str = "evt-test") -> ExerciseEvent:
    return ExerciseEvent(
        identifier=identifier,
        title="Test Event",
        summary="A notional event for tests.",
        event_type=EventType.MILITARY,
        originating_source=EventSource.EXCON,
        scenario_actors_involved=["Joint Task Force Headquarters"],
        locations_involved=["Capital Operations Center"],
        timestamp=datetime(2026, 6, 27, 15, 30, tzinfo=timezone.utc),
        exercise_day=2,
        exercise_phase="execution",
        confidence=0.9,
        impacts=[
            EventImpact(
                area="force_posture",
                severity=EventSeverity.MEDIUM,
                summary="Controllers should monitor posture changes.",
                affected_entities=["unit-jtf-hq"],
            )
        ],
        related_entities=["unit-jtf-hq"],
        supporting_source_references=["config/entities.example.yaml"],
        tags=["test"],
        metadata={"notional": True},
        status=EventStatus.ACTIVE,
    )


def test_exercise_event_can_be_created_directly() -> None:
    event = make_event()

    assert event.identifier == "evt-test"
    assert event.event_type is EventType.MILITARY
    assert event.status is EventStatus.ACTIVE
    assert event.impacts[0].severity is EventSeverity.MEDIUM


def test_loader_loads_example_events() -> None:
    registry = load_events("config/events.example.yaml")

    assert len(registry.events) == 2
    assert registry.get_event("evt-001").title.startswith("Host Nation")
    assert registry.get_event("evt-001").originating_source is EventSource.EXCON
    assert registry.get_event("evt-002").status is EventStatus.ACTIVE


def test_registry_supports_lookup_by_id_and_event_type() -> None:
    political = make_event("evt-political")
    political.event_type = EventType.POLITICAL
    military = make_event("evt-military")
    registry = EventRegistry(events=[political, military])

    assert registry.get_event("evt-military") is military
    assert registry.get_event("missing") is None
    assert registry.list_by_type(EventType.POLITICAL) == [political]


def test_validator_accepts_valid_event() -> None:
    EventValidator().validate_event(make_event())


def test_validator_rejects_duplicate_identifiers() -> None:
    with pytest.raises(ValueError):
        EventRegistry(events=[make_event("evt-dup"), make_event("evt-dup")])


def test_validator_rejects_event_without_impacts() -> None:
    event = make_event()
    event.impacts = []

    with pytest.raises(ValueError):
        EventValidator().validate_event(event)


def test_model_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        ExerciseEvent(
            identifier="evt-bad",
            title="Bad Event",
            summary="Invalid confidence.",
            event_type=EventType.CYBER,
            originating_source=EventSource.SYSTEM,
            scenario_actors_involved=["EXCON"],
            locations_involved=["Main Operations Center"],
            timestamp=datetime.now(timezone.utc),
            exercise_day=1,
            exercise_phase="execution",
            confidence=1.5,
        )


def test_loader_rejects_invalid_timestamp(tmp_path: Path) -> None:
    config_path = tmp_path / "events.yaml"
    config_path.write_text(
        """
{
  "events": [
    {
      "identifier": "evt-bad-time",
      "title": "Bad Time",
      "summary": "Invalid timestamp.",
      "event_type": "information",
      "originating_source": "system",
      "scenario_actors_involved": ["EXCON"],
      "locations_involved": ["Main Operations Center"],
      "timestamp": "not-a-time",
      "exercise_day": 1,
      "exercise_phase": "execution",
      "confidence": 0.5,
      "impacts": [
        {
          "area": "information_environment",
          "severity": "low",
          "summary": "Placeholder."
        }
      ]
    }
  ]
}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        EventLoader(config_path).load()
