# Forge Release Strategy

Forge is an open-source digital operations platform for modern Exercise Control.

Every Event. Every Inject. Every Exercise.

Human Command. Machine Assistance.

This release strategy describes the intended maturity path from architecture foundation to Forge Enterprise Platform. Version labels are planning markers, not production guarantees.

## Release Principles

- Human judgment remains authoritative.
- Forge assists; people decide.
- Each release should preserve deterministic local development and test behavior.
- New capabilities should strengthen exercise lifecycle workflows.
- Extension points should be documented before they are treated as stable.
- No release should imply automatic publishing or uncontrolled external integration.

## v0.1 Architecture Complete

Purpose: establish the platform foundation.

Expected scope:

- Forge Core service foundations.
- End-to-end local demo pipeline.
- Forge Studio local MVP.
- Exercise Data Engine.
- Organization, exercise, and workspace framework.
- Forge Studio Design System.
- Architecture, brand, and operational documentation.

Definition of success: contributors can understand Forge as a modular Exercise Control platform and run deterministic local demonstrations.

## v0.2 Interactive Workspaces

Purpose: make Forge Studio feel operational across the core workspaces.

Expected scope:

- Mission Control refinement.
- Timeline interactions.
- Intelligence workspace workflows.
- Inject Library improvements.
- Exercise Library workflows.
- Review Queue ergonomics.
- Administration surfaces for local configuration.

Definition of success: a user can navigate the platform and understand the exercise workflow without reading implementation code.

## v0.3 Mission Replay

Purpose: introduce replayable exercise history.

Expected scope:

- Replay model.
- Timeline reconstruction.
- Audit-linked event playback.
- Product and review history views.
- Metrics snapshots across exercise time.

Definition of success: a completed exercise can be reviewed as a sequence of events, decisions, reviews, and outputs.

## v0.4 Plugin Framework

Purpose: formalize extensibility.

Expected scope:

- Stable product plugin contract.
- Profile packaging conventions.
- Workflow module conventions.
- Plugin discovery and validation.
- Extension author documentation.

Definition of success: contributors can build controlled Forge extensions without modifying Forge Core.

## v0.5 Forge Assist

Purpose: define bounded AI-assisted workflows.

Expected scope:

- Assist interface design.
- Prompt and context governance.
- Offline and stub provider behavior.
- Review-aware draft assistance.
- Audit metadata for AI-assisted actions.

Definition of success: Forge can support AI-assisted preparation while preserving human review authority.

## v0.6 Enterprise Deployment

Purpose: prepare Forge for controlled organizational deployment.

Expected scope:

- Deployment architecture guidance.
- Configuration profiles.
- Role and permission hardening.
- Operational runbooks.
- Backup, retention, and archive guidance.
- Observability guidance.

Definition of success: an enterprise team can evaluate how Forge would run in a controlled environment.

## v0.7 Coalition Operations

Purpose: support joint and coalition exercise patterns.

Expected scope:

- Coalition-aware profiles.
- Terminology mappings.
- Release constraints.
- Role and sharing models.
- Cross-organization exercise context.

Definition of success: Forge can represent exercise control workflows across multiple organizations and partner contexts.

## v0.8 Operational Analytics

Purpose: strengthen metrics, assessment, and after-action workflows.

Expected scope:

- Exercise analytics dashboards.
- Review latency metrics.
- Product throughput metrics.
- Objective coverage indicators.
- Cross-exercise trend analysis foundation.

Definition of success: Forge can support assessment and leadership awareness with traceable operational metrics.

## v0.9 Release Candidate

Purpose: stabilize the Forge 1.0 surface.

Expected scope:

- Documentation freeze candidate.
- API and SDK review.
- Compatibility review.
- Security review.
- Usability review.
- Test and validation hardening.

Definition of success: Forge is ready for final 1.0 readiness review.

## v1.0 Forge Enterprise Platform

Purpose: establish Forge as a professional enterprise platform foundation for Exercise Control.

Expected scope:

- Stable Forge Core architecture.
- Usable Forge Studio workflows.
- Documented Forge API direction.
- Documented Forge SDK direction.
- Controlled plugin and profile ecosystem.
- Mission Replay foundation.
- Forge Assist foundation.
- Enterprise deployment guidance.
- Coalition and analytics direction.

Definition of success: Forge can be presented as a coherent open-source platform for modern Exercise Control, with clear boundaries, extension points, and future growth path.
