# Production RAG Assistant

A production-style Dockerized RAG assistant built as a fullstack monorepo.

## Phase 1 Status

The current implementation provides the infrastructure foundation:

- FastAPI API with dependency health checks
- Next.js frontend placeholder
- Celery worker shell
- PostgreSQL
- Redis
- Qdrant
- Ollama

## Run

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Web: http://localhost:3000
- API health: http://localhost:8000/health
- Qdrant dashboard/API: http://localhost:6333/dashboard

Later phases add document upload, asynchronous ingestion, chunking, embeddings, retrieval, grounded chat, and portfolio documentation.
