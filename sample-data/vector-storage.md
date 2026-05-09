# Vector Storage Validation Document

Embeddings should be written into Qdrant for semantic retrieval.

The ingestion worker extracts document text, chunks the text with overlap, generates embeddings through the configured OpenAI-compatible provider, and stores vectors in the `rag_chunks` collection.

Every grounded answer should include citations that point back to retrieved chunks.
