from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: uuid.UUID
    original_filename: str
    stored_filename: str
    content_type: str
    file_extension: str
    size_bytes: int
    checksum_sha256: str
    status: str
    error_message: str | None
    extracted_text_path: str | None
    document_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    duplicate: bool
