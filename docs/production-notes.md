# Production Notes

This project is portfolio-grade, not a complete SaaS deployment. The current architecture is intentionally ready for production hardening.

## Security

- File type allow-list for PDF, TXT, and Markdown.
- Size limits enforced while streaming upload bytes.
- Filenames sanitized before storage.
- Secrets are environment-based and not committed.
- API validates request bodies with Pydantic.

Production additions:

- authentication and authorization
- tenant isolation
- object storage instead of local Docker volumes
- malware scanning for uploads
- stricter MIME sniffing

## Reliability

Implemented:

- Docker health checks
- dependency-aware startup
- Celery retries
- request IDs
- JSON logs
- provider timeouts
- persisted ingestion logs and errors

Production additions:

- OpenTelemetry traces
- metrics export
- dead-letter queue
- retry backoff tuning
- rate limits
- circuit breakers for model providers

## Data Operations

Postgres is the source of truth for metadata and conversations. Qdrant can be rebuilt from Postgres chunks if needed.

Production additions:

- managed Postgres backups
- Qdrant snapshots
- migration CI
- retention policies
- admin tools for re-ingestion
