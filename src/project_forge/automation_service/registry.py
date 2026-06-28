from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import (
    AutomationExecution,
    AutomationRule,
    AutomationStatus,
    EventTrigger,
    Trigger,
    TriggerType,
    WorkflowTrigger,
)
from .validator import AutomationValidator


@dataclass(slots=True)
class AutomationRegistry:
    """In-memory registry and trigger recording surface for automation rules."""

    rules: list[AutomationRule] = field(default_factory=list)
    validator: AutomationValidator = field(default_factory=AutomationValidator)

    def __post_init__(self) -> None:
        self.validator.validate_rules(self.rules)
        self.rules.sort(key=lambda rule: rule.rule_id)

    def register_rule(self, rule: AutomationRule) -> None:
        if self.get_rule(rule.rule_id) is not None:
            raise ValueError(f"automation rule identifier already exists: {rule.rule_id}")
        self.validator.validate_rule(rule)
        self.rules.append(rule)
        self.rules.sort(key=lambda item: item.rule_id)

    def get_rule(self, rule_id: str) -> AutomationRule | None:
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def list_rules(self) -> list[AutomationRule]:
        return list(self.rules)

    def enable_rule(self, rule_id: str) -> AutomationRule:
        rule = self._required_rule(rule_id)
        rule.enable()
        return rule

    def disable_rule(self, rule_id: str) -> AutomationRule:
        rule = self._required_rule(rule_id)
        rule.disable()
        return rule

    def record_manual_trigger(
        self,
        rule_id: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> AutomationExecution:
        rule = self._required_rule(rule_id)
        trigger = self._find_trigger(rule, TriggerType.MANUAL)
        if trigger is None:
            raise ValueError(f"manual trigger not found for rule: {rule_id}")
        return self._record(rule, trigger, trigger.should_fire({}), metadata=metadata)

    def record_event(
        self,
        event: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[AutomationExecution]:
        executions: list[AutomationExecution] = []
        for rule in self.rules:
            for trigger in rule.triggers:
                if isinstance(trigger, EventTrigger) and trigger.matches_event(event):
                    executions.append(self._record(rule, trigger, True, metadata=metadata))
        return executions

    def record_workflow_event(
        self,
        workflow_event: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[AutomationExecution]:
        executions: list[AutomationExecution] = []
        for rule in self.rules:
            for trigger in rule.triggers:
                if isinstance(trigger, WorkflowTrigger) and trigger.matches_workflow(
                    workflow_event
                ):
                    executions.append(self._record(rule, trigger, True, metadata=metadata))
        return executions

    def evaluate_conditional_triggers(
        self,
        context: dict[str, Any],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[AutomationExecution]:
        executions: list[AutomationExecution] = []
        for rule in self.rules:
            for trigger in rule.triggers:
                if trigger.trigger_type is TriggerType.CONDITIONAL:
                    executions.append(
                        self._record(
                            rule,
                            trigger,
                            trigger.should_fire(context),
                            metadata=metadata,
                        )
                    )
        return executions

    def _record(
        self,
        rule: AutomationRule,
        trigger: Trigger,
        should_record: bool,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> AutomationExecution:
        if not rule.enabled or not trigger.enabled or not should_record:
            status = AutomationStatus.SKIPPED
            message = "automation trigger skipped"
        else:
            status = AutomationStatus.RECORDED
            message = "automation trigger recorded; workflow execution not performed"
        execution = AutomationExecution(
            execution_id=rule.next_execution_id(),
            rule_id=rule.rule_id,
            trigger_id=trigger.identifier,
            status=status,
            message=message,
            metadata=dict(metadata or {}),
        )
        self.validator.validate_execution(rule, execution)
        rule.record_execution(execution)
        return execution

    def _required_rule(self, rule_id: str) -> AutomationRule:
        rule = self.get_rule(rule_id)
        if rule is None:
            raise ValueError(f"automation rule not found: {rule_id}")
        return rule

    def _find_trigger(
        self,
        rule: AutomationRule,
        trigger_type: TriggerType,
    ) -> Trigger | None:
        for trigger in rule.triggers:
            if trigger.trigger_type is trigger_type:
                return trigger
        return None
