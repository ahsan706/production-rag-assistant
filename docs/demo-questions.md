# Demo Questions

Upload `sample-data/vector-storage.md`, wait for `embedded`, then ask:

```txt
What does the vector storage validation document say embeddings should be written into?
```

Expected behavior:

- retrieves the matching chunk
- answers with Qdrant
- includes citation metadata

Ask an unsupported question:

```txt
What is the capital of Sweden according to the uploaded documents?
```

Expected behavior:

- refuses with "I don't know based on the provided documents."
- preserves retrieved debug context
- does not cite irrelevant chunks as support

Upload `sample-data/operations-runbook.txt`, then ask:

```txt
What should an operator check if ingestion jobs are retrying?
```

Expected behavior:

- retrieves operational guidance from the sample runbook
- answers with citations
