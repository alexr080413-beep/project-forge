import pytest

from project_forge.automation_service import (
    AutomationExecution,
    AutomationRegistry,
    AutomationRule,
    AutomationStatus,
    AutomationValidator,
    EventTrigger,
    RetryPolicy,
    Schedule,
    Trigger,
    TriggerType,
    WorkflowTrigger,
    conditional_trigger,
    create_sample_automation_rules,
    manual_trigger,
)


def test_rules_register() -> None:
    rule = AutomationRule(
        rule_id="manual-rule",
        name="Manual Rule",
        workflow_identifier="daily-intelligence-summary",
        triggers=[manual_trigger()],
    )
    registry = AutomationRegistry()

    registry.register_rule(rule)

    assert registry.get_rule("manual-rule") is rule


def test_cron_schedule_validates_five_fields() -> None:
    schedule = Schedule(identifier="daily", cron_expression="0 6 * * *")

    assert schedule.cron_expression == "0 6 * * *"

    with pytest.raises(ValueError):
        Schedule(identifier="bad", cron_expression="0 6 *")


def test_event_trigger_validates_and_matches_event_payload() -> None:
    trigger = EventTrigger(
        identifier="event",
        trigger_type=TriggerType.EVENT,
        event_type="breaking_news",
        source="event_engine",
    )

    assert trigger.matches_event(
        {"event_type": "breaking_news", "source": "event_engine"}
    )
    assert not trigger.matches_event(
        {"event_type": "routine_update", "source": "event_engine"}
    )


def test_workflow_trigger_validates_and_matches_workflow_event() -> None:
    trigger = WorkflowTrigger(
        identifier="workflow",
        trigger_type=TriggerType.WORKFLOW,
        workflow_identifier="review-queue",
        workflow_status="approved",
    )

    assert trigger.matches_workflow(
        {"workflow_identifier": "review-queue", "status": "approved"}
    )
    assert not trigger.matches_workflow(
        {"workflow_identifier": "review-queue", "status": "rejected"}
    )


def test_conditional_trigger_records_only_when_condition_matches() -> None:
    rule = AutomationRule(
        rule_id="conditional-rule",
        name="Conditional Rule",
        workflow_identifier="breaking-news-inject",
        triggers=[
            conditional_trigger(
                "inject-required",
                condition_key="inject_required",
                condition_equals=True,
            )
        ],
    )
    registry = AutomationRegistry(rules=[rule])

    skipped = registry.evaluate_conditional_triggers({"inject_required": False})[0]
    recorded = registry.evaluate_conditional_triggers({"inject_required": True})[0]

    assert skipped.status is AutomationStatus.SKIPPED
    assert recorded.status is AutomationStatus.RECORDED
    assert len(rule.execution_history) == 2


def test_manual_trigger_records_history_without_workflow_execution() -> None:
    rule = AutomationRule(
        rule_id="manual-rule",
        name="Manual Rule",
        workflow_identifier="daily-intelligence-summary",
        triggers=[manual_trigger()],
    )
    registry = AutomationRegistry(rules=[rule])

    execution = registry.record_manual_trigger("manual-rule")

    assert execution.status is AutomationStatus.RECORDED
    assert execution.message == "automation trigger recorded; workflow execution not performed"
    assert rule.execution_history == [execution]


def test_event_trigger_records_matching_rules() -> None:
    rule = AutomationRule(
        rule_id="event-rule",
        name="Event Rule",
        workflow_identifier="breaking-news-inject",
        triggers=[
            EventTrigger(
                identifier="breaking-news",
                trigger_type=TriggerType.EVENT,
                event_type="breaking_news",
            )
        ],
    )
    registry = AutomationRegistry(rules=[rule])

    executions = registry.record_event({"event_type": "breaking_news"})

    assert len(executions) == 1
    assert executions[0].trigger_id == "breaking-news"
    assert executions[0].status is AutomationStatus.RECORDED


def test_disabled_rule_skips_trigger_recording() -> None:
    rule = AutomationRule(
        rule_id="disabled-rule",
        name="Disabled Rule",
        workflow_identifier="daily-intelligence-summary",
        enabled=False,
        triggers=[manual_trigger()],
    )
    registry = AutomationRegistry(rules=[rule])

    execution = registry.record_manual_trigger("disabled-rule")

    assert execution.status is AutomationStatus.SKIPPED


def test_retry_policy_limits_execution_attempts() -> None:
    rule = AutomationRule(
        rule_id="retry-rule",
        name="Retry Rule",
        workflow_identifier="daily-intelligence-summary",
        triggers=[manual_trigger()],
        retry_policy=RetryPolicy(max_attempts=1),
    )
    execution = AutomationExecution(
        execution_id="retry-rule:2",
        rule_id="retry-rule",
        trigger_id="manual",
        status=AutomationStatus.FAILED,
        attempt=2,
        message="failed",
    )

    with pytest.raises(ValueError):
        AutomationValidator().validate_execution(rule, execution)


def test_validator_rejects_mismatched_trigger_classes() -> None:
    trigger = Trigger(identifier="bad", trigger_type=TriggerType.EVENT)

    with pytest.raises(ValueError):
        AutomationValidator().validate_trigger(trigger)


def test_duplicate_rules_are_rejected() -> None:
    rule = AutomationRule(
        rule_id="duplicate",
        name="Duplicate",
        workflow_identifier="daily-intelligence-summary",
        triggers=[manual_trigger()],
    )

    with pytest.raises(ValueError):
        AutomationRegistry(rules=[rule, rule])


def test_sample_rules_cover_schedule_event_conditional_and_workflow_triggers() -> None:
    registry = AutomationRegistry(rules=create_sample_automation_rules())

    assert [rule.rule_id for rule in registry.list_rules()] == [
        "breaking-news-inject",
        "daily-intelligence-summary",
        "post-review-distribution",
    ]
    assert registry.get_rule("daily-intelligence-summary").schedules[0].cron_expression == (
        "0 6 * * *"
    )
