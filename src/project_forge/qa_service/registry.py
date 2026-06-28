from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import QACheck, QAReport
from .validator import QAValidator


@dataclass(slots=True)
class QARegistry:
    """In-memory registry and execution surface for QA checks."""

    checks: list[QACheck] = field(default_factory=list)
    validator: QAValidator = field(default_factory=QAValidator)

    def __post_init__(self) -> None:
        self._validate_unique_checks()
        self.checks.sort(key=lambda check: check.identifier)

    def register_check(self, check: QACheck) -> None:
        if self.get_check(check.identifier) is not None:
            raise ValueError(f"QA check identifier already exists: {check.identifier}")
        self.checks.append(check)
        self.checks.sort(key=lambda item: item.identifier)

    def get_check(self, identifier: str) -> QACheck | None:
        for check in self.checks:
            if check.identifier == identifier:
                return check
        return None

    def run_checks(self, product: dict[str, Any]) -> QAReport:
        product_identifier = str(
            product.get("product_identifier")
            or product.get("id")
            or "unknown"
        )
        results = [check.execute(product) for check in self.checks]
        for result in results:
            self.validator.validate_result(result)
        report = QAReport(
            product_identifier=product_identifier,
            status=self.validator.aggregate_status(results),
            results=results,
        )
        self.validator.validate_report(report)
        return report

    def _validate_unique_checks(self) -> None:
        identifiers = [check.identifier for check in self.checks]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("QA check identifiers must be unique")
