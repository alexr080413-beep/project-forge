from __future__ import annotations

from .models import Workflow


class WorkflowValidator:
    """Validates workflow definitions before registration or execution."""

    def validate_workflow(self, workflow: Workflow) -> None:
        step_ids = [step.identifier for step in workflow.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("workflow step identifiers must be unique")

        known_steps: set[str] = set()
        all_steps = set(step_ids)
        for step in workflow.steps:
            unknown = sorted(set(step.dependencies) - all_steps)
            if unknown:
                raise ValueError(f"step references unknown dependencies: {unknown}")
            forward = sorted(set(step.dependencies) - known_steps)
            if forward:
                raise ValueError(f"step depends on later step: {forward}")
            known_steps.add(step.identifier)

    def validate_workflows(self, workflows: list[Workflow]) -> None:
        identifiers = [workflow.identifier for workflow in workflows]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("workflow identifiers must be unique")
        for workflow in workflows:
            self.validate_workflow(workflow)
