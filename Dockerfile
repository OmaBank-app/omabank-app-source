# STAGE 1: Builder
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation for faster 2026 app startup
ENV UV_COMPILE_BYTECODE=1

# Copy ONLY lockfiles first to maximize Docker layer caching
COPY pyproject.toml uv.lock ./

# Use uv pip to install directly into the system python environment, bypassing venv creation
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy application source code
COPY . /app

# Install the actual app package
RUN uv pip install --system --no-cache --no-deps .

# STAGE 2: Secure Distroless Runtime
FROM gcr.io/distroless/python3-debian12:latest

# We no longer copy /opt/venv. We copy the system packages from python3.11
COPY --from=builder --chown=65532:65532 /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder --chown=65532:65532 /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder --chown=65532:65532 /app /app

USER 65532:65532

# Ensure Python knows exactly where to look for the packages
ENV PYTHONPATH="/usr/local/lib/python3.11/site-packages:/app"

EXPOSE 8000

# Execute the globally installed uvicorn binary
CMD ["/usr/local/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
