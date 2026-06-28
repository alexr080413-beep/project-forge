# Forge Studio Web MVP

Forge Studio Web MVP is the first runnable local application for Forge Studio. It proves the platform architecture by connecting the Forge Studio MVP domain models to a small web interface with mock data.

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

## What It Shows

The app displays:

- Forge logo and title
- Primary slogan: Every Event. Every Inject. Every Exercise.
- Dark Forge command-center theme
- Orange accents
- Responsive sidebar navigation
- Dashboard backed by Forge Studio MVP mock data
- Placeholder pages for future sections

Navigation sections:

- Dashboard
- Exercises
- Timeline
- Inject Library
- Controllers
- Reports
- Settings

## Dashboard Data

The dashboard uses `project_forge.forge_studio.mock_data.create_mock_registry()` to create local mock objects from the existing Forge Studio MVP domain model.

Dashboard metrics:

- Active Exercise
- Exercise Status
- Exercise Phase
- Pending Reviews
- Active Injects
- Timeline Summary
- Controller Count

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
