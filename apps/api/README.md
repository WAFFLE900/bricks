# Bricks API

This backend is managed with `uv`.

## Setup

```powershell
cd C:\bricks\apps\api
uv sync
```

## Run locally

```powershell
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test

```powershell
uv run pytest
```

## Docker

The container image also uses `uv sync` during build, so local and container dependency resolution stay aligned.

