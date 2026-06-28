from __future__ import annotations

from project_forge.forge_studio.models import AuditLog
from project_forge.forge_studio.registry import ForgeStudioRegistry


def list_audit_logs(
    registry: ForgeStudioRegistry,
    exercise_id: str | None = None,
) -> list[AuditLog]:
    return registry.list_audit_logs(exercise_id=exercise_id)


def get_audit_log(registry: ForgeStudioRegistry, log_id: str) -> AuditLog | None:
    return registry.get_audit_log(log_id)


def create_audit_log(registry: ForgeStudioRegistry, log: AuditLog) -> AuditLog:
    registry.register_audit_log(log)
    return log
