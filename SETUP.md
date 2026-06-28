# Setup

This guide describes the expected local setup path for Project Forge. Commands are placeholders until the project defines concrete runtime dependencies.

## Requirements

- Python 3.11 or newer
- Git
- A virtual environment tool such as `venv`, `uv`, `pyenv`, or `conda`

## Create A Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install The Project

Once dependencies are defined, install the project in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Validate The Environment

Run tests with:

```bash
python -m pytest
```

Run the local end-to-end demo pipeline with:

```bash
python -m project_forge.demo_pipeline
```

Run the local Forge Studio Web MVP with:

```bash
python -m project_forge.forge_studio.web_app
```

Open:

```text
http://127.0.0.1:8765
```

Future quality checks should add canonical commands for:

- Formatting code
- Linting code
- Type checking code
- Building distributable artifacts

## Configuration

Use files in `config/` as templates for local settings. Do not commit secrets, credentials, tokens, private keys, or personal machine paths.
