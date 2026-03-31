# Dockerfile for Delta Dagster + dbt Platform
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies using uv
RUN uv sync --frozen

# Build dbt manifest (required for Dagster)
ENV DBT_TARGET=prod
RUN cd dbt && uv run dbt deps && uv run dbt parse

# Expose Dagster port
EXPOSE 3000

# Set Dagster Home
ENV DAGSTER_HOME=/app/.dagster
RUN mkdir -p $DAGSTER_HOME

# Run Dagster webserver
CMD ["uv", "run", "dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
