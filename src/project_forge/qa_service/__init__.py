"""QA and Validation Service foundation for Project Forge."""

from .checks import (
    create_default_qa_checks,
    low_confidence_warning_check,
    missing_exercise_day_check,
    missing_report_type_check,
    missing_source_reference_check,
    real_world_actor_name_detected_check,
)
from .models import (
    QACheck,
    QAFinding,
    QAReport,
    QAResult,
    QASeverity,
    QAStatus,
)
from .registry import QARegistry
from .validator import QAValidator

__all__ = [
    "QACheck",
    "QAFinding",
    "QARegistry",
    "QAReport",
    "QAResult",
    "QASeverity",
    "QAStatus",
    "QAValidator",
    "create_default_qa_checks",
    "low_confidence_warning_check",
    "missing_exercise_day_check",
    "missing_report_type_check",
    "missing_source_reference_check",
    "real_world_actor_name_detected_check",
]
