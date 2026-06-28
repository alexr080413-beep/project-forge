from __future__ import annotations

from .models import (
    AutomationRule,
    EventTrigger,
    RetryPolicy,
    Schedule,
    TriggerType,
    WorkflowTrigger,
    conditional_trigger,
    manual_trigger,
)


def create_sample_automation_rules() -> list[AutomationRule]:
    """Create safe local automation rule examples."""

    return [
        AutomationRule(
            rule_id="daily-intelligence-summary",
            name="Daily Intelligence Summary Automation",
            description="Records the daily summary workflow trigger.",
            workflow_identifier="daily-intelligence-summary",
            schedules=[
                Schedule(
                    identifier="daily-0600",
                    cron_expression="0 6 * * *",
                )
            ],
            triggers=[manual_trigger()],
            retry_policy=RetryPolicy(max_attempts=2, retry_delay_seconds=60),
            metadata={"notional": True},
        ),
        AutomationRule(
            rule_id="breaking-news-inject",
            name="Breaking News Inject Automation",
            description="Records event-driven inject workflow triggers.",
            workflow_identifier="breaking-news-inject",
            triggers=[
                EventTrigger(
                    identifier="breaking-news-event",
                    trigger_type=TriggerType.EVENT,
                    event_type="breaking_news",
                    source="event_engine",
                ),
                conditional_trigger(
                    "inject-required",
                    condition_key="inject_required",
                    condition_equals=True,
                ),
            ],
            retry_policy=RetryPolicy(max_attempts=1),
            metadata={"notional": True},
        ),
        AutomationRule(
            rule_id="post-review-distribution",
            name="Post-Review Distribution Automation",
            description="Records workflow completion triggers after review.",
            workflow_identifier="distribution-prep",
            triggers=[
                WorkflowTrigger(
                    identifier="review-approved",
                    trigger_type=TriggerType.WORKFLOW,
                    workflow_identifier="review-queue",
                    workflow_status="approved",
                )
            ],
            retry_policy=RetryPolicy(max_attempts=1),
            metadata={"notional": True},
        ),
    ]
