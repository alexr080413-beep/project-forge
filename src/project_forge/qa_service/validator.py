from __future__ import annotations

from .models import QAReport, QAResult, QASeverity, QAStatus


class QAValidator:
    """Validates QA results and aggregates reports."""

    def validate_result(self, result: QAResult) -> None:
        if result.status is QAStatus.FAIL and not result.findings:
            raise ValueError("failed QA results must include findings")
        if result.status is QAStatus.WARNING and not result.findings:
            raise ValueError("warning QA results must include findings")
        for finding in result.findings:
            if result.status is QAStatus.FAIL and finding.severity is QASeverity.INFO:
                raise ValueError("failed QA findings must be warning or error severity")

    def aggregate_status(self, results: list[QAResult]) -> QAStatus:
        if any(result.status is QAStatus.FAIL for result in results):
            return QAStatus.FAIL
        if any(result.status is QAStatus.WARNING for result in results):
            return QAStatus.WARNING
        return QAStatus.PASS

    def validate_report(self, report: QAReport) -> None:
        expected = self.aggregate_status(report.results)
        if report.status is not expected:
            raise ValueError("QA report status does not match result aggregate status")
        for result in report.results:
            self.validate_result(result)
