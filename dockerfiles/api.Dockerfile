FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set working directory
WORKDIR /app

# Copy dependency metadata first (for caching)
COPY pyproject.toml uv.lock ./

# Install runtime dependencies only
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ app/

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI service
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
