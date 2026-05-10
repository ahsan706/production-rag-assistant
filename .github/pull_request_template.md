<!-- Keep PRs small and focused. One concern per PR. -->

## Summary

<!-- One paragraph: what changes and why. -->

## Type

- [ ] Feature
- [ ] Fix
- [ ] Refactor (no behavior change)
- [ ] Docs / chore
- [ ] Migration (touches `apps/api/alembic/versions/`)

## Verification

<!-- How a reviewer can convince themselves this works. Paste commands and results. -->

- [ ] `docker compose exec api python -m pytest -q` passes
- [ ] `docker compose run --rm web npm run build` passes (if web touched)
- [ ] Manual smoke test in the UI (if user-facing)

## Migration notes

<!-- If this PR adds a migration: describe the schema change, whether it is online,
     and what to do on rollback. Otherwise: N/A. -->

## Risk

<!-- What's the blast radius if this is wrong? Anything to watch in logs after deploy? -->
