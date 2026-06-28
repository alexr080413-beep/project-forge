from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class ContextReference:
    """A stable reference to an object included in a context snapshot."""

    reference_type: str
    identifier: str
    label: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("reference_type", self.reference_type)
        _validate_non_empty("identifier", self.identifier)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def sort_key(self) -> tuple[str, str, str, str]:
        return (self.reference_type, self.source, self.identifier, self.label)


@dataclass(slots=True)
class ExerciseContext:
    """Aggregated exercise information for downstream deterministic processing."""

    exercise_state: Any | None = None
    scenario: Any | None = None
    knowledge_documents: list[Any] = field(default_factory=list)
    entities: list[Any] = field(default_factory=list)
    events: list[Any] = field(default_factory=list)
    decision_results: list[Any] = field(default_factory=list)
    training_objectives: list[str] = field(default_factory=list)
    references: list[ContextReference] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_str_list("training_objectives", self.training_objectives)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")
        self.training_objectives = sorted(set(self.training_objectives))
        self.references = sorted(self.references, key=lambda reference: reference.sort_key())


@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    """A deterministic snapshot of an aggregated exercise context."""

    identifier: str
    context_type: str
    exercise_context: ExerciseContext
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("context_type", self.context_type)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(slots=True)
class ContextBuilder:
    """Builds deterministic context snapshots from loaded Project Forge engines."""

    knowledge_base: Any | None = None
    exercise_state: Any | None = None
    scenario_registry: Any | None = None
    entity_catalog: Any | None = None
    event_registry: Any | None = None
    decision_results: list[Any] = field(default_factory=list)
    training_objectives: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_str_list("training_objectives", self.training_objectives)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def build_current_context(self) -> ContextSnapshot:
        return self._build_snapshot("current", "current")

    def build_event_context(self, event_identifier: str) -> ContextSnapshot:
        _validate_non_empty("event_identifier", event_identifier)
        event = _get_event(self.event_registry, event_identifier)
        events = [event] if event is not None else []
        return self._build_snapshot(
            f"event:{event_identifier}",
            "event",
            events=events,
            metadata={"event_identifier": event_identifier},
        )

    def build_entity_context(self, entity_identifier: str) -> ContextSnapshot:
        _validate_non_empty("entity_identifier", entity_identifier)
        entity = _get_entity(self.entity_catalog, entity_identifier)
        related_events = [
            event
            for event in _list_events(self.event_registry)
            if entity_identifier in _event_related_entities(event)
        ]
        entities = [entity] if entity is not None else []
        return self._build_snapshot(
            f"entity:{entity_identifier}",
            "entity",
            entities=entities,
            events=related_events,
            metadata={"entity_identifier": entity_identifier},
        )

    def build_daily_context(self, exercise_day: int | None = None) -> ContextSnapshot:
        day = exercise_day or _current_exercise_day(self.exercise_state)
        events = [
            event
            for event in _list_events(self.event_registry)
            if getattr(event, "exercise_day", None) == day
        ]
        return self._build_snapshot(
            f"day:{day}",
            "daily",
            events=events,
            metadata={"exercise_day": day},
        )

    def _build_snapshot(
        self,
        identifier: str,
        context_type: str,
        *,
        entities: list[Any] | None = None,
        events: list[Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ContextSnapshot:
        selected_entities = _sort_by_identifier(
            entities if entities is not None else _list_entities(self.entity_catalog)
        )
        selected_events = _sort_by_identifier(
            events if events is not None else _list_events(self.event_registry)
        )
        knowledge_documents = _sort_by_identifier(_list_documents(self.knowledge_base))
        scenario = _current_scenario(self.scenario_registry)
        context = ExerciseContext(
            exercise_state=self.exercise_state,
            scenario=scenario,
            knowledge_documents=knowledge_documents,
            entities=selected_entities,
            events=selected_events,
            decision_results=list(self.decision_results),
            training_objectives=self._training_objectives(scenario),
            references=_references_for(
                knowledge_documents=knowledge_documents,
                entities=selected_entities,
                events=selected_events,
                decision_results=self.decision_results,
                scenario=scenario,
            ),
            metadata=dict(self.metadata),
        )
        snapshot_metadata = dict(metadata or {})
        return ContextSnapshot(
            identifier=identifier,
            context_type=context_type,
            exercise_context=context,
            metadata=snapshot_metadata,
        )

    def _training_objectives(self, scenario: Any | None) -> list[str]:
        objectives = list(self.training_objectives)
        objectives.extend(
            str(objective)
            for objective in getattr(
                self.exercise_state,
                "active_training_objectives",
                [],
            )
        )
        objectives.extend(
            str(getattr(objective, "title", ""))
            for objective in getattr(scenario, "active_objectives", [])
        )
        return [objective for objective in objectives if objective.strip()]


def _references_for(
    *,
    knowledge_documents: list[Any],
    entities: list[Any],
    events: list[Any],
    decision_results: list[Any],
    scenario: Any | None,
) -> list[ContextReference]:
    references: list[ContextReference] = []
    if scenario is not None:
        references.append(
            ContextReference(
                reference_type="scenario",
                identifier=str(getattr(scenario, "identifier", "")),
                label=str(getattr(scenario, "scenario_name", "")),
                source="scenario_engine",
            )
        )
    references.extend(_knowledge_references(knowledge_documents))
    references.extend(_entity_references(entities))
    references.extend(_event_references(events))
    references.extend(_decision_references(decision_results))
    return references


def _knowledge_references(documents: list[Any]) -> list[ContextReference]:
    return [
        ContextReference(
            reference_type="knowledge_document",
            identifier=str(getattr(document, "relative_path", "")),
            label=str(getattr(document, "document_type", "")),
            source="knowledge_engine",
        )
        for document in documents
    ]


def _entity_references(entities: list[Any]) -> list[ContextReference]:
    return [
        ContextReference(
            reference_type="entity",
            identifier=str(getattr(entity, "identifier", "")),
            label=str(getattr(entity, "display_name", "")),
            source="entity_engine",
        )
        for entity in entities
    ]


def _event_references(events: list[Any]) -> list[ContextReference]:
    return [
        ContextReference(
            reference_type="event",
            identifier=str(getattr(event, "identifier", "")),
            label=str(getattr(event, "title", "")),
            source="event_engine",
        )
        for event in events
    ]


def _decision_references(decision_results: list[Any]) -> list[ContextReference]:
    return [
        ContextReference(
            reference_type="decision_result",
            identifier=str(getattr(result, "decision_identifier", "")),
            label=str(getattr(getattr(result, "outcome", ""), "value", "")),
            source="decision_engine",
        )
        for result in decision_results
    ]


def _current_scenario(scenario_registry: Any | None) -> Any | None:
    get_current = getattr(scenario_registry, "get_current_scenario", None)
    return get_current() if callable(get_current) else None


def _get_event(event_registry: Any | None, identifier: str) -> Any | None:
    get_event = getattr(event_registry, "get_event", None)
    return get_event(identifier) if callable(get_event) else None


def _get_entity(entity_catalog: Any | None, identifier: str) -> Any | None:
    get_entity = getattr(entity_catalog, "get_entity", None)
    return get_entity(identifier) if callable(get_entity) else None


def _list_documents(knowledge_base: Any | None) -> list[Any]:
    list_documents = getattr(knowledge_base, "list_documents", None)
    return list(list_documents()) if callable(list_documents) else []


def _list_entities(entity_catalog: Any | None) -> list[Any]:
    return list(getattr(entity_catalog, "entities", []) or [])


def _list_events(event_registry: Any | None) -> list[Any]:
    return list(getattr(event_registry, "events", []) or [])


def _event_related_entities(event: Any) -> set[str]:
    related = set(getattr(event, "related_entities", []) or [])
    for impact in getattr(event, "impacts", []) or []:
        related.update(getattr(impact, "affected_entities", []) or [])
    return related


def _current_exercise_day(exercise_state: Any | None) -> int | None:
    current_day = getattr(exercise_state, "current_day", None)
    return getattr(current_day, "day_number", None)


def _sort_by_identifier(items: list[Any]) -> list[Any]:
    return sorted(items, key=lambda item: str(_stable_identifier(item)))


def _stable_identifier(item: Any) -> str:
    for attribute in ("identifier", "relative_path", "path", "display_name", "title"):
        value = getattr(item, attribute, None)
        if value is not None:
            return str(value)
    return repr(item)


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")
