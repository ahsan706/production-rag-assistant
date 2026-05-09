# Production RAG Assistant

A Dockerized fullstack RAG assistant that demonstrates asynchronous document ingestion, chunking, embeddings, Qdrant vector search, grounded answer generation, citations, and local Ollama support.

The project is structured as a production-style monorepo:

```txt
production-rag-assistant/
  apps/web      Next.js, TypeScript, Tailwind UI
  apps/api      FastAPI, SQLAlchemy, Alembic
  apps/worker   Celery worker using the API domain code
  docs          Architecture and production notes
  sample-data   Uploadable demo documents
  screenshots   Portfolio screenshot assets
```

## What It Demonstrates

- Document upload with validation, filename sanitization, size limits, checksum de-duplication, and persisted metadata.
- Asynchronous ingestion through Celery and Redis.
- Text extraction for TXT, Markdown, and PDF.
- Token-window chunking with overlap and page metadata where available.
- OpenAI-compatible embedding provider abstraction.
- Ollama local embeddings and chat by default.
- Qdrant vector storage and semantic search.
- Grounded answer generation with backend citation metadata.
- Refusal behavior when retrieved context is not strong enough.
- Docker Compose infrastructure for Postgres, Redis, Qdrant, Ollama, API, worker, and web.
- JSON request logs, request IDs, health checks, retries, and timeout configuration.

## Quick Start

1. Copy environment defaults if you want to override them:

```bash
cp .env.example .env
```

2. Start the full stack:

```bash
docker compose up --build
```

3. Pull the default Ollama models once:

```bash
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull qwen2.5:0.5b
```

4. Open the app:

- Web: http://localhost:3000
- API health: http://localhost:8000/health
- Qdrant: http://localhost:6333/dashboard

## Demo Flow

1. Upload `sample-data/vector-storage.md`.
2. Wait for the document status to become `embedded`.
3. Open `/retrieval` and search for:

```txt
What should embeddings be written into?
```

4. Open `/chat` and ask:

```txt
What does the vector storage validation document say embeddings should be written into?
```

Expected result: the assistant answers from the uploaded document and returns citations.

Unsupported prompt to test refusal:

```txt
What is the capital of Sweden according to the uploaded documents?
```

Expected result: the assistant refuses because the uploaded documents do not support the answer.

## API

Implemented endpoints:

```http
GET  /health

POST /documents/upload
GET  /documents
GET  /documents/{id}

POST /retrieval/debug

POST /chat/sessions
GET  /chat/sessions/{id}
POST /chat/sessions/{id}/messages
```

## Provider Configuration

The AI layer uses OpenAI-compatible HTTP APIs. Ollama is the default local provider:

```env
AI_BASE_URL=http://ollama:11434/v1
AI_API_KEY=ollama
AI_EMBEDDING_MODEL=nomic-embed-text
AI_CHAT_MODEL=qwen2.5:0.5b
AI_EMBEDDING_DIMENSIONS=768
```

To use OpenAI or another compatible provider, set `AI_BASE_URL`, `AI_API_KEY`, `AI_EMBEDDING_MODEL`, `AI_CHAT_MODEL`, and `AI_EMBEDDING_DIMENSIONS` in `.env`.

## Validation Commands

```bash
docker compose ps
curl http://localhost:8000/health
docker compose exec api python -m pytest -p no:cacheprovider tests -q
docker compose run --rm web npm run build
```

## Documentation

- [Architecture](docs/architecture.md)
- [RAG Pipeline](docs/rag-pipeline.md)
- [Ingestion Pipeline](docs/ingestion-pipeline.md)
- [Tradeoffs](docs/tradeoffs.md)
- [Production Notes](docs/production-notes.md)
- [Demo Questions](docs/demo-questions.md)

## Commit History

The implementation is intentionally split into phase commits:

- Infrastructure and upload foundation
- Async ingestion
- Chunking
- Embeddings and Qdrant
- Semantic retrieval
- Grounded RAG answers
- Frontend chat experience
- Observability and timeouts
- Documentation and portfolio polish
