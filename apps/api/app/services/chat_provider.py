from __future__ import annotations

from typing import Protocol

import httpx

from app.core.config import settings


class ChatProvider(Protocol):
    def generate(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        pass


class OpenAICompatibleChatProvider:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def generate(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "messages": messages, "temperature": temperature},
            timeout=120.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()


def get_chat_provider() -> ChatProvider:
    return OpenAICompatibleChatProvider(
        base_url=settings.ai_base_url,
        api_key=settings.ai_api_key,
        model=settings.ai_chat_model,
    )
