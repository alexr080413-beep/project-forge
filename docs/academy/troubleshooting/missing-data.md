# Missing Data Troubleshooting

## Symptoms

- Dashboard counts look wrong.
- Injects or products are missing.
- Knowledge Graph nodes do not match the selected exercise.

## Checks

1. Confirm the selected exercise.
2. Confirm the workspace is reading from the Exercise Data Engine.
3. Check whether the current feature uses mock data.
4. Restart the local app if in-memory state was changed during testing.

## Current Boundary

The MVP does not persist data after the local server stops.
