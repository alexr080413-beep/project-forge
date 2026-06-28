from __future__ import annotations

from .models import (
    AutomationExecution,
    AutomationRule,
    AutomationStatus,
    EventTrigger,
    Trigger,
    TriggerType,
    WorkflowTrigger,
)


class AutomationValidator:
    """Validates automation rules, triggers, and execution history."""

    def validate_trigger(self, trigger: Trigger) -> None:
        if trigger.trigger_type is TriggerType.EVENT and not isinstance(
            trigger,
            EventTrigger,
        ):
            raise ValueError("event trigger type must use EventTrigger")
        if trigger.trigger_type is TriggerType.WORKFLOW and not isinstance(
            trigger,
            WorkflowTrigger,
        ):
            raise ValueError("workflow trigger type must use WorkflowTrigger")
        if trigger.trigger_type is TriggerType.CONDITIONAL and trigger.condition_key is None:
            raise ValueError("conditional triggers must include a condition_key")

    def validate_rule(self, rule: AutomationRule) -> None:
        trigger_ids = [trigger.identifier for trigger in rule.triggers]
        if len(trigger_ids) != len(set(trigger_ids)):
            raise ValueError("automation trigger identifiers must be unique")
        schedule_ids = [schedule.identifier for schedule in rule.schedules]
        if len(schedule_ids) != len(set(schedule_ids)):
            raise ValueError("automation schedule identifiers must be unique")
        for trigger in rule.triggers:
            self.validate_trigger(trigger)
        for execution in rule.execution_history:
            self.validate_execution(rule, execution)

    def validate_rules(self, rules: list[AutomationRule]) -> None:
        identifiers = [rule.rule_id for rule in rules]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("automation rule identifiers must be unique")
        for rule in rules:
            self.validate_rule(rule)

    def validate_execution(
        self,
        rule: AutomationRule,
        execution: AutomationExecution,
    ) -> None:
        if execution.rule_id != rule.rule_id:
            raise ValueError("execution rule_id must match automation rule")
        if execution.attempt > rule.retry_policy.max_attempts:
            raise ValueError("execution attempt exceeds retry policy")
        if execution.status is AutomationStatus.FAILED and not execution.message.strip():
            raise ValueError("failed automation executions must include a message")
