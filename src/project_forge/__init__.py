"""Project Forge package.

The package now includes a minimal typed model layer for the core domain
concepts used by Forge Alpha.
"""

from .models import (
    ExerciseContext,
    GeneratedReport,
    QualityCheckResult,
    ReportRequest,
    ReviewStatus,
    ScenarioActor,
    ScenarioLocation,
    ScenarioMapping,
    SourceItem,
    TrainingObjective,
)

__all__: list[str] = [
    "ExerciseContext",
    "GeneratedReport",
    "QualityCheckResult",
    "ReportRequest",
    "ReviewStatus",
    "ScenarioActor",
    "ScenarioLocation",
    "ScenarioMapping",
    "SourceItem",
    "TrainingObjective",
]
