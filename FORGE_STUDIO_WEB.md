# Forge Studio Web MVP

Forge Studio Web MVP is the first runnable local application for Forge Studio. It proves the platform architecture by connecting the Forge Studio MVP domain models to a small web interface with mock operational data.

This is intentionally minimal. It does not implement authentication, persistence, frontend build tooling, automatic publishing, external APIs, or every Forge Studio feature.

## Start Locally

From the repository root:

```bash
python -m project_forge.forge_studio.web_app
```

Then open:

```text
http://127.0.0.1:8765
```

Optional host and port:

```bash
python -m project_forge.forge_studio.web_app --host 127.0.0.1 --port 8787
```

## Active Exercise

The interactive demo revolves around one active exercise:

| Field | Value |
| --- | --- |
| Exercise | Mountain Exercise 3-27 |
| Status | ACTIVE |
| Phase | EXECUTE |
| Start | 0800 |
| Exercise Director | Col Smith |
| Exercise Control | Bridgeport EXCON |

## What It Shows

The app displays:

- Forge logo and title
- Primary slogan: Every Event. Every Inject. Every Exercise.
- Dark Forge command-center theme
- Orange accents
- Responsive sidebar navigation
- Dashboard backed by Forge Studio MVP mock data
- Exercise Workspace page
- Operational Timeline page
- Inject Library page
- Controller cards
- Exercise Library product repository
- Settings cards

Navigation sections:

- Dashboard
- Exercises
- Timeline
- Inject Library
- Controllers
- Exercise Library
- Settings

## Exercise Workspace Concept

The Exercise Workspace is the primary operating surface for a single active exercise. It gathers exercise overview, objectives, participating units, phase, timeline status, exercise director, training audience, and statistics into one controller-facing page.

The workspace is not a personal dashboard. It is the shared operational context for Exercise Control. Future Forge Studio features should treat this workspace as the anchor for injects, timeline events, controller activity, review queues, products, audit records, and after-action material.

## Dashboard Data

The dashboard uses `project_forge.forge_studio.mock_data.create_mock_registry()` to create local mock objects from the existing Forge Studio MVP domain model.

Dashboard metrics:

- Active Exercise
- Exercise Status
- Exercise Phase
- Pending Reviews
- Open Injects
- Products Generated
- Timeline Summary
- Controller Count
- Current Operational Time
- Latest Activity Feed

## Exercise Library Philosophy

The Exercise Library replaces the generic Reports placeholder. It is the historical repository for every product generated during the exercise.

The library organizes generated material into folders:

- Intelligence
- Injects
- Media
- Weather
- Reports
- Maps
- Photos
- Video
- Documents
- Exports

Each product record shows product type, title, status, version, last updated time, author, and review status. The library should eventually become the authoritative exercise archive for retrieval, assessment, export, and after-action review.

The API endpoint is:

```text
GET /api/dashboard
```

The endpoint is served by the local stdlib web server in:

```text
src/project_forge/forge_studio/web_app.py
```

## Structure

```text
src/project_forge/forge_studio/
├── mock_data.py
├── web_app.py
└── static/
    ├── index.html
    ├── styles.css
    └── app.js
```

## Design Direction

The interface follows the Forge design language:

- Dark theme
- Graphite and steel surfaces
- Orange Forge accents
- Dense operational cards
- Sidebar navigation
- No consumer-style landing page
- No decorative UI that competes with exercise data

## Boundaries

Current boundaries:

- No frontend framework
- No npm dependency
- No authentication
- No database
- No automatic publishing
- No real distribution
- No external network calls
- No live AI provider calls

The application is a runnable proof of architecture, not the final Forge Studio product.

## Future Work

Future sprints can add:

- Real route adapters
- Persistent storage
- Role-based authorization
- Editable exercise records
- Timeline interactions
- Inject library workflows
- Review queue actions
- Audit log views
- Metrics and health panels
- React or another frontend framework if the project adopts one
