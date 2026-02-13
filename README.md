# LLMcourse

DTU LLM Course Project - FastAPI app with PDF processing and sentiment analysis.

## Setup

```bash
# Install dependencies with uv
uv sync
```

## Run

```bash
# With Docker
docker compose up --build

# API available at http://localhost:8000
```

## Development

```bash
# Run tests
uv run pytest

# Run API locally (without Docker)
uv run uvicorn app.main:app --reload
```