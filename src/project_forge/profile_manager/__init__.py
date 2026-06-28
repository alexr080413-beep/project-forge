"""Profile Manager foundation for Project Forge."""

from .loader import ProfileLoader, load_profiles, profile_registry_from_mapping
from .models import ForgeProfile, ProfileComponent, ProfileMetadata
from .registry import ProfileRegistry
from .validator import ProfileValidator

__all__ = [
    "ForgeProfile",
    "ProfileComponent",
    "ProfileLoader",
    "ProfileMetadata",
    "ProfileRegistry",
    "ProfileValidator",
    "load_profiles",
    "profile_registry_from_mapping",
]
