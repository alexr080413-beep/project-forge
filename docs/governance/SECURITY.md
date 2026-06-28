# Security Policy

Forge is designed around controlled exercise workflows, auditability, and human approval.

## Responsible Disclosure

Do not disclose security issues publicly before maintainers have had time to review and respond.

Report:

- Authentication or authorization weaknesses.
- Secret exposure.
- Unsafe external calls.
- Audit bypasses.
- Review gate bypasses.
- Data leakage risks.
- Dependency or configuration risks.

## Security Philosophy

Forge should be:

- Secure by default.
- Local and deterministic by default.
- Explicit about external calls.
- Audit-ready.
- Human-authority centered.
- Careful with real-world and exercise-fiction boundaries.

## Authentication Goals

Current Forge foundations do not implement production authentication. Future authentication should support clear identity, roles, permissions, and audit records without weakening human approval gates.

## Audit Philosophy

Security-sensitive actions should produce records that explain:

- Who acted.
- What changed.
- What target was affected.
- What result occurred.
- When it happened.

## Human Approval Philosophy

Forge must not silently publish, distribute, or release controlled exercise material. Human review remains authoritative.
