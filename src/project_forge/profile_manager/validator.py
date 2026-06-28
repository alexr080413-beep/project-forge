from __future__ import annotations

from pathlib import Path

from .models import ForgeProfile


class ProfileValidator:
    """Validates profile definitions and local path bindings."""

    def __init__(self, path_base: str | Path = ".") -> None:
        self.path_base = Path(path_base)

    def validate_profile(self, profile: ForgeProfile) -> None:
        self._validate_non_empty_list("enabled_services", profile.enabled_services)
        self._validate_non_empty_list("enabled_plugins", profile.enabled_plugins)
        self._validate_unique_components(profile)
        self._validate_required_paths(profile)

    def validate_profiles(self, profiles: list[ForgeProfile]) -> None:
        identifiers = [profile.profile_id for profile in profiles]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("profile identifiers must be unique")
        for profile in profiles:
            self.validate_profile(profile)

    def _validate_required_paths(self, profile: ForgeProfile) -> None:
        for field_name, path_value in [
            ("knowledge_base_path", profile.knowledge_base_path),
            ("template_path", profile.template_path),
            ("translation_dictionary_path", profile.translation_dictionary_path),
            ("workflow_path", profile.workflow_path),
        ]:
            resolved = self._resolve_path(path_value)
            if not resolved.exists():
                raise FileNotFoundError(f"{field_name} does not exist: {resolved}")

    def _resolve_path(self, path_value: str) -> Path:
        path = Path(path_value)
        if path.is_absolute():
            return path
        return (self.path_base / path).resolve()

    def _validate_unique_components(self, profile: ForgeProfile) -> None:
        keys = [
            (component.component_type, component.identifier)
            for component in profile.components
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("profile component identifiers must be unique by type")

    def _validate_non_empty_list(self, name: str, values: list[str]) -> None:
        if not values:
            raise ValueError(f"{name} must include at least one value")
        if any(not value.strip() for value in values):
            raise ValueError(f"{name} must not contain blank values")
