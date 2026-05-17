# Contributing

This repo is a portfolio project — issues and small PRs are welcome, but I don't promise responsiveness. If you're forking it for your own use, no need to ask.

## Repo layout

```
apps/web      Next.js 16, TypeScript, Tailwind
apps/api      FastAPI, SQLAlchemy 2, Alembic
apps/worker   Celery worker; reuses apps/api domain code
docs          Architecture, pipelines, tradeoffs, review
sample-data   Demo documents you can upload
```

The worker currently imports from `apps/api/app/` directly. See `docs/architecture-review.md` for why this is flagged and how it would be split.

## Local Python venv (for IDE / Pylance)

Python dependencies are managed with [uv](https://docs.astral.sh/uv/). Install uv, then from `apps/api/`:

```bash
uv sync
```

uv reads `.python-version` and `requires-python` in `pyproject.toml`, refuses to run on the wrong interpreter, and creates `apps/api/.venv` with the locked deps. Then in VS Code: `Cmd+Shift+P` → "Python: Select Interpreter" → `apps/api/.venv`.

To add a dep: `uv add <pkg>` (or `uv add --group dev <pkg>` for dev-only). Commit the updated `pyproject.toml` and `uv.lock`.

## Development loop

```bash
cp .env.example .env
docker compose up --build

# one-time: pull local models
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull qwen2.5:0.5b
```

## Tests

```bash
docker compose exec api python -m pytest -q
docker compose run --rm web npm run build
```

API tests are hermetic — they monkeypatch `httpx`, so no live Postgres / Qdrant / Ollama is required to run them. They do, however, require the env vars in `.env.example` to be set, because `Settings()` reads them at import time.

## Style

- **Python**: 3.12.x, pinned via `.python-version` and `requires-python` in `apps/api/pyproject.toml`. Deps managed by uv (`uv.lock` is the source of truth). `ruff check` / `ruff format` configured in the same `pyproject.toml`; line length 100; `from __future__ import annotations` is the repo convention.
- **Node**: 22.x (`.nvmrc`). `engines` in `apps/web/package.json` plus `engine-strict=true` in `apps/web/.npmrc` make `npm install` hard-fail on the wrong runtime.
- **TypeScript**: `tsc --noEmit` for type errors; `next build` is the build gate.
- **Commits**: short imperative subject. The repo's history uses phase-style scopes (`feat(ingestion):`, `docs:`, `chore:`).
- **Pre-commit** is optional but recommended:
  ```bash
  pipx install pre-commit && pre-commit install
  ```

## What I'll merge

- Bug fixes with a regression test.
- Docs improvements (typos, clarity, missing context).
- Items from the "Decisions I would defend" section of `docs/architecture-review.md` only if you have a strong reason to revisit them.
- Items from "What's missing for production" only if scoped narrowly and the PR doesn't grow the surface area unreasonably for a portfolio repo.

## What I'll close politely

- Wholesale rewrites of working code.
- New features that don't fit the portfolio scope.
- "Add framework X" PRs with no migration plan.
