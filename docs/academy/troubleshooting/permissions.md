# Permissions Troubleshooting

## Symptoms

- User expects an action to be role-restricted.
- Role names or review authority are unclear.

## Checks

1. Review [Roles](../reference/roles.md).
2. Confirm the current MVP has no real authentication.
3. Confirm human review still governs release.
4. Do not assume CAC, external identity, or production RBAC is implemented in Forge Studio MVP.

## Current Boundary

The security service provides local authorization foundations, but Forge Studio MVP does not implement real authentication.
