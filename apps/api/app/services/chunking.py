from __future__ import annotations

import re
from dataclasses import dataclass

DEFAULT_CHUNK_TOKENS = 800
DEFAULT_OVERLAP_TOKENS = 150

TOKEN_RE = re.compile(r"\S+")
PAGE_RE = re.compile(r"\[Page\s+(\d+)\]")


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    text: str
    token_count: int
    char_start: int
    char_end: int
    page_number: int | None


def _page_for_position(text: str, char_start: int) -> int | None:
    page_number: int | None = None
    for match in PAGE_RE.finditer(text):
        if match.start() > char_start:
            break
        page_number = int(match.group(1))
    return page_number


def chunk_text(
    text: str,
    chunk_tokens: int = DEFAULT_CHUNK_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[TextChunk]:
    if chunk_tokens <= 0:
        raise ValueError("chunk_tokens must be greater than zero.")
    if overlap_tokens < 0:
        raise ValueError("overlap_tokens cannot be negative.")
    if overlap_tokens >= chunk_tokens:
        raise ValueError("overlap_tokens must be smaller than chunk_tokens.")

    matches = list(TOKEN_RE.finditer(text))
    if not matches:
        return []

    chunks: list[TextChunk] = []
    start_token = 0
    while start_token < len(matches):
        end_token = min(start_token + chunk_tokens, len(matches))
        char_start = matches[start_token].start()
        char_end = matches[end_token - 1].end()
        chunk_body = text[char_start:char_end].strip()
        chunks.append(
            TextChunk(
                chunk_index=len(chunks),
                text=chunk_body,
                token_count=end_token - start_token,
                char_start=char_start,
                char_end=char_end,
                page_number=_page_for_position(text, char_start),
            )
        )
        if end_token == len(matches):
            break
        start_token = max(end_token - overlap_tokens, start_token + 1)

    return chunks
