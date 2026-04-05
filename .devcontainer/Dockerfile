FROM mcr.microsoft.com/devcontainers/python:3.12

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Keep venv inside project for visibility
ENV UV_PROJECT_ENVIRONMENT=/workspaces/aviation-ops-briefing-agent/.venv
