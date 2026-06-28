import pytest

from project_forge.qa_service import (
    QACheck,
    QAFinding,
    QARegistry,
    QAResult,
    QASeverity,
    QAStatus,
    QAValidator,
    create_default_qa_checks,
)


def valid_product() -> dict[str, object]:
    return {
        "product_identifier": "product-1",
        "report_type": "intelligence_summary",
        "exercise_day": 2,
        "exercise_phase": "execution",
        "confidence": 0.9,
        "content": "Asteria forces remain within exercise boundaries.",
        "source_references": ["knowledge_base/README.md"],
        "training_objectives": ["Maintain shared scenario awareness"],
        "metadata": {"template_identifier": "intelligence-summary-template"},
    }


def test_qa_checks_can_be_registered() -> None:
    registry = QARegistry()
    check = create_default_qa_checks()[0]

    registry.register_check(check)

    assert registry.get_check(check.identifier) is check


def test_default_checks_pass_valid_product_metadata() -> None:
    registry = QARegistry(checks=create_default_qa_checks())

    report = registry.run_checks(valid_product())

    assert report.status is QAStatus.PASS
    assert [result.status for result in report.results] == [QAStatus.PASS] * 5
    assert report.findings == []


def test_results_include_warning_status() -> None:
    product = valid_product()
    product["confidence"] = 0.4
    registry = QARegistry(checks=create_default_qa_checks())

    report = registry.run_checks(product)

    assert report.status is QAStatus.WARNING
    warning_results = [
        result for result in report.results if result.status is QAStatus.WARNING
    ]
    assert warning_results[0].check_identifier == "low-confidence-warning"
    assert warning_results[0].findings[0].severity is QASeverity.WARNING


def test_results_include_fail_status_for_missing_fields_and_leakage() -> None:
    product = valid_product()
    product.pop("source_references")
    product.pop("exercise_day")
    product["report_type"] = ""
    product["content"] = "Russia appears in an unconverted exercise product."
    registry = QARegistry(checks=create_default_qa_checks())

    report = registry.run_checks(product)

    assert report.status is QAStatus.FAIL
    failed = [
        result.check_identifier
        for result in report.results
        if result.status is QAStatus.FAIL
    ]
    assert failed == [
        "missing-exercise-day",
        "missing-report-type",
        "missing-source-reference",
        "real-world-actor-name-detected",
    ]
    leakage = [
        finding
        for finding in report.findings
        if finding.check_identifier == "real-world-actor-name-detected"
    ][0]
    assert leakage.metadata["detected_names"] == ["Russia"]


def test_custom_check_executes_against_sample_product_metadata() -> None:
    def evaluate(product):
        if product.get("exercise_phase") == "execution":
            return QAResult(check_identifier="phase-alignment", status=QAStatus.PASS)
        return QAResult(
            check_identifier="phase-alignment",
            status=QAStatus.FAIL,
            findings=[
                QAFinding(
                    check_identifier="phase-alignment",
                    severity=QASeverity.ERROR,
                    field="exercise_phase",
                    message="Exercise phase is not aligned.",
                )
            ],
        )

    registry = QARegistry(
        checks=[
            QACheck(
                identifier="phase-alignment",
                name="Phase Alignment",
                description="Checks exercise phase alignment.",
                evaluator=evaluate,
                categories=["exercise_phase_alignment"],
            )
        ]
    )

    report = registry.run_checks(valid_product())

    assert report.status is QAStatus.PASS
    assert report.results[0].check_identifier == "phase-alignment"


def test_validator_rejects_warning_without_finding() -> None:
    with pytest.raises(ValueError):
        QAValidator().validate_result(
            QAResult(check_identifier="bad-warning", status=QAStatus.WARNING)
        )


def test_registry_rejects_duplicate_checks() -> None:
    check = create_default_qa_checks()[0]

    with pytest.raises(ValueError):
        QARegistry(checks=[check, check])
