# Changelog

All notable changes to Project Forge will be documented in this file.

This project can follow the principles of [Keep a Changelog](https://keepachangelog.com/) and semantic versioning once releases begin.

## [Unreleased]

### Added

- Initial project skeleton.
- Placeholder documentation set.
- Python package source layout.
- Test, asset, configuration, knowledge base, output, and GitHub Actions directories.
- Typed core models for source items, exercise context, scenario actors and locations, scenario mappings, report requests, generated reports, review status, and quality checks.
- Pipeline Orchestrator foundation with ordered stage execution, execution logging, metadata, failure handling, registry support, and a real-world event example pipeline.
- Executive and platform documentation covering vision, architecture, services, profiles, plugins, workflows, and development conventions.
- Profile Manager foundation with YAML loading, profile validation, registry lookup, and example MWTC, ITX, and Joint Exercise profiles.
- Review Queue Service foundation with ordered queues, reviewer assignment, approval, rejection, revision requests, audit history, notes, timestamps, registry support, manager operations, and sample review items.
- Distribution Service foundation with channel registration, target validation, dry-run handling, status tracking, audit metadata, local file/archive handlers, and placeholder channels for email-ready, markdown, HTML, DOCX, PDF, PowerPoint, SharePoint, and Teams outputs.
- Automation Service foundation with automation rules, cron schedules, manual triggers, event triggers, workflow triggers, conditional triggers, enable/disable controls, execution history, retry policy validation, and registry support.
- Integration Service foundation with YAML-loaded source definitions, connector registration, source validation, dry-run collection, status tracking, metadata capture, error handling, and audit metadata for RSS, website, manual upload, local file, and placeholder external source types.
- Storage Service foundation with provider registration, path validation, metadata reads, dry-run writes, local folder listing, archive operations, audit metadata, and placeholder S3, Azure Blob, and SharePoint providers.
- Search Service foundation with query validation, multiple local indexes, exact search, partial search, tag search, metadata search, date and service filtering, relevance ranking, pagination, and future semantic/vector/hybrid capability declarations.
- Audit Service foundation with in-memory actors, actions, categories, events, entries, sessions, validation, timestamps, correlation IDs, parent/child events, severity, tags, metadata, and filtering.
- Metrics Service foundation with counters, gauges, timers, histogram placeholders, tags, metadata, snapshots, collectors, reports, validation, and standard Forge operational metrics.
- Configuration Service foundation with YAML/JSON loading, scoped configuration items, profiles, defaults, deterministic overrides, required field validation, environment variable placeholders, metadata, registry lookup, and audit-ready change records.
- Security Service foundation with users, service accounts, system actors, roles, permissions, policies, RBAC evaluation, default Forge roles, metadata, validation, and audit-ready allow/deny decision records.
- End-to-end demo pipeline command that runs a local sample event through implemented Forge service foundations, dry-run handlers, offline AI stub reasoning, audit logging, and metrics snapshotting.

### Changed

- Nothing yet.

### Deprecated

- Nothing yet.

### Removed

- Nothing yet.

### Fixed

- Nothing yet.

### Security

- Nothing yet.
