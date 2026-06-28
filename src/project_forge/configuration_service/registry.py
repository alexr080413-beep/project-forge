from __future__ import annotations

from dataclasses import dataclass, field

from .models import ConfigurationItem, ConfigurationProfile, ConfigurationScope
from .validator import ConfigurationValidator


@dataclass(slots=True)
class ConfigurationRegistry:
    """In-memory registry for resolved configuration items."""

    items: list[ConfigurationItem] = field(default_factory=list)
    profiles: list[ConfigurationProfile] = field(default_factory=list)
    validator: ConfigurationValidator = field(default_factory=ConfigurationValidator)

    def __post_init__(self) -> None:
        self.validator.validate_items(self.items)
        for profile in self.profiles:
            self.validator.validate_profile(profile)
        self.items.sort(key=lambda item: (item.scope.value, item.key))
        self.profiles.sort(key=lambda profile: profile.profile_id)

    def register_item(self, item: ConfigurationItem) -> None:
        if self.get_item(item.scope, item.key) is not None:
            raise ValueError(
                f"configuration item already exists for {item.scope.value}:{item.key}"
            )
        self.validator.validate_item(item)
        self.items.append(item)
        self.items.sort(key=lambda value: (value.scope.value, value.key))

    def register_profile(self, profile: ConfigurationProfile) -> None:
        if self.get_profile(profile.profile_id) is not None:
            raise ValueError(f"configuration profile already exists: {profile.profile_id}")
        self.validator.validate_profile(profile)
        self.profiles.append(profile)
        self.profiles.sort(key=lambda value: value.profile_id)

    def get_item(
        self,
        scope: ConfigurationScope,
        key: str,
    ) -> ConfigurationItem | None:
        for item in self.items:
            if item.scope is scope and item.key == key:
                return item
        return None

    def get_value(
        self,
        scope: ConfigurationScope,
        key: str,
        default=None,
    ):
        item = self.get_item(scope, key)
        if item is None:
            return default
        return item.value if item.value is not None else item.default

    def get_profile(self, profile_id: str) -> ConfigurationProfile | None:
        for profile in self.profiles:
            if profile.profile_id == profile_id:
                return profile
        return None

    def list_items(self) -> list[ConfigurationItem]:
        return list(self.items)

    def list_by_scope(self, scope: ConfigurationScope) -> list[ConfigurationItem]:
        return [item for item in self.items if item.scope is scope]

    def list_profiles(self) -> list[ConfigurationProfile]:
        return list(self.profiles)


def configuration_registry_from_items(
    items: list[ConfigurationItem],
    *,
    profiles: list[ConfigurationProfile] | None = None,
    validator: ConfigurationValidator | None = None,
) -> ConfigurationRegistry:
    return ConfigurationRegistry(
        items=items,
        profiles=profiles or [],
        validator=validator or ConfigurationValidator(),
    )
