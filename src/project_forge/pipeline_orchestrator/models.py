from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class PipelineStatus(str, Enum):
    """Lifecycle states for pipelines, executions, and stages."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class PipelineContext:
    """Shared execution context passed through ordered pipeline stages."""

    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.data, dict):
            raise ValueError("data must be a dictionary")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def update(self, values: dict[str, Any]) -> None:
        if not isinstance(values, dict):
            raise ValueError("context update values must be a dictionary")
        self.data.update(values)


StageHandler = Callable[[PipelineContext, "PipelineStage"], dict[str, Any] | None]


@dataclass(frozen=True, slots=True)
class PipelineStage:
    """A deterministic local operation in an end-to-end pipeline."""

    identifier: str
    name: str
    service: str
    handler: StageHandler = field(repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("service", self.service)
        if not callable(self.handler):
            raise ValueError("handler must be callable")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def execute(self, context: PipelineContext) -> dict[str, Any]:
        output = self.handler(context, self) or {}
        if not isinstance(output, dict):
            raise ValueError("stage handler must return a dictionary or None")
        return output


@dataclass(slots=True)
class Pipeline:
    """An ordered collection of dynamically registered pipeline stages."""

    identifier: str
    name: str
    description: str
    stages: list[PipelineStage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("name", self.name)
        _validate_non_empty("description", self.description)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")
        self._validate_unique_stages()

    @property
    def status(self) -> PipelineStatus:
        return PipelineStatus.PENDING

    def register_stage(self, stage: PipelineStage) -> None:
        if self.get_stage(stage.identifier) is not None:
            raise ValueError(f"pipeline stage identifier already exists: {stage.identifier}")
        self.stages.append(stage)

    def get_stage(self, identifier: str) -> PipelineStage | None:
        for stage in self.stages:
            if stage.identifier == identifier:
                return stage
        return None

    def _validate_unique_stages(self) -> None:
        identifiers = [stage.identifier for stage in self.stages]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("pipeline stage identifiers must be unique")


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Result for a single pipeline stage execution."""

    stage_identifier: str
    status: PipelineStatus
    message: str = ""
    output: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("stage_identifier", self.stage_identifier)
        if not isinstance(self.output, dict):
            raise ValueError("output must be a dictionary")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")


@dataclass(slots=True)
class PipelineExecution:
    """Runs a pipeline locally with ordered stages, logs, metadata, and failures."""

    pipeline: Pipeline
    context: PipelineContext = field(default_factory=PipelineContext)
    results: list[PipelineResult] = field(default_factory=list)
    execution_log: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: PipelineStatus = PipelineStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def execute(self) -> "PipelineExecution":
        if not self.pipeline.stages:
            raise ValueError("pipeline must include at least one stage")

        self.status = PipelineStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)
        self._log(f"pipeline {self.pipeline.identifier} started")

        for stage in self.pipeline.stages:
            result = self._execute_stage(stage)
            self.results.append(result)
            if result.status is PipelineStatus.FAILED:
                self.status = PipelineStatus.FAILED
                break
            self.context.update(result.output)

        if self.status is PipelineStatus.RUNNING:
            self.status = PipelineStatus.SUCCEEDED
        self.completed_at = datetime.now(timezone.utc)
        self._log(f"pipeline {self.pipeline.identifier} {self.status.value}")
        return self

    def _execute_stage(self, stage: PipelineStage) -> PipelineResult:
        self._log(f"stage {stage.identifier} started")
        input_keys = sorted(self.context.data.keys())
        try:
            output = stage.execute(self.context)
        except Exception as error:  # pragma: no cover - exact message asserted in tests
            message = str(error)
            self._log(f"stage {stage.identifier} failed: {message}")
            return PipelineResult(
                stage_identifier=stage.identifier,
                status=PipelineStatus.FAILED,
                message=message or "stage failed",
                metadata={
                    "service": stage.service,
                    "input_keys": input_keys,
                    "output_keys": [],
                },
            )

        output_keys = sorted(output.keys())
        self._log(f"stage {stage.identifier} succeeded")
        return PipelineResult(
            stage_identifier=stage.identifier,
            status=PipelineStatus.SUCCEEDED,
            message="stage succeeded",
            output=output,
            metadata={
                "service": stage.service,
                "input_keys": input_keys,
                "output_keys": output_keys,
            },
        )

    def _log(self, message: str) -> None:
        self.execution_log.append(message)


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")
