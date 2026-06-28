from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class WorkflowStatus(str, Enum):
    """Lifecycle states for workflow execution and steps."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


StepHandler = Callable[[dict[str, Any], "WorkflowStep"], dict[str, Any] | None]


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """A single orchestrated workflow operation."""

    identifier: str
    name: str
    action: str
    dependencies: list[str] = field(default_factory=list)
    condition_key: str | None = None
    condition_equals: Any | None = None
    max_attempts: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("action", self.action)
        _validate_str_list("dependencies", self.dependencies)
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be greater than zero")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def should_run(self, execution_context: dict[str, Any]) -> bool:
        if self.condition_key is None:
            return True
        return execution_context.get(self.condition_key) == self.condition_equals


@dataclass(frozen=True, slots=True)
class Workflow:
    """A workflow definition composed of ordered steps."""

    identifier: str
    name: str
    description: str
    steps: list[WorkflowStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("description", self.description)
        if not self.steps:
            raise ValueError("workflow must include at least one step")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    """Result for one workflow step."""

    step_identifier: str
    status: WorkflowStatus
    attempts: int
    message: str = ""
    output: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("step_identifier", self.step_identifier)
        if self.attempts < 0:
            raise ValueError("attempts must be greater than or equal to zero")
        if not isinstance(self.output, dict):
            raise ValueError("output must be a dictionary")


@dataclass(slots=True)
class WorkflowExecution:
    """Executes a workflow with local registered handlers only."""

    workflow: Workflow
    execution_context: dict[str, Any] = field(default_factory=dict)
    handlers: dict[str, StepHandler] = field(default_factory=dict)
    results: list[WorkflowResult] = field(default_factory=list)
    execution_log: list[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def execute(self) -> "WorkflowExecution":
        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)
        self._log(f"workflow {self.workflow.identifier} started")
        completed_steps: set[str] = set()

        for step in self.workflow.steps:
            if not step.should_run(self.execution_context):
                result = WorkflowResult(
                    step_identifier=step.identifier,
                    status=WorkflowStatus.SKIPPED,
                    attempts=0,
                    message="condition not met",
                )
                self.results.append(result)
                self._log(f"step {step.identifier} skipped")
                continue

            missing = sorted(set(step.dependencies) - completed_steps)
            if missing:
                result = WorkflowResult(
                    step_identifier=step.identifier,
                    status=WorkflowStatus.FAILED,
                    attempts=0,
                    message=f"missing dependencies: {', '.join(missing)}",
                )
                self.results.append(result)
                self.status = WorkflowStatus.FAILED
                self._log(f"step {step.identifier} failed dependency check")
                break

            result = self._execute_step(step)
            self.results.append(result)
            if result.status is WorkflowStatus.SUCCEEDED:
                completed_steps.add(step.identifier)
                self.execution_context.update(result.output)
            else:
                self.status = WorkflowStatus.FAILED
                break

        if self.status is WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.SUCCEEDED
        self.completed_at = datetime.now(timezone.utc)
        self._log(f"workflow {self.workflow.identifier} {self.status.value}")
        return self

    def _execute_step(self, step: WorkflowStep) -> WorkflowResult:
        handler = self.handlers.get(step.action, _default_handler)
        attempts = 0
        last_error = ""
        while attempts < step.max_attempts:
            attempts += 1
            self._log(f"step {step.identifier} attempt {attempts}")
            try:
                output = handler(dict(self.execution_context), step) or {}
            except Exception as error:  # pragma: no cover - message asserted in tests
                last_error = str(error)
                self._log(f"step {step.identifier} failed: {last_error}")
                continue
            return WorkflowResult(
                step_identifier=step.identifier,
                status=WorkflowStatus.SUCCEEDED,
                attempts=attempts,
                message="step succeeded",
                output=output,
            )

        return WorkflowResult(
            step_identifier=step.identifier,
            status=WorkflowStatus.FAILED,
            attempts=attempts,
            message=last_error or "step failed",
        )

    def _log(self, message: str) -> None:
        self.execution_log.append(message)


def _default_handler(
    execution_context: dict[str, Any],
    step: WorkflowStep,
) -> dict[str, Any]:
    return {step.identifier: True}


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"{name} must be a list of strings")
