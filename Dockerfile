FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies only (no dev extras)
RUN uv sync --frozen --no-dev

# Copy application source
COPY src/ ./src/
COPY config/ ./config/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Expose default port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "uvicorn", "cop_thief.webserver.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
