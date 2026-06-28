from __future__ import annotations

from dataclasses import dataclass, field

from .models import Pipeline, PipelineExecution, PipelineStage


@dataclass(slots=True)
class PipelineRegistry:
    """In-memory registry for pipelines and reusable stage definitions."""

    pipelines: list[Pipeline] = field(default_factory=list)
    stages: list[PipelineStage] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_unique_pipelines()
        self._validate_unique_stages()
        self.pipelines.sort(key=lambda pipeline: pipeline.identifier)
        self.stages.sort(key=lambda stage: stage.identifier)

    def register_pipeline(self, pipeline: Pipeline) -> None:
        if self.get_pipeline(pipeline.identifier) is not None:
            raise ValueError(f"pipeline identifier already exists: {pipeline.identifier}")
        self.pipelines.append(pipeline)
        self.pipelines.sort(key=lambda item: item.identifier)

    def get_pipeline(self, identifier: str) -> Pipeline | None:
        for pipeline in self.pipelines:
            if pipeline.identifier == identifier:
                return pipeline
        return None

    def register_stage(self, stage: PipelineStage) -> None:
        if self.get_stage(stage.identifier) is not None:
            raise ValueError(f"pipeline stage identifier already exists: {stage.identifier}")
        self.stages.append(stage)
        self.stages.sort(key=lambda item: item.identifier)

    def get_stage(self, identifier: str) -> PipelineStage | None:
        for stage in self.stages:
            if stage.identifier == identifier:
                return stage
        return None

    def execute_pipeline(self, identifier: str) -> PipelineExecution:
        pipeline = self.get_pipeline(identifier)
        if pipeline is None:
            raise ValueError(f"pipeline not found: {identifier}")
        return PipelineExecution(pipeline=pipeline).execute()

    def _validate_unique_pipelines(self) -> None:
        identifiers = [pipeline.identifier for pipeline in self.pipelines]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("pipeline identifiers must be unique")

    def _validate_unique_stages(self) -> None:
        identifiers = [stage.identifier for stage in self.stages]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("pipeline stage identifiers must be unique")
