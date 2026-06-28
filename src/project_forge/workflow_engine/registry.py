from __future__ import annotations

from dataclasses import dataclass, field

from .models import Workflow
from .validator import WorkflowValidator


@dataclass(slots=True)
class WorkflowRegistry:
    """In-memory registry for validated workflows."""

    workflows: list[Workflow] = field(default_factory=list)
    validator: WorkflowValidator = field(default_factory=WorkflowValidator)

    def __post_init__(self) -> None:
        self.validator.validate_workflows(self.workflows)
        self.workflows.sort(key=lambda workflow: workflow.identifier)

    def register_workflow(self, workflow: Workflow) -> None:
        if self.get_workflow(workflow.identifier) is not None:
            raise ValueError(f"workflow identifier already exists: {workflow.identifier}")
        self.validator.validate_workflow(workflow)
        self.workflows.append(workflow)
        self.workflows.sort(key=lambda item: item.identifier)

    def get_workflow(self, identifier: str) -> Workflow | None:
        for workflow in self.workflows:
            if workflow.identifier == identifier:
                return workflow
        return None
