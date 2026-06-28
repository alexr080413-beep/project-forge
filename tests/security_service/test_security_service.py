import pytest

from project_forge.security_service import (
    SecurityEffect,
    SecurityPermission,
    SecurityPolicy,
    SecurityPrincipal,
    SecurityPrincipalType,
    SecurityRegistry,
    SecurityRole,
    SecurityValidator,
    create_default_security_registry,
)


def principal(
    principal_id: str = "user:controller-one",
    *,
    principal_type: SecurityPrincipalType = SecurityPrincipalType.USER,
    role_ids: list[str] | None = None,
    permission_ids: list[str] | None = None,
    enabled: bool = True,
) -> SecurityPrincipal:
    return SecurityPrincipal(
        principal_id=principal_id,
        display_name="Controller One",
        principal_type=principal_type,
        role_ids=["reviewer"] if role_ids is None else role_ids,
        permission_ids=[] if permission_ids is None else permission_ids,
        enabled=enabled,
        metadata={"exercise_day": 1},
    )


def test_default_registry_contains_required_roles() -> None:
    registry = create_default_security_registry()

    assert [role.role_id for role in registry.list_roles()] == [
        "administrator",
        "excon_controller",
        "exercise_director",
        "intelligence_controller",
        "media_controller",
        "reviewer",
        "system",
        "viewer",
    ]


def test_principals_and_roles_register_and_lookup() -> None:
    registry = create_default_security_registry()
    item = principal(role_ids=["viewer"])

    registry.register_principal(item)

    assert registry.get_principal("user:controller-one") is item
    assert registry.get_role("viewer").role_id == "viewer"


def test_unknown_principal_role_fails_validation() -> None:
    registry = create_default_security_registry()

    with pytest.raises(ValueError):
        registry.register_principal(principal(role_ids=["missing"]))


def test_role_permission_references_validate() -> None:
    permission = SecurityPermission(
        permission_id="product:approve",
        name="Approve Products",
        action="approve",
        resource="product",
    )
    role = SecurityRole(
        role_id="approver",
        name="Approver",
        permission_ids=["product:approve"],
    )

    SecurityValidator().validate_role(role, [permission])


def test_unknown_role_permission_fails_validation() -> None:
    with pytest.raises(ValueError):
        SecurityValidator().validate_role(
            SecurityRole(
                role_id="bad-role",
                name="Bad Role",
                permission_ids=["missing"],
            ),
            [],
        )


def test_role_based_decision_allows_matching_permission() -> None:
    registry = create_default_security_registry([principal(role_ids=["reviewer"])])

    decision = registry.evaluate(
        "user:controller-one",
        "review",
        "product",
        metadata={"request_id": "request-1"},
    )

    assert decision.allowed
    assert decision.effect is SecurityEffect.ALLOW
    assert decision.permission_ids == ["product:review"]
    assert decision.policy_ids == ["default-allow:reviewer"]
    assert decision.metadata == {"request_id": "request-1"}
    assert registry.list_decisions() == [decision]


def test_missing_permission_denies_decision() -> None:
    registry = create_default_security_registry([principal(role_ids=["viewer"])])

    decision = registry.evaluate("user:controller-one", "review", "product")

    assert decision.denied
    assert decision.effect is SecurityEffect.DENY
    assert decision.reason == "no matching permission"
    assert decision.permission_ids == []


def test_explicit_deny_policy_overrides_matching_permission() -> None:
    registry = create_default_security_registry([principal(role_ids=["reviewer"])])
    registry.register_policy(
        SecurityPolicy(
            policy_id="deny-review-freeze",
            name="Deny Review During Freeze",
            effect=SecurityEffect.DENY,
            permission_ids=["product:review"],
            role_ids=["reviewer"],
            priority=1,
            metadata={"reason": "control freeze"},
        )
    )

    decision = registry.evaluate("user:controller-one", "review", "product")

    assert decision.denied
    assert decision.reason == "explicit deny policy matched"
    assert decision.policy_ids == ["deny-review-freeze"]
    assert decision.permission_ids == ["product:review"]


def test_disabled_principal_denies_decision() -> None:
    registry = create_default_security_registry([principal(enabled=False)])

    decision = registry.evaluate("user:controller-one", "review", "product")

    assert decision.denied
    assert decision.reason == "principal is disabled"


def test_direct_principal_permission_supports_service_accounts() -> None:
    service_account = principal(
        principal_id="service:distribution",
        principal_type=SecurityPrincipalType.SERVICE_ACCOUNT,
        role_ids=[],
        permission_ids=["system:operate"],
    )
    registry = create_default_security_registry([service_account])

    decision = registry.evaluate("service:distribution", "operate", "system")

    assert decision.allowed
    assert decision.role_ids == []
    assert decision.permission_ids == ["system:operate"]


def test_system_actor_can_use_system_role() -> None:
    system_actor = principal(
        principal_id="system:pipeline",
        principal_type=SecurityPrincipalType.SYSTEM_ACTOR,
        role_ids=["system"],
    )
    registry = create_default_security_registry([system_actor])

    decision = registry.evaluate("system:pipeline", "delete", "anything")

    assert decision.allowed
    assert "platform:all" in decision.permission_ids


def test_policy_references_are_validated() -> None:
    registry = create_default_security_registry()

    with pytest.raises(ValueError):
        registry.register_policy(
            SecurityPolicy(
                policy_id="bad-policy",
                name="Bad Policy",
                effect=SecurityEffect.ALLOW,
                permission_ids=["missing"],
            )
        )


def test_duplicate_registry_identifiers_are_rejected() -> None:
    item = principal()

    with pytest.raises(ValueError):
        SecurityRegistry(principals=[item, item])
