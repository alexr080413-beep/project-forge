from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import (
    SecurityContext,
    SecurityDecision,
    SecurityEffect,
    SecurityPermission,
    SecurityPolicy,
    SecurityPrincipal,
    SecurityRole,
)
from .validator import SecurityValidator


@dataclass(slots=True)
class SecurityRegistry:
    """In-memory registry and evaluation surface for local RBAC decisions."""

    principals: list[SecurityPrincipal] = field(default_factory=list)
    roles: list[SecurityRole] = field(default_factory=list)
    permissions: list[SecurityPermission] = field(default_factory=list)
    policies: list[SecurityPolicy] = field(default_factory=list)
    decisions: list[SecurityDecision] = field(default_factory=list)
    validator: SecurityValidator = field(default_factory=SecurityValidator)

    def __post_init__(self) -> None:
        self.validator.validate_registry(
            principals=self.principals,
            roles=self.roles,
            permissions=self.permissions,
            policies=self.policies,
        )
        self.principals.sort(key=lambda principal: principal.principal_id)
        self.roles.sort(key=lambda role: role.role_id)
        self.permissions.sort(key=lambda permission: permission.permission_id)
        self.policies.sort(key=lambda policy: (policy.priority, policy.policy_id))

    def register_principal(self, principal: SecurityPrincipal) -> None:
        if self.get_principal(principal.principal_id) is not None:
            raise ValueError(f"security principal already exists: {principal.principal_id}")
        self.validator.validate_principal(principal, self.roles, self.permissions)
        self.principals.append(principal)
        self.principals.sort(key=lambda item: item.principal_id)

    def register_role(self, role: SecurityRole) -> None:
        if self.get_role(role.role_id) is not None:
            raise ValueError(f"security role already exists: {role.role_id}")
        self.validator.validate_role(role, self.permissions)
        self.roles.append(role)
        self.roles.sort(key=lambda item: item.role_id)

    def register_permission(self, permission: SecurityPermission) -> None:
        if self.get_permission(permission.permission_id) is not None:
            raise ValueError(f"security permission already exists: {permission.permission_id}")
        self.validator.validate_permission(permission)
        self.permissions.append(permission)
        self.permissions.sort(key=lambda item: item.permission_id)

    def register_policy(self, policy: SecurityPolicy) -> None:
        if self.get_policy(policy.policy_id) is not None:
            raise ValueError(f"security policy already exists: {policy.policy_id}")
        self.validator.validate_policy(
            policy,
            roles=self.roles,
            permissions=self.permissions,
            principals=self.principals,
        )
        self.policies.append(policy)
        self.policies.sort(key=lambda item: (item.priority, item.policy_id))

    def get_principal(self, principal_id: str) -> SecurityPrincipal | None:
        for principal in self.principals:
            if principal.principal_id == principal_id:
                return principal
        return None

    def get_role(self, role_id: str) -> SecurityRole | None:
        for role in self.roles:
            if role.role_id == role_id:
                return role
        return None

    def get_permission(self, permission_id: str) -> SecurityPermission | None:
        for permission in self.permissions:
            if permission.permission_id == permission_id:
                return permission
        return None

    def get_policy(self, policy_id: str) -> SecurityPolicy | None:
        for policy in self.policies:
            if policy.policy_id == policy_id:
                return policy
        return None

    def list_principals(self) -> list[SecurityPrincipal]:
        return list(self.principals)

    def list_roles(self) -> list[SecurityRole]:
        return list(self.roles)

    def list_permissions(self) -> list[SecurityPermission]:
        return list(self.permissions)

    def list_policies(self) -> list[SecurityPolicy]:
        return list(self.policies)

    def list_decisions(self) -> list[SecurityDecision]:
        return list(self.decisions)

    def context_for_principal(
        self,
        principal_id: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityContext:
        principal = self.get_principal(principal_id)
        if principal is None:
            raise ValueError(f"security principal not found: {principal_id}")
        roles = [self._required_role(role_id) for role_id in principal.role_ids]
        permission_ids = set(principal.permission_ids)
        for role in roles:
            permission_ids.update(role.permission_ids)
        permissions = [
            self._required_permission(permission_id)
            for permission_id in sorted(permission_ids)
        ]
        context = SecurityContext(
            principal=principal,
            roles=roles,
            permissions=permissions,
            metadata=dict(metadata or {}),
        )
        self.validator.validate_context(context)
        return context

    def evaluate(
        self,
        principal_id: str,
        action: str,
        resource: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityDecision:
        context = self.context_for_principal(principal_id, metadata=metadata)
        if not context.principal.enabled:
            return self._record_decision(
                context,
                action,
                resource,
                SecurityEffect.DENY,
                "principal is disabled",
                metadata=metadata,
            )

        matching_permissions = [
            permission
            for permission in context.permissions
            if permission.matches(action, resource)
        ]
        matching_policies = self._matching_policies(context, action, resource)
        deny_policies = [
            policy for policy in matching_policies if policy.effect is SecurityEffect.DENY
        ]
        if deny_policies:
            return self._record_decision(
                context,
                action,
                resource,
                SecurityEffect.DENY,
                "explicit deny policy matched",
                permission_ids=[permission.permission_id for permission in matching_permissions],
                policy_ids=[policy.policy_id for policy in deny_policies],
                metadata=metadata,
            )
        allow_policies = [
            policy for policy in matching_policies if policy.effect is SecurityEffect.ALLOW
        ]
        if matching_permissions:
            reason = "allow policy matched" if allow_policies else "role-based permission matched"
            return self._record_decision(
                context,
                action,
                resource,
                SecurityEffect.ALLOW,
                reason,
                permission_ids=[permission.permission_id for permission in matching_permissions],
                policy_ids=[policy.policy_id for policy in allow_policies],
                metadata=metadata,
            )
        return self._record_decision(
            context,
            action,
            resource,
            SecurityEffect.DENY,
            "no matching permission",
            policy_ids=[policy.policy_id for policy in matching_policies],
            metadata=metadata,
        )

    def _matching_policies(
        self,
        context: SecurityContext,
        action: str,
        resource: str,
    ) -> list[SecurityPolicy]:
        matching: list[SecurityPolicy] = []
        for policy in self.policies:
            if not policy.applies_to(context):
                continue
            for permission_id in policy.permission_ids:
                permission = self._required_permission(permission_id)
                if permission.matches(action, resource):
                    matching.append(policy)
                    break
        return matching

    def _record_decision(
        self,
        context: SecurityContext,
        action: str,
        resource: str,
        effect: SecurityEffect,
        reason: str,
        *,
        permission_ids: list[str] | None = None,
        policy_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityDecision:
        decision = SecurityDecision(
            decision_id=f"security-decision:{len(self.decisions) + 1}",
            principal_id=context.principal.principal_id,
            action=action,
            resource=resource,
            effect=effect,
            reason=reason,
            role_ids=context.role_ids,
            permission_ids=permission_ids or [],
            policy_ids=policy_ids or [],
            metadata=dict(metadata or {}),
        )
        self.validator.validate_decision(decision)
        self.decisions.append(decision)
        return decision

    def _required_role(self, role_id: str) -> SecurityRole:
        role = self.get_role(role_id)
        if role is None:
            raise ValueError(f"security role not found: {role_id}")
        return role

    def _required_permission(self, permission_id: str) -> SecurityPermission:
        permission = self.get_permission(permission_id)
        if permission is None:
            raise ValueError(f"security permission not found: {permission_id}")
        return permission


def create_default_security_registry(
    principals: list[SecurityPrincipal] | None = None,
) -> SecurityRegistry:
    """Create a registry with default Forge roles, permissions, and allow policies."""

    permissions = create_default_security_permissions()
    roles = create_default_security_roles()
    policies = [
        SecurityPolicy(
            policy_id=f"default-allow:{role.role_id}",
            name=f"Default allow for {role.name}",
            effect=SecurityEffect.ALLOW,
            permission_ids=list(role.permission_ids),
            role_ids=[role.role_id],
            priority=100,
            metadata={"default": True},
        )
        for role in roles
    ]
    return SecurityRegistry(
        principals=principals or [],
        roles=roles,
        permissions=permissions,
        policies=policies,
    )


def create_default_security_permissions() -> list[SecurityPermission]:
    """Create default local permissions for foundational Forge roles."""

    return [
        SecurityPermission(
            permission_id="platform:all",
            name="Platform Administration",
            action="*",
            resource="*",
        ),
        SecurityPermission(
            permission_id="exercise:direct",
            name="Direct Exercise",
            action="direct",
            resource="exercise",
        ),
        SecurityPermission(
            permission_id="excon:control",
            name="Control EXCON Activity",
            action="control",
            resource="excon",
        ),
        SecurityPermission(
            permission_id="intelligence:control",
            name="Control Intelligence Products",
            action="control",
            resource="intelligence",
        ),
        SecurityPermission(
            permission_id="media:control",
            name="Control Media Products",
            action="control",
            resource="media",
        ),
        SecurityPermission(
            permission_id="product:review",
            name="Review Products",
            action="review",
            resource="product",
        ),
        SecurityPermission(
            permission_id="product:view",
            name="View Products",
            action="view",
            resource="product",
        ),
        SecurityPermission(
            permission_id="system:operate",
            name="Operate System Services",
            action="operate",
            resource="system",
        ),
    ]


def create_default_security_roles() -> list[SecurityRole]:
    """Create the required default Project Forge security roles."""

    return [
        SecurityRole(
            role_id="administrator",
            name="Administrator",
            permission_ids=["platform:all"],
        ),
        SecurityRole(
            role_id="exercise_director",
            name="Exercise Director",
            permission_ids=[
                "exercise:direct",
                "excon:control",
                "product:review",
                "product:view",
            ],
        ),
        SecurityRole(
            role_id="excon_controller",
            name="EXCON Controller",
            permission_ids=["excon:control", "product:review", "product:view"],
        ),
        SecurityRole(
            role_id="intelligence_controller",
            name="Intelligence Controller",
            permission_ids=["intelligence:control", "product:review", "product:view"],
        ),
        SecurityRole(
            role_id="media_controller",
            name="Media Controller",
            permission_ids=["media:control", "product:review", "product:view"],
        ),
        SecurityRole(
            role_id="reviewer",
            name="Reviewer",
            permission_ids=["product:review", "product:view"],
        ),
        SecurityRole(
            role_id="viewer",
            name="Viewer",
            permission_ids=["product:view"],
        ),
        SecurityRole(
            role_id="system",
            name="System",
            permission_ids=["platform:all", "system:operate"],
        ),
    ]
