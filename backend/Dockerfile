FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

WORKDIR /app

FROM base AS deps-dev
COPY pyproject.toml ./
RUN uv sync --no-install-project --dev

FROM base AS deps-prod
COPY pyproject.toml ./
RUN uv sync --no-install-project --no-dev

FROM base AS development
COPY --from=deps-dev /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:${PATH}"
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS production
COPY --from=deps-prod /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:${PATH}"
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
