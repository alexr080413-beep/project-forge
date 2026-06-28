from __future__ import annotations

from project_forge.forge_studio.models import User
from project_forge.forge_studio.registry import ForgeStudioRegistry


def list_users(registry: ForgeStudioRegistry) -> list[User]:
    return registry.list_users()


def get_user(registry: ForgeStudioRegistry, user_id: str) -> User | None:
    return registry.get_user(user_id)


def create_user(registry: ForgeStudioRegistry, user: User) -> User:
    registry.register_user(user)
    return user
