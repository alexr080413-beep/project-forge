# Startup Troubleshooting

## Symptoms

- Forge Studio does not start.
- Browser cannot reach `http://127.0.0.1:8765`.
- Port is already in use.

## Checks

1. Run `python -m project_forge.forge_studio.web_app`.
2. Confirm the command prints the local URL.
3. If the port is in use, start with another port.
4. Open the printed URL in a browser.

## Current Boundary

Forge Studio MVP uses a local stdlib web server and in-memory data.
