from __future__ import annotations

from datetime import datetime

from project_forge.forge_studio.models import Inject
from project_forge.forge_studio.registry import ForgeStudioRegistry


def list_injects(
    registry: ForgeStudioRegistry,
    exercise_id: str | None = None,
) -> list[Inject]:
    return registry.list_injects(exercise_id=exercise_id)


def get_inject(registry: ForgeStudioRegistry, inject_id: str) -> Inject | None:
    return registry.get_inject(inject_id)


def create_inject(registry: ForgeStudioRegistry, inject: Inject) -> Inject:
    registry.register_inject(inject)
    return inject


def submit_inject_for_review(registry: ForgeStudioRegistry, inject_id: str) -> Inject:
    inject = _required_inject(registry, inject_id)
    inject.submit_for_review()
    return inject


def schedule_inject(
    registry: ForgeStudioRegistry,
    inject_id: str,
    scheduled_time: datetime,
) -> Inject:
    inject = _required_inject(registry, inject_id)
    inject.schedule(scheduled_time)
    return inject


def _required_inject(registry: ForgeStudioRegistry, inject_id: str) -> Inject:
    inject = registry.get_inject(inject_id)
    if inject is None:
        raise ValueError(f"inject not found: {inject_id}")
    return inject
