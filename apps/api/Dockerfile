FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.13 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

RUN addgroup --system app && adduser --system --ingroup app app
RUN mkdir -p /data/uploads && chown -R app:app /data

COPY --chown=app:app alembic.ini .
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app app ./app
COPY --chown=app:app tests ./tests

USER app

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
