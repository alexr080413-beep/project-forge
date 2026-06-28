from __future__ import annotations

from .models import AuditAction, AuditCategory, AuditEntry, AuditEvent, AuditFilter, AuditSession


ACTION_CATEGORY_MAP: dict[AuditAction, AuditCategory] = {
    AuditAction.SERVICE_EXECUTION: AuditCategory.SERVICE,
    AuditAction.WORKFLOW_EXECUTION: AuditCategory.WORKFLOW,
    AuditAction.REVIEW_ACTION: AuditCategory.REVIEW,
    AuditAction.APPROVAL: AuditCategory.APPROVAL,
    AuditAction.REJECTION: AuditCategory.REVIEW,
    AuditAction.CONFIGURATION_CHANGE: AuditCategory.CONFIGURATION,
    AuditAction.PROFILE_SELECTION: AuditCategory.PROFILE,
    AuditAction.AI_REQUEST: AuditCategory.AI,
    AuditAction.PRODUCT_GENERATION: AuditCategory.PRODUCT,
    AuditAction.DISTRIBUTION: AuditCategory.DISTRIBUTION,
    AuditAction.AUTOMATION_EXECUTION: AuditCategory.AUTOMATION,
}


class AuditValidator:
    """Validates audit sessions, events, entries, and filters."""

    def validate_event(self, event: AuditEvent) -> None:
        expected = ACTION_CATEGORY_MAP[event.action]
        if event.category is not expected:
            raise ValueError(
                f"audit action {event.action.value} must use category {expected.value}"
            )
        if event.action in {
            AuditAction.SERVICE_EXECUTION,
            AuditAction.WORKFLOW_EXECUTION,
            AuditAction.AI_REQUEST,
            AuditAction.PRODUCT_GENERATION,
            AuditAction.DISTRIBUTION,
            AuditAction.AUTOMATION_EXECUTION,
        } and not event.service.strip():
            raise ValueError("service must be provided for service-oriented audit actions")
        if event.action is AuditAction.AI_REQUEST:
            forbidden = {"prompt", "response", "completion", "content"}
            if forbidden & set(event.metadata):
                raise ValueError("AI audit events may store metadata only, not prompt or response content")

    def validate_entry(self, entry: AuditEntry) -> None:
        self.validate_event(entry.event)
        if entry.recorded_at < entry.event.occurred_at:
            raise ValueError("recorded_at must not be before occurred_at")

    def validate_session(self, session: AuditSession) -> None:
        if session.ended_at and session.ended_at < session.started_at:
            raise ValueError("ended_at must not be before started_at")

    def validate_filter(self, audit_filter: AuditFilter) -> None:
        if audit_filter.date_from and audit_filter.date_to:
            if audit_filter.date_from > audit_filter.date_to:
                raise ValueError("date_from must be before or equal to date_to")

    def validate_entries(self, entries: list[AuditEntry]) -> None:
        identifiers = [entry.entry_id for entry in entries]
        event_ids = [entry.event.event_id for entry in entries]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("audit entry identifiers must be unique")
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("audit event identifiers must be unique")
        for entry in entries:
            self.validate_entry(entry)
