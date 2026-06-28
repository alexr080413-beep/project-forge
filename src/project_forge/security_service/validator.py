from __future__ import annotations

from .models import (
    SecurityContext,
    SecurityDecision,
    SecurityEffect,
    SecurityPermission,
    SecurityPolicy,
    SecurityPrincipal,
    SecurityRole,
)


class SecurityValidator:
    """Validates local security roles, permissions, policies, and decisions."""

    def validate_permission(self, permission: SecurityPermission) -> None:
        if permission.action != "*" and ":" in permission.action:
            raise ValueError("permission action must not include resource separators")

    def validate_role(
        self,
        role: SecurityRole,
        permissions: list[SecurityPermission] | None = None,
    ) -> None:
        _validate_unique_values("role permission identifiers", role.permission_ids)
        if permissions is not None:
            permission_ids = {permission.permission_id for permission in permissions}
            missing = sorted(set(role.permission_ids) - permission_ids)
            if missing:
                raise ValueError(f"role references unknown permissions: {', '.join(missing)}")

    def validate_principal(
        self,
        principal: SecurityPrincipal,
        roles: list[SecurityRole] | None = None,
        permissions: list[SecurityPermission] | None = None,
    ) -> None:
        _validate_unique_values("principal role identifiers", principal.role_ids)
        _validate_unique_values("principal permission identifiers", principal.permission_ids)
        if roles is not None:
            role_ids = {role.role_id for role in roles}
            missing = sorted(set(principal.role_ids) - role_ids)
            if missing:
                raise ValueError(f"principal references unknown roles: {', '.join(missing)}")
        if permissions is not None:
            permission_ids = {permission.permission_id for permission in permissions}
            missing = sorted(set(principal.permission_ids) - permission_ids)
            if missing:
                raise ValueError(f"principal references unknown permissions: {', '.join(missing)}")

    def validate_policy(
        self,
        policy: SecurityPolicy,
        *,
        roles: list[SecurityRole] | None = None,
        permissions: list[SecurityPermission] | None = None,
        principals: list[SecurityPrincipal] | None = None,
    ) -> None:
        _validate_unique_values("policy permission identifiers", policy.permission_ids)
        _validate_unique_values("policy role identifiers", policy.role_ids)
        _validate_unique_values("policy principal identifiers", policy.principal_ids)
        if permissions is not None:
            permission_ids = {permission.permission_id for permission in permissions}
            missing = sorted(set(policy.permission_ids) - permission_ids)
            if missing:
                raise ValueError(f"policy references unknown permissions: {', '.join(missing)}")
        if roles is not None:
            role_ids = {role.role_id for role in roles}
            missing = sorted(set(policy.role_ids) - role_ids)
            if missing:
                raise ValueError(f"policy references unknown roles: {', '.join(missing)}")
        if principals is not None:
            principal_ids = {principal.principal_id for principal in principals}
            missing = sorted(set(policy.principal_ids) - principal_ids)
            if missing:
                raise ValueError(f"policy references unknown principals: {', '.join(missing)}")

    def validate_context(self, context: SecurityContext) -> None:
        principal_role_ids = set(context.principal.role_ids)
        context_role_ids = {role.role_id for role in context.roles}
        if not principal_role_ids.issubset(context_role_ids):
            missing = sorted(principal_role_ids - context_role_ids)
            raise ValueError(f"security context missing principal roles: {', '.join(missing)}")
        principal_permission_ids = set(context.principal.permission_ids)
        context_permission_ids = {permission.permission_id for permission in context.permissions}
        if not principal_permission_ids.issubset(context_permission_ids):
            missing = sorted(principal_permission_ids - context_permission_ids)
            raise ValueError(f"security context missing principal permissions: {', '.join(missing)}")

    def validate_decision(self, decision: SecurityDecision) -> None:
        if decision.effect is SecurityEffect.ALLOW and not decision.permission_ids:
            raise ValueError("allow security decisions must include matching permissions")

    def validate_registry(
        self,
        *,
        principals: list[SecurityPrincipal],
        roles: list[SecurityRole],
        permissions: list[SecurityPermission],
        policies: list[SecurityPolicy],
    ) -> None:
        _validate_unique_objects("principal identifiers", [item.principal_id for item in principals])
        _validate_unique_objects("role identifiers", [item.role_id for item in roles])
        _validate_unique_objects(
            "permission identifiers",
            [item.permission_id for item in permissions],
        )
        _validate_unique_objects("policy identifiers", [item.policy_id for item in policies])
        for permission in permissions:
            self.validate_permission(permission)
        for role in roles:
            self.validate_role(role, permissions)
        for principal in principals:
            self.validate_principal(principal, roles, permissions)
        for policy in policies:
            self.validate_policy(
                policy,
                roles=roles,
                permissions=permissions,
                principals=principals,
            )


def _validate_unique_values(name: str, values: list[str]) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must be unique")


def _validate_unique_objects(name: str, values: list[str]) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must be unique")
