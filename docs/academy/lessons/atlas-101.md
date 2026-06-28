# Atlas 101

Project Atlas is the Exercise Designer planning environment.

## What You See

- Object Library.
- Exercise Canvas / Timeline.
- Properties Inspector.
- Validation status.
- Relationship map.
- Editable objective cards.
- Editable controller assignments.
- Editable inject and timeline planning forms.

## What It Is For

Use Atlas to design an exercise before it enters Mission Control.

## Alpha Behavior

Atlas Alpha uses Project Sentinel as the reference implementation and stores planning edits in the local Exercise Data Engine for the running session.

You can:

- Create, edit, duplicate, archive, and save draft exercises.
- Add, edit, and delete objectives.
- Add success criteria and linked assets.
- Add and edit controller assignments.
- Create and edit injects with controller, objective, priority, notes, and time.
- Add, edit, delete, and move timeline events.
- Validate readiness and see relationship warnings update live.
- Publish a validated exercise package into Mission Control.
- Review publication summary and version history.

Atlas Alpha does not implement durable persistence, drag and drop, collaborative editing, or production release routing. `Publish` is functional in-memory: it creates an Exercise Package, increments version history, populates live Studio workspaces, and opens Mission Control after validation succeeds.
