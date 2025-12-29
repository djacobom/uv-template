# ----------------------------------------------------------------------------------
# Stage 1: Builder
# ----------------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

# Install dependencies without installing the project itself and dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# ----------------------------------------------------------------------------------
# Stage 2: Final (Runtime)
# ----------------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS final

WORKDIR /app

# Copy only the installed packages from the builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables so Python and the shell find the packages
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the application code
COPY . .

EXPOSE 8080

# Run the application using uvicorn, with configurable port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]



