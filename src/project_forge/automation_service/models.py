from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AutomationStatus(str, Enum):
    """Lifecycle states for automation executions."""

    PENDING = "pending"
    RECORDED = "recorded"
    SKIPPED = "skipped"
    FAILED = "failed"


class TriggerType(str, Enum):
    """Supported automation trigger families."""

    MANUAL = "manual"
    SCHEDULE = "schedule"
    EVENT = "event"
    WORKFLOW = "workflow"
    CONDITIONAL = "conditional"


@dataclass(frozen=True, slots=True)
class Schedule:
    """A cron-style local schedule definition."""

    identifier: str
    cron_expression: str
    timezone: str = "UTC"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        _validate_non_empty("cron_expression", self.cron_expression)
        _validate_non_empty("timezone", self.timezone)
        _validate_cron_expression(self.cron_expression)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class Trigger:
    """Base trigger definition for an automation rule."""

    identifier: str
    trigger_type: TriggerType
    enabled: bool = True
    condition_key: str | None = None
    condition_equals: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("identifier", self.identifier)
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")
        if self.condition_key is not None and not self.condition_key.strip():
            raise ValueError("condition_key must not be blank")
        _validate_metadata(self.metadata)

    def should_fire(self, context: dict[str, Any] | None = None) -> bool:
        if not self.enabled:
            return False
        if self.condition_key is None:
            return True
        return (context or {}).get(self.condition_key) == self.condition_equals


@dataclass(frozen=True, slots=True)
class EventTrigger(Trigger):
    """Trigger that matches a local event payload."""

    event_type: str = ""
    source: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.trigger_type is not TriggerType.EVENT:
            raise ValueError("event triggers must use event trigger type")
        _validate_non_empty("event_type", self.event_type)

    def matches_event(self, event: dict[str, Any]) -> bool:
        if not self.should_fire(event):
            return False
        if event.get("event_type") != self.event_type:
            return False
        if self.source and event.get("source") != self.source:
            return False
        return True


@dataclass(frozen=True, slots=True)
class WorkflowTrigger(Trigger):
    """Trigger that records workflow lifecycle events."""

    workflow_identifier: str = ""
    workflow_status: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.trigger_type is not TriggerType.WORKFLOW:
            raise ValueError("workflow triggers must use workflow trigger type")
        _validate_non_empty("workflow_identifier", self.workflow_identifier)

    def matches_workflow(self, workflow_event: dict[str, Any]) -> bool:
        if not self.should_fire(workflow_event):
            return False
        if workflow_event.get("workflow_identifier") != self.workflow_identifier:
            return False
        if self.workflow_status and workflow_event.get("status") != self.workflow_status:
            return False
        return True


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Retry settings for automation execution recording."""

    max_attempts: int = 1
    retry_delay_seconds: int = 0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be greater than zero")
        if self.retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must be greater than or equal to zero")


@dataclass(frozen=True, slots=True)
class AutomationExecution:
    """A recorded automation trigger event. It does not execute workflows."""

    execution_id: str
    rule_id: str
    trigger_id: str
    status: AutomationStatus
    attempt: int = 1
    message: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("execution_id", self.execution_id)
        _validate_non_empty("rule_id", self.rule_id)
        _validate_non_empty("trigger_id", self.trigger_id)
        if self.attempt < 1:
            raise ValueError("attempt must be greater than zero")
        _validate_metadata(self.metadata)


@dataclass(slots=True)
class AutomationRule:
    """A local automation rule composed of schedules, triggers, and retry policy."""

    rule_id: str
    name: str
    workflow_identifier: str
    description: str = ""
    enabled: bool = True
    schedules: list[Schedule] = field(default_factory=list)
    triggers: list[Trigger] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    execution_history: list[AutomationExecution] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("rule_id", self.rule_id)
        _validate_non_empty("name", self.name)
        _validate_non_empty("workflow_identifier", self.workflow_identifier)
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")
        if not self.schedules and not self.triggers:
            raise ValueError("automation rule must include at least one schedule or trigger")
        _validate_metadata(self.metadata)
        self._validate_unique_triggers()
        self._validate_unique_schedules()

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def record_execution(self, execution: AutomationExecution) -> None:
        if execution.rule_id != self.rule_id:
            raise ValueError("execution rule_id must match automation rule")
        self.execution_history.append(execution)

    def next_execution_id(self) -> str:
        return f"{self.rule_id}:{len(self.execution_history) + 1}"

    def _validate_unique_triggers(self) -> None:
        identifiers = [trigger.identifier for trigger in self.triggers]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("automation trigger identifiers must be unique")

    def _validate_unique_schedules(self) -> None:
        identifiers = [schedule.identifier for schedule in self.schedules]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("automation schedule identifiers must be unique")


def manual_trigger(identifier: str = "manual") -> Trigger:
    """Create a simple manual trigger."""

    return Trigger(identifier=identifier, trigger_type=TriggerType.MANUAL)


def conditional_trigger(
    identifier: str,
    *,
    condition_key: str,
    condition_equals: Any,
) -> Trigger:
    """Create a local conditional trigger."""

    return Trigger(
        identifier=identifier,
        trigger_type=TriggerType.CONDITIONAL,
        condition_key=condition_key,
        condition_equals=condition_equals,
    )


def _validate_cron_expression(expression: str) -> None:
    parts = expression.split()
    if len(parts) != 5:
        raise ValueError("cron_expression must contain five fields")
    for part in parts:
        if not part.strip():
            raise ValueError("cron_expression fields must not be blank")


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
