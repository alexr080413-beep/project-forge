from __future__ import annotations

from .models import Scenario, ScenarioStatus


class ScenarioValidator:
    """Validates scenario objects before registry use."""

    def validate_scenario(self, scenario: Scenario) -> None:
        if not scenario.active_objectives:
            raise ValueError("active_objectives must include at least one objective")
        if not scenario.active_constraints:
            raise ValueError("active_constraints must include at least one constraint")
        if not scenario.active_assumptions:
            raise ValueError("active_assumptions must include at least one assumption")
        if not scenario.active_control_measures:
            raise ValueError(
                "active_control_measures must include at least one control measure"
            )

    def validate_scenarios(self, scenarios: list[Scenario]) -> None:
        identifiers = [scenario.identifier for scenario in scenarios]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("scenario identifiers must be unique")

        current_count = sum(
            1 for scenario in scenarios if scenario.status is ScenarioStatus.CURRENT
        )
        if current_count > 1:
            raise ValueError("only one scenario can have current status")

        for scenario in scenarios:
            self.validate_scenario(scenario)
