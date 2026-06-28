from project_forge.demo_pipeline import create_end_to_end_demo_pipeline, run_demo_pipeline
from project_forge.distribution_service import DistributionStatus
from project_forge.integration_service import IntegrationStatus
from project_forge.pipeline_orchestrator import PipelineStatus
from project_forge.qa_service import QAStatus
from project_forge.review_queue import ReviewStatus
from project_forge.storage_service import StorageStatus


def test_end_to_end_demo_pipeline_executes_all_requested_services() -> None:
    execution = run_demo_pipeline()

    assert execution.status is PipelineStatus.SUCCEEDED
    assert [result.stage_identifier for result in execution.results] == [
        "sample-real-world-event",
        "integration-dry-run",
        "storage",
        "knowledge-lookup",
        "scenario-lookup",
        "entity-lookup",
        "event-creation",
        "decision-engine",
        "context-engine",
        "translation-engine",
        "ai-reasoning-stub",
        "product-sdk",
        "qa-service",
        "review-queue",
        "distribution-dry-run",
        "audit-log",
        "metrics-snapshot",
    ]
    assert all(result.status is PipelineStatus.SUCCEEDED for result in execution.results)

    data = execution.context.data
    assert data["integration_result"].status is IntegrationStatus.DRY_RUN
    assert data["storage_result"].status is StorageStatus.DRY_RUN
    assert data["knowledge_document"].relative_path.as_posix() == "README.md"
    assert data["scenario"].identifier == "scenario-forge-example"
    assert data["entity"].identifier == "unit-jtf-hq"
    assert data["exercise_event"].identifier == "demo-real-world-event-001"
    assert data["decision_result"].passed
    assert data["context_snapshot"].identifier == "event:demo-real-world-event-001"
    assert data["translation_result"].applied_rule_identifiers
    assert data["ai_response"].metadata == {"offline": True}
    assert data["product_output"].product_identifier == "intelligence-summary"
    assert data["qa_report"].status is QAStatus.PASS
    assert data["review_item"].status is ReviewStatus.APPROVED
    assert data["distribution_result"].status is DistributionStatus.DRY_RUN
    assert len(data["audit_entries"]) == 15
    assert data["metrics_report"].summary["workflow-executions"] == 1
    assert data["metrics_report"].summary["products-generated"] == 1
    assert data["metrics_report"].summary["distribution-events"] == 1


def test_demo_pipeline_factory_is_deterministic() -> None:
    pipeline = create_end_to_end_demo_pipeline()

    assert pipeline.identifier == "forge-core-demo"
    assert len(pipeline.stages) == 17
    assert pipeline.metadata == {"demo": True, "external_calls": False}
