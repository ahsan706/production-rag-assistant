import httpx
import pytest

from app.services.embeddings import OpenAICompatibleEmbeddingProvider


def test_openai_compatible_embedding_provider_preserves_input_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(
            200,
            request=httpx.Request("POST", "http://ai.example/v1/embeddings"),
            json={
                "data": [
                    {"index": 1, "embedding": [0.3, 0.4]},
                    {"index": 0, "embedding": [0.1, 0.2]},
                ]
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    provider = OpenAICompatibleEmbeddingProvider("http://ai.example/v1", "test-key", "test-embed")

    assert provider.embed_texts(["first", "second"]) == [[0.1, 0.2], [0.3, 0.4]]


def test_openai_compatible_embedding_provider_returns_empty_batch_without_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(*args, **kwargs):
        raise AssertionError("empty embedding batches should not make HTTP requests")

    monkeypatch.setattr(httpx, "post", fake_post)

    provider = OpenAICompatibleEmbeddingProvider("http://ai.example/v1", "test-key", "test-embed")

    assert provider.embed_texts([]) == []
