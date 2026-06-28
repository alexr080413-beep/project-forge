from __future__ import annotations

from dataclasses import dataclass, field

from .models import ForgeProfile
from .validator import ProfileValidator


@dataclass(slots=True)
class ProfileRegistry:
    """In-memory registry for validated Forge profiles."""

    profiles: list[ForgeProfile] = field(default_factory=list)
    validator: ProfileValidator = field(default_factory=ProfileValidator)

    def __post_init__(self) -> None:
        self.validator.validate_profiles(self.profiles)
        self.profiles.sort(key=lambda profile: profile.profile_id)

    def register_profile(self, profile: ForgeProfile) -> None:
        if self.get_profile(profile.profile_id) is not None:
            raise ValueError(f"profile identifier already exists: {profile.profile_id}")
        self.validator.validate_profile(profile)
        self.profiles.append(profile)
        self.profiles.sort(key=lambda item: item.profile_id)

    def get_profile(self, profile_id: str) -> ForgeProfile | None:
        for profile in self.profiles:
            if profile.profile_id == profile_id:
                return profile
        return None

    def list_profiles(self) -> list[ForgeProfile]:
        return list(self.profiles)
