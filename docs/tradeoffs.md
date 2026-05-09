# Tradeoffs

## OpenAI-Compatible Provider Interface

The project uses OpenAI-compatible `/embeddings` and `/chat/completions` APIs. This keeps OpenAI, Ollama, and compatible hosted providers behind the same configuration surface.

Tradeoff: provider-specific features are intentionally not exposed yet. The benefit is a clear portable baseline.

## Qdrant as Search Index

Chunk metadata is persisted in Postgres and duplicated into Qdrant payloads.

Tradeoff: duplication requires consistency discipline. The benefit is fast debug output from Qdrant and durable relational records in Postgres.

## Threshold-Based Refusal

The answer layer refuses when retrieval scores are below a configurable threshold.

Tradeoff: a threshold can reject some borderline valid questions. The benefit is a conservative default that avoids confident unsupported answers.

## Docker-First Development

All services run in Docker Compose.

Tradeoff: local iteration is heavier than single-process development. The benefit is a realistic production-style environment with service boundaries, health checks, volumes, and repeatable setup.

## Simple Chunking Before Advanced Parsing

The chunker uses fixed token windows with overlap.

Tradeoff: semantic sectioning could improve retrieval later. The benefit is understandable, testable behavior before adding document-layout complexity.
