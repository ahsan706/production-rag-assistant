from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: uuid.UUID
    original_filename: str
    content_type: str
    file_extension: str
    size_bytes: int
    checksum_sha256: str
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    duplicate: bool
