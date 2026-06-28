from __future__ import annotations

from dataclasses import dataclass, field

from .models import Scenario, ScenarioStatus
from .validator import ScenarioValidator


@dataclass(slots=True)
class ScenarioRegistry:
    """In-memory registry for validated scenarios."""

    scenarios: list[Scenario] = field(default_factory=list)
    validator: ScenarioValidator = field(default_factory=ScenarioValidator)

    def __post_init__(self) -> None:
        self.validator.validate_scenarios(self.scenarios)

    def get_scenario(self, identifier: str) -> Scenario | None:
        for scenario in self.scenarios:
            if scenario.identifier == identifier:
                return scenario
        return None

    def get_current_scenario(self) -> Scenario | None:
        for scenario in self.scenarios:
            if scenario.status is ScenarioStatus.CURRENT:
                return scenario
        return self.scenarios[0] if self.scenarios else None

    def add_scenario(self, scenario: Scenario) -> None:
        self.validator.validate_scenario(scenario)
        if self.get_scenario(scenario.identifier) is not None:
            raise ValueError(f"scenario identifier already exists: {scenario.identifier}")
        has_current = any(
            existing.status is ScenarioStatus.CURRENT for existing in self.scenarios
        )
        if scenario.status is ScenarioStatus.CURRENT and has_current:
            raise ValueError("only one scenario can have current status")
        self.scenarios.append(scenario)
