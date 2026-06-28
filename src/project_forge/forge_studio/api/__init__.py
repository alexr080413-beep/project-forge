"""Framework-neutral Forge Studio API route scaffolding.

These modules expose route-shaped functions over the local
``ForgeStudioRegistry``. They are intentionally not bound to FastAPI or another
web framework yet, because the repository currently has no API dependency.
"""

from . import audit, exercises, injects, review, timeline, users

__all__ = ["audit", "exercises", "injects", "review", "timeline", "users"]
