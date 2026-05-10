# Handoff State
Updated: 2026-05-09T20:56:46Z
From: codex   To: _none_
Branch: main   Last commit: 97ef7e9

## Current Task
Production RAG Assistant — portfolio-grade Dockerized RAG over FastAPI + Celery + Qdrant + Next.js with local Ollama. The work was split into nine phase commits ending in `97ef7e9 docs: polish portfolio handoff`. Codex completed the portfolio scope.

## Status
ready-for-review

## Last Action
Codex committed `97ef7e9 docs: polish portfolio handoff` and ended its session. Working tree is clean. No tests were re-run in this Claude session — the last documented validation commands live in `README.md` under "Validation Commands":
- `docker compose ps`
- `curl http://localhost:8000/health`
- `docker compose exec api python -m pytest -p no:cacheprovider tests -q`
- `docker compose run --rm web npm run build`

## Next Steps
- [ ] _none for portfolio scope._ If you want to keep going, pick from `docs/production-notes.md` (auth, OpenTelemetry, dead-letter queue, rate limits, Qdrant snapshots, etc.) and convert it into a Current Task before resuming.

## Files In Flight
- _none_

## Blockers / Open Questions
- _none_

## Mental Model
This file is also serving as the seed example for the new Codex ↔ Claude Code handoff protocol defined in `~/AGENTS.md`. The protocol expects this file to be **overwritten**, not appended, on each handoff. Keep it that way — git log is the journal, this file is current state. The repo is monorepo-style with three apps (`api/`, `worker/`, `web/`) sharing one `packages/shared/` workspace; ingestion is async via Celery; embeddings/search go through Qdrant; refusal behavior triggers when retrieved context is below a similarity threshold.
