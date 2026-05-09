from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class EmptyDocumentError(ValueError):
    pass


def extract_text(path: str, extension: str) -> str:
    file_path = Path(path)
    if extension in {".txt", ".md", ".markdown"}:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    elif extension == ".pdf":
        reader = PdfReader(str(file_path))
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(f"[Page {index}]\\n{page_text.strip()}")
        text = "\\n\\n".join(pages)
    else:
        raise ValueError(f"Unsupported extension for extraction: {extension}")

    normalized = text.strip()
    if not normalized:
        raise EmptyDocumentError("Document contains no extractable text.")
    return normalized
