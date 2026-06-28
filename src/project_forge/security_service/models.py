from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SecurityPrincipalType(str, Enum):
    """Supported local actor families for security decisions."""

    USER = "user"
    SERVICE_ACCOUNT = "service_account"
    SYSTEM_ACTOR = "system_actor"


class SecurityEffect(str, Enum):
    """Policy and decision effects."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True, slots=True)
class SecurityPermission:
    """A deterministic action/resource permission."""

    permission_id: str
    name: str
    action: str
    resource: str
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_identifier("permission_id", self.permission_id)
        _validate_non_empty("name", self.name)
        _validate_non_empty("action", self.action)
        _validate_non_empty("resource", self.resource)
        _validate_metadata(self.metadata)

    def matches(self, action: str, resource: str) -> bool:
        return _matches_token(self.action, action) and _matches_token(self.resource, resource)


@dataclass(frozen=True, slots=True)
class SecurityRole:
    """A role composed of permission identifiers."""

    role_id: str
    name: str
    description: str = ""
    permission_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_identifier("role_id", self.role_id)
        _validate_non_empty("name", self.name)
        _validate_str_list("permission_ids", self.permission_ids)
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class SecurityPrincipal:
    """A local user, service account, or system actor."""

    principal_id: str
    display_name: str
    principal_type: SecurityPrincipalType
    role_ids: list[str] = field(default_factory=list)
    permission_ids: list[str] = field(default_factory=list)
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_identifier("principal_id", self.principal_id)
        _validate_non_empty("display_name", self.display_name)
        _validate_str_list("role_ids", self.role_ids)
        _validate_str_list("permission_ids", self.permission_ids)
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")
        _validate_metadata(self.metadata)


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    """A local policy that can allow or deny permissions for principals or roles."""

    policy_id: str
    name: str
    effect: SecurityEffect
    permission_ids: list[str]
    description: str = ""
    principal_ids: list[str] = field(default_factory=list)
    role_ids: list[str] = field(default_factory=list)
    enabled: bool = True
    priority: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_identifier("policy_id", self.policy_id)
        _validate_non_empty("name", self.name)
        _validate_str_list("permission_ids", self.permission_ids)
        _validate_str_list("principal_ids", self.principal_ids)
        _validate_str_list("role_ids", self.role_ids)
        if not self.permission_ids:
            raise ValueError("security policy must include at least one permission")
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")
        if self.priority < 0:
            raise ValueError("priority must be greater than or equal to zero")
        _validate_metadata(self.metadata)

    def applies_to(self, context: SecurityContext) -> bool:
        if not self.enabled:
            return False
        if self.principal_ids and context.principal.principal_id not in self.principal_ids:
            return False
        if self.role_ids and not set(self.role_ids).intersection(context.role_ids):
            return False
        return True


@dataclass(frozen=True, slots=True)
class SecurityContext:
    """Resolved local security context for one principal."""

    principal: SecurityPrincipal
    roles: list[SecurityRole] = field(default_factory=list)
    permissions: list[SecurityPermission] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_metadata(self.metadata)

    @property
    def role_ids(self) -> list[str]:
        return [role.role_id for role in self.roles]

    @property
    def permission_ids(self) -> list[str]:
        return [permission.permission_id for permission in self.permissions]

    def has_permission(self, action: str, resource: str) -> bool:
        return any(permission.matches(action, resource) for permission in self.permissions)


@dataclass(frozen=True, slots=True)
class SecurityDecision:
    """Audit-ready result of a local authorization evaluation."""

    decision_id: str
    principal_id: str
    action: str
    resource: str
    effect: SecurityEffect
    reason: str
    role_ids: list[str] = field(default_factory=list)
    permission_ids: list[str] = field(default_factory=list)
    policy_ids: list[str] = field(default_factory=list)
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_non_empty("decision_id", self.decision_id)
        _validate_identifier("principal_id", self.principal_id)
        _validate_non_empty("action", self.action)
        _validate_non_empty("resource", self.resource)
        _validate_non_empty("reason", self.reason)
        _validate_str_list("role_ids", self.role_ids)
        _validate_str_list("permission_ids", self.permission_ids)
        _validate_str_list("policy_ids", self.policy_ids)
        _validate_metadata(self.metadata)

    @property
    def allowed(self) -> bool:
        return self.effect is SecurityEffect.ALLOW

    @property
    def denied(self) -> bool:
        return self.effect is SecurityEffect.DENY


def _matches_token(pattern: str, value: str) -> bool:
    normalized_pattern = pattern.strip().lower()
    normalized_value = value.strip().lower()
    return normalized_pattern == "*" or normalized_pattern == normalized_value


def _validate_identifier(name: str, value: str | None) -> None:
    _validate_non_empty(name, value)
    assert value is not None
    if any(character.isspace() for character in value):
        raise ValueError(f"{name} must not contain whitespace")


def _validate_non_empty(name: str, value: str | None) -> None:
    if value is None or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _validate_str_list(name: str, values: list[str]) -> None:
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError(f"{name} must be a list of non-empty strings")


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")
