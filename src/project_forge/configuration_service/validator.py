from __future__ import annotations

from .models import ConfigurationItem, ConfigurationProfile, ConfigurationResult


class ConfigurationValidator:
    """Validates configuration items, profiles, and load results."""

    def validate_item(self, item: ConfigurationItem) -> None:
        value = item.value if item.value is not None else item.default
        if item.required and _is_missing(value):
            raise ValueError(f"required configuration item is missing: {item.key}")

    def validate_items(self, items: list[ConfigurationItem]) -> None:
        identifiers = [(item.scope, item.key) for item in items]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("configuration item scope/key pairs must be unique")
        for item in items:
            self.validate_item(item)

    def validate_profile(self, profile: ConfigurationProfile) -> None:
        self.validate_items(profile.items)

    def validate_result(self, result: ConfigurationResult) -> None:
        self.validate_items(result.items)
        source_ids = [source.source_id for source in result.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("configuration source identifiers must be unique")


def _is_missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False
