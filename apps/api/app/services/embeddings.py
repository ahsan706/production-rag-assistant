from __future__ import annotations

from typing import Protocol

import httpx

from app.core.config import settings


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        pass


class OpenAICompatibleEmbeddingProvider:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": texts},
            timeout=settings.ai_request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        data = sorted(payload["data"], key=lambda item: item["index"])
        return [item["embedding"] for item in data]


def get_embedding_provider() -> EmbeddingProvider:
    return OpenAICompatibleEmbeddingProvider(
        base_url=settings.ai_base_url,
        api_key=settings.ai_api_key,
        model=settings.ai_embedding_model,
    )
