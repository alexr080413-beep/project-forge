# Publish To Mission Control

Use this guide to publish a validated Atlas plan into live Forge Studio workspaces.

The Publish Pipeline converts an editable planning exercise into a versioned Exercise Package and opens Mission Control.

## Steps

1. Open `Exercise Designer`.
2. Validate exercise metadata, objectives, timeline, injects, controllers, relationships, Knowledge Graph, required products, and review requirements.
3. Confirm the Exercise Director approves the plan.
4. Resolve blocking validation issues.
5. Select `Publish`.
6. Confirm the publication summary shows a new version.
7. Confirm Mission Control opens.
8. Confirm live workspaces receive the approved exercise objects.

## Validation Gate

Publication is blocked until validation succeeds.

The pipeline checks:

- Exercise metadata.
- Objectives.
- Timeline.
- Injects.
- Controllers.
- Relationships.
- Knowledge Graph.
- Required products.
- Review requirements.

## Exercise Package

Publishing creates an internal Exercise Package containing:

- Exercise.
- Objectives.
- Timeline.
- Injects.
- Controllers.
- Operational assets.
- Knowledge Graph.
- Relationships.
- Validation summary.
- Publication timestamp.
- Version number.

## Version History

The first publication creates `Version 1`.

Subsequent publications create `Version 2`, `Version 3`, and so on.

## Current Boundary

Publishing is in-memory in Atlas Alpha. It populates live Studio workspaces for the running session and remains explicit and human-approved. Durable persistence and production release routing are future capabilities.
