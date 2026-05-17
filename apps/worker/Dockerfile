FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.13 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

RUN addgroup --system app && adduser --system --ingroup app app
RUN mkdir -p /data/uploads /data/extracted && chown -R app:app /data

COPY --chown=app:app apps/api/app ./app

USER app

CMD ["celery", "-A", "app.worker.celery_app", "worker", "--loglevel=INFO", "--concurrency=2"]
