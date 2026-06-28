from __future__ import annotations

from dataclasses import dataclass, field

from .models import (
    AuditActor,
    AuditCategory,
    AuditEntry,
    AuditEvent,
    AuditFilter,
    AuditSession,
)
from .validator import AuditValidator


@dataclass(slots=True)
class AuditRegistry:
    """In-memory audit registry for sessions and significant platform events."""

    entries: list[AuditEntry] = field(default_factory=list)
    sessions: list[AuditSession] = field(default_factory=list)
    validator: AuditValidator = field(default_factory=AuditValidator)

    def __post_init__(self) -> None:
        self.validator.validate_entries(self.entries)
        for session in self.sessions:
            self.validator.validate_session(session)
        self.entries.sort(key=lambda entry: (entry.event.occurred_at, entry.entry_id))
        self.sessions.sort(key=lambda session: session.session_id)

    def start_session(
        self,
        session_id: str,
        actor: AuditActor,
        correlation_id: str,
        *,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> AuditSession:
        if self.get_session(session_id) is not None:
            raise ValueError(f"audit session already exists: {session_id}")
        session = AuditSession(
            session_id=session_id,
            actor=actor,
            correlation_id=correlation_id,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.validator.validate_session(session)
        self.sessions.append(session)
        self.sessions.sort(key=lambda item: item.session_id)
        return session

    def get_session(self, session_id: str) -> AuditSession | None:
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        return None

    def close_session(self, session_id: str) -> AuditSession:
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"audit session not found: {session_id}")
        session.close()
        self.validator.validate_session(session)
        return session

    def record_event(self, event: AuditEvent, *, session_id: str = "") -> AuditEntry:
        if self.get_entry_by_event_id(event.event_id) is not None:
            raise ValueError(f"audit event already exists: {event.event_id}")
        if session_id and self.get_session(session_id) is None:
            raise ValueError(f"audit session not found: {session_id}")
        entry = AuditEntry(
            entry_id=f"audit-entry:{event.event_id}",
            event=event,
            session_id=session_id,
            child_event_ids=self._child_event_ids_for(event.event_id),
        )
        self.validator.validate_entry(entry)
        self.entries.append(entry)
        self._refresh_parent_children(event)
        self.entries.sort(key=lambda item: (item.event.occurred_at, item.entry_id))
        return entry

    def get_entry(self, entry_id: str) -> AuditEntry | None:
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def get_entry_by_event_id(self, event_id: str) -> AuditEntry | None:
        for entry in self.entries:
            if entry.event.event_id == event_id:
                return entry
        return None

    def list_entries(self) -> list[AuditEntry]:
        return list(self.entries)

    def query(self, audit_filter: AuditFilter | None = None) -> list[AuditEntry]:
        active_filter = audit_filter or AuditFilter()
        self.validator.validate_filter(active_filter)
        return [entry for entry in self.entries if _matches(entry, active_filter)]

    def query_by_category(self, category: AuditCategory) -> list[AuditEntry]:
        return self.query(AuditFilter(categories=[category]))

    def _child_event_ids_for(self, event_id: str) -> list[str]:
        return [
            entry.event.event_id
            for entry in self.entries
            if entry.event.parent_event_id == event_id
        ]

    def _refresh_parent_children(self, event: AuditEvent) -> None:
        if not event.parent_event_id:
            return
        parent = self.get_entry_by_event_id(event.parent_event_id)
        if parent is None:
            return
        child_ids = sorted(set(parent.child_event_ids + [event.event_id]))
        refreshed = AuditEntry(
            entry_id=parent.entry_id,
            event=parent.event,
            session_id=parent.session_id,
            child_event_ids=child_ids,
            recorded_at=parent.recorded_at,
            metadata=parent.metadata,
        )
        self.entries = [
            refreshed if entry.entry_id == parent.entry_id else entry
            for entry in self.entries
        ]


def _matches(entry: AuditEntry, audit_filter: AuditFilter) -> bool:
    event = entry.event
    if audit_filter.categories and event.category not in audit_filter.categories:
        return False
    if audit_filter.actions and event.action not in audit_filter.actions:
        return False
    if audit_filter.severities and event.severity not in audit_filter.severities:
        return False
    if audit_filter.services and event.service not in audit_filter.services:
        return False
    if audit_filter.actor_ids and event.actor.actor_id not in audit_filter.actor_ids:
        return False
    normalized_tags = {tag.lower() for tag in event.tags}
    if audit_filter.tags and not all(tag.lower() in normalized_tags for tag in audit_filter.tags):
        return False
    if audit_filter.correlation_id and event.correlation_id != audit_filter.correlation_id:
        return False
    if audit_filter.parent_event_id and event.parent_event_id != audit_filter.parent_event_id:
        return False
    if audit_filter.date_from and event.occurred_at < audit_filter.date_from:
        return False
    if audit_filter.date_to and event.occurred_at > audit_filter.date_to:
        return False
    for key, expected in audit_filter.metadata.items():
        if event.metadata.get(key) != expected:
            return False
    return True


def create_default_audit_registry() -> AuditRegistry:
    """Create an empty in-memory audit registry."""

    return AuditRegistry()
