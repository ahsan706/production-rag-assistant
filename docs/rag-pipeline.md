# RAG Pipeline

The RAG path starts after a document reaches `embedded`.

```mermaid
sequenceDiagram
  participant User
  participant Web
  participant API
  participant Embeddings
  participant Qdrant
  participant Postgres
  participant Chat

  User->>Web: Ask question
  Web->>API: POST /chat/sessions/{id}/messages
  API->>Embeddings: Embed query
  API->>Qdrant: Search top K vectors
  API->>Postgres: Hydrate chunks and documents
  API->>API: Filter weak support
  alt Supported
    API->>Chat: Generate grounded answer
    API->>Postgres: Save messages, citations, retrieved context
    API->>Web: Answer with citations
  else Unsupported
    API->>Postgres: Save refusal and retrieved debug context
    API->>Web: I don't know based on provided documents
  end
```

## Grounding Rules

The system prompt requires the model to:

- use only retrieved context
- cite factual claims with numbered labels
- refuse unsupported questions
- avoid sources not present in context

Citation objects are built by the backend from retrieved chunks. The model does not invent source metadata.

## Retrieval Debugging

`POST /retrieval/debug` exposes raw semantic retrieval with:

- chunk ID
- document ID
- filename
- chunk index
- page number
- score
- text

This makes retrieval quality inspectable before answer generation.
