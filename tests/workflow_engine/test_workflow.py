from pathlib import Path

import pytest

from project_forge.workflow_engine import (
    Workflow,
    WorkflowExecution,
    WorkflowLoader,
    WorkflowRegistry,
    WorkflowStatus,
    WorkflowStep,
    WorkflowValidator,
    load_workflows,
)


def test_workflows_load_from_yaml() -> None:
    registry = load_workflows("config/workflows.example.yaml")

    assert len(registry.workflows) == 4
    assert registry.get_workflow("daily-intelligence-summary") is not None
    assert registry.get_workflow("breaking-news-inject").steps[1].max_attempts == 2


def test_workflow_registry_functions() -> None:
    registry = WorkflowRegistry()
    workflow = Workflow(
        identifier="custom-workflow",
        name="Custom Workflow",
        description="A custom workflow.",
        steps=[
            WorkflowStep(
                identifier="step-1",
                name="Step 1",
                action="stage_inputs",
            )
        ],
    )

    registry.register_workflow(workflow)

    assert registry.get_workflow("custom-workflow") is workflow


def test_execution_pipeline_runs_steps_sequentially() -> None:
    workflow = load_workflows("config/workflows.example.yaml").get_workflow(
        "daily-intelligence-summary"
    )
    calls: list[str] = []

    def handler(context, step):
        calls.append(step.identifier)
        return {f"{step.identifier}_complete": True}

    execution = WorkflowExecution(
        workflow=workflow,
        handlers={
            "build_current_context": handler,
            "evaluate_decisions": handler,
            "stage_inputs": handler,
        },
    ).execute()

    assert execution.status is WorkflowStatus.SUCCEEDED
    assert calls == [
        "load-current-context",
        "evaluate-decisions",
        "stage-summary-inputs",
    ]
    assert [result.status for result in execution.results] == [
        WorkflowStatus.SUCCEEDED,
        WorkflowStatus.SUCCEEDED,
        WorkflowStatus.SUCCEEDED,
    ]
    assert execution.execution_log[-1] == "workflow daily-intelligence-summary succeeded"


def test_conditional_branching_skips_step_when_condition_not_met() -> None:
    workflow = load_workflows("config/workflows.example.yaml").get_workflow(
        "breaking-news-inject"
    )

    execution = WorkflowExecution(
        workflow=workflow,
        execution_context={"inject_required": False},
    ).execute()

    assert execution.status is WorkflowStatus.SUCCEEDED
    assert execution.results[-1].step_identifier == "stage-inject-inputs"
    assert execution.results[-1].status is WorkflowStatus.SKIPPED


def test_retry_policy_retries_failed_handler() -> None:
    workflow = Workflow(
        identifier="retry-workflow",
        name="Retry Workflow",
        description="Exercises retry behavior.",
        steps=[
            WorkflowStep(
                identifier="retry-step",
                name="Retry Step",
                action="flaky",
                max_attempts=2,
            )
        ],
    )
    attempts = {"count": 0}

    def flaky(context, step):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("temporary failure")
        return {"recovered": True}

    execution = WorkflowExecution(
        workflow=workflow,
        handlers={"flaky": flaky},
    ).execute()

    assert execution.status is WorkflowStatus.SUCCEEDED
    assert execution.results[0].attempts == 2
    assert execution.execution_context["recovered"] is True


def test_dependency_failure_stops_execution() -> None:
    workflow = Workflow(
        identifier="dependency-workflow",
        name="Dependency Workflow",
        description="Exercises dependency failure behavior.",
        steps=[
            WorkflowStep(
                identifier="first",
                name="First",
                action="fail",
            ),
            WorkflowStep(
                identifier="second",
                name="Second",
                action="stage_inputs",
                dependencies=["first"],
            ),
        ],
    )

    def fail(context, step):
        raise RuntimeError("boom")

    execution = WorkflowExecution(
        workflow=workflow,
        handlers={"fail": fail},
    ).execute()

    assert execution.status is WorkflowStatus.FAILED
    assert len(execution.results) == 1
    assert execution.results[0].status is WorkflowStatus.FAILED


def test_validator_rejects_forward_dependency() -> None:
    workflow = Workflow(
        identifier="bad-workflow",
        name="Bad Workflow",
        description="Invalid workflow.",
        steps=[
            WorkflowStep(
                identifier="first",
                name="First",
                action="stage_inputs",
                dependencies=["second"],
            ),
            WorkflowStep(
                identifier="second",
                name="Second",
                action="stage_inputs",
            ),
        ],
    )

    with pytest.raises(ValueError):
        WorkflowValidator().validate_workflow(workflow)


def test_loader_rejects_missing_config(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        WorkflowLoader(tmp_path / "missing.yaml").load()
