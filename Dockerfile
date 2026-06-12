# STAGE 1: Builder
# Pinning explicit Python version and SHA-256 digest
FROM python:3.11.12-slim@sha256:d8058726dd9c9d0903362a26569ec988d3f6a2b8e3a2468f3074d6c6e7a2b9d1 AS builder

# Pinning explicit Astral UV tool digest
COPY --from=ghcr.io/astral-sh/uv:0.6.0@sha256:5db988c5efb47b4df4477c77efd5bb1339adcd77bde2130e5cf7eef9b49b387e /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation for faster 2026 app startup
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy ONLY lockfiles first to maximize Docker layer caching
COPY pyproject.toml uv.lock ./
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies ONLY (do not look for app source code yet)
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY . /app

# Now that source is copied, sync the actual OmaBank package
RUN uv sync --frozen --no-dev

# STAGE 2: Secure Distroless Runtime
# Pinning the exact Debian 12 Python 3 distroless digest
FROM gcr.io/distroless/python3-debian12@sha256:918bbbfbb39fb04ca98cf982e04da57c8bfcd3a6c23cfb8bdfb1e32719280d0d

# Enforce least privilege using explicit numeric UIDs (Required for Kubernetes Kyverno)
COPY --from=builder --chown=65532:65532 /opt/venv /opt/venv
COPY --from=builder --chown=65532:65532 /app /app

# Apply NIST 800-53 compliant non-root execution via explicit UID
USER 65532:65532

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000

# Execute server safely inside the distroless sandbox
CMD ["/opt/venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
