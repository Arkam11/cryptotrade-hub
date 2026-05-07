# Build stage — installs all dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install Poetry with the export plugin
RUN pip install poetry==2.3.4 && \
    poetry self add poetry-plugin-export

# Copy dependency files first — Docker caches this layer
# and skips reinstallation when only application code changes
COPY pyproject.toml poetry.lock* ./

# Export to requirements.txt for the runtime stage
# --without dev excludes test and linting tools
RUN poetry export -f requirements.txt --output requirements.txt --without dev --no-interaction


# Runtime stage — lean image with only what is needed to run
FROM python:3.11-slim AS runtime

WORKDIR /app

# System libraries required by psycopg2 and bcrypt
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from builder stage
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .

# Run as non-root user for container security
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
