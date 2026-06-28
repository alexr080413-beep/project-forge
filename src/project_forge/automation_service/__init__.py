"""Automation Service foundation for Project Forge."""

from .examples import create_sample_automation_rules
from .models import (
    AutomationExecution,
    AutomationRule,
    AutomationStatus,
    EventTrigger,
    RetryPolicy,
    Schedule,
    Trigger,
    TriggerType,
    WorkflowTrigger,
    conditional_trigger,
    manual_trigger,
)
from .registry import AutomationRegistry
from .validator import AutomationValidator

__all__ = [
    "AutomationExecution",
    "AutomationRegistry",
    "AutomationRule",
    "AutomationStatus",
    "AutomationValidator",
    "EventTrigger",
    "RetryPolicy",
    "Schedule",
    "Trigger",
    "TriggerType",
    "WorkflowTrigger",
    "conditional_trigger",
    "create_sample_automation_rules",
    "manual_trigger",
]
