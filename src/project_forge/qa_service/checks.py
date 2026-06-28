from __future__ import annotations

from typing import Any

from .models import QACheck, QAFinding, QAResult, QASeverity, QAStatus


REAL_WORLD_ACTOR_NAMES = {"Russia", "China", "United States", "Iran", "NATO"}


def create_default_qa_checks() -> list[QACheck]:
    """Create the foundational deterministic QA checks."""

    return [
        missing_source_reference_check(),
        real_world_actor_name_detected_check(),
        missing_exercise_day_check(),
        missing_report_type_check(),
        low_confidence_warning_check(),
    ]


def missing_source_reference_check() -> QACheck:
    return QACheck(
        identifier="missing-source-reference",
        name="Missing Source Reference",
        description="Fails when no source references are attached.",
        categories=["source_traceability"],
        evaluator=_evaluate_missing_source_reference,
    )


def real_world_actor_name_detected_check() -> QACheck:
    return QACheck(
        identifier="real-world-actor-name-detected",
        name="Real-world Actor Name Detected",
        description="Fails when known real-world actor names appear in content.",
        categories=["fictional_entity_usage", "real_world_name_leakage"],
        evaluator=_evaluate_real_world_actor_name_detected,
    )


def missing_exercise_day_check() -> QACheck:
    return QACheck(
        identifier="missing-exercise-day",
        name="Missing Exercise Day",
        description="Fails when exercise_day is missing.",
        categories=["exercise_phase_alignment"],
        evaluator=_evaluate_missing_exercise_day,
    )


def missing_report_type_check() -> QACheck:
    return QACheck(
        identifier="missing-report-type",
        name="Missing Report Type",
        description="Fails when report_type is missing.",
        categories=["required_product_fields", "template_compliance"],
        evaluator=_evaluate_missing_report_type,
    )


def low_confidence_warning_check(threshold: float = 0.6) -> QACheck:
    return QACheck(
        identifier="low-confidence-warning",
        name="Low Confidence Warning",
        description="Warns when confidence is below threshold.",
        categories=[
            "scenario_consistency",
            "escalation_limits",
            "training_objective_alignment",
        ],
        evaluator=lambda product: _evaluate_low_confidence_warning(product, threshold),
        metadata={"threshold": threshold},
    )


def _evaluate_missing_source_reference(product: dict[str, Any]) -> QAResult:
    references = (
        product.get("source_references")
        or product.get("supporting_source_references")
        or []
    )
    if references:
        return _pass("missing-source-reference")
    return _fail(
        "missing-source-reference",
        "source_references",
        "Product must include at least one source reference.",
    )


def _evaluate_real_world_actor_name_detected(product: dict[str, Any]) -> QAResult:
    content = str(product.get("content", ""))
    leaked = sorted(name for name in REAL_WORLD_ACTOR_NAMES if name in content)
    if not leaked:
        return _pass("real-world-actor-name-detected")
    return QAResult(
        check_identifier="real-world-actor-name-detected",
        status=QAStatus.FAIL,
        findings=[
            QAFinding(
                check_identifier="real-world-actor-name-detected",
                severity=QASeverity.ERROR,
                field="content",
                message="Real-world actor names detected in product content.",
                metadata={"detected_names": leaked},
            )
        ],
    )


def _evaluate_missing_exercise_day(product: dict[str, Any]) -> QAResult:
    if product.get("exercise_day"):
        return _pass("missing-exercise-day")
    return _fail(
        "missing-exercise-day",
        "exercise_day",
        "Product must include an exercise day.",
    )


def _evaluate_missing_report_type(product: dict[str, Any]) -> QAResult:
    if str(product.get("report_type", "")).strip():
        return _pass("missing-report-type")
    return _fail(
        "missing-report-type",
        "report_type",
        "Product must include a report type.",
    )


def _evaluate_low_confidence_warning(
    product: dict[str, Any],
    threshold: float,
) -> QAResult:
    confidence = product.get("confidence", 1.0)
    if not isinstance(confidence, int | float):
        confidence = 0.0
    if float(confidence) >= threshold:
        return _pass("low-confidence-warning")
    return QAResult(
        check_identifier="low-confidence-warning",
        status=QAStatus.WARNING,
        findings=[
            QAFinding(
                check_identifier="low-confidence-warning",
                severity=QASeverity.WARNING,
                field="confidence",
                message="Product confidence is below QA warning threshold.",
                metadata={"confidence": float(confidence), "threshold": threshold},
            )
        ],
    )


def _pass(check_identifier: str) -> QAResult:
    return QAResult(check_identifier=check_identifier, status=QAStatus.PASS)


def _fail(check_identifier: str, field: str, message: str) -> QAResult:
    return QAResult(
        check_identifier=check_identifier,
        status=QAStatus.FAIL,
        findings=[
            QAFinding(
                check_identifier=check_identifier,
                severity=QASeverity.ERROR,
                field=field,
                message=message,
            )
        ],
    )
