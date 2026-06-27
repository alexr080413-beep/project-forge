# Runbook

This runbook captures operational procedures for Project Forge maintainers. It is intentionally lightweight until the project has real runtime behavior.

## Current Operations

There are no production services, scheduled jobs, deployment targets, or runtime tasks yet.

## Maintenance Checklist

- Keep documentation current with code changes.
- Keep `CHANGELOG.md` updated for notable changes.
- Keep generated files in `outputs/` unless they are intentional fixtures.
- Review GitHub Actions workflows whenever dependencies or supported Python versions change.
- Document recurring operational tasks here as they are introduced.

## Incident Response Placeholder

When Project Forge gains production behavior, document:

- Known failure modes
- Alert sources
- Triage steps
- Rollback procedures
- Recovery commands
- Escalation contacts or ownership boundaries

## Release Placeholder

When releases begin, document:

- Versioning policy
- Release checklist
- Artifact publishing process
- Post-release verification
