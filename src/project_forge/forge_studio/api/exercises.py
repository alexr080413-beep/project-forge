from __future__ import annotations

from project_forge.forge_studio.models import Exercise, ExercisePhase, ExerciseStatus
from project_forge.forge_studio.registry import ForgeStudioRegistry


def list_exercises(registry: ForgeStudioRegistry) -> list[Exercise]:
    return registry.list_exercises()


def get_exercise(registry: ForgeStudioRegistry, exercise_id: str) -> Exercise | None:
    return registry.get_exercise(exercise_id)


def create_exercise(registry: ForgeStudioRegistry, exercise: Exercise) -> Exercise:
    registry.register_exercise(exercise)
    return exercise


def update_exercise_status(
    registry: ForgeStudioRegistry,
    exercise_id: str,
    status: ExerciseStatus,
) -> Exercise:
    exercise = _required_exercise(registry, exercise_id)
    exercise.transition_status(status)
    return exercise


def update_exercise_phase(
    registry: ForgeStudioRegistry,
    exercise_id: str,
    phase: ExercisePhase,
) -> Exercise:
    exercise = _required_exercise(registry, exercise_id)
    exercise.transition_phase(phase)
    return exercise


def _required_exercise(registry: ForgeStudioRegistry, exercise_id: str) -> Exercise:
    exercise = registry.get_exercise(exercise_id)
    if exercise is None:
        raise ValueError(f"exercise not found: {exercise_id}")
    return exercise
