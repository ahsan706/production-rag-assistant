from __future__ import annotations

import hashlib
import re
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/x-markdown",
    "application/octet-stream",
}


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name.strip()
    stem = Path(name).stem
    suffix = Path(name).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip(".-_")
    if not safe_stem:
        safe_stem = "document"
    return f"{safe_stem[:180]}{suffix}"


def validate_upload(file: UploadFile) -> tuple[str, str]:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required.")

    safe_name = sanitize_filename(file.filename)
    extension = Path(safe_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Upload PDF, TXT, or Markdown files.",
        )

    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported content type.",
        )

    return safe_name, extension


def save_document_upload(db: Session, file: UploadFile) -> tuple[Document, bool]:
    safe_name, extension = validate_upload(file)
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    temp_name = f"{uuid.uuid4()}.upload"
    temp_path = upload_dir / temp_name
    checksum = hashlib.sha256()
    size = 0

    try:
        with temp_path.open("wb") as output:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds {settings.max_upload_bytes} byte limit.",
                    )
                checksum.update(chunk)
                output.write(chunk)

        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty."
            )

        checksum_hex = checksum.hexdigest()
        existing = db.scalar(select(Document).where(Document.checksum_sha256 == checksum_hex))
        if existing:
            temp_path.unlink(missing_ok=True)
            return existing, True

        document_id = uuid.uuid4()
        stored_filename = f"{document_id}{extension}"
        storage_path = upload_dir / stored_filename
        shutil.move(str(temp_path), storage_path)

        document = Document(
            id=document_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            storage_path=str(storage_path),
            content_type=file.content_type or "application/octet-stream",
            file_extension=extension,
            size_bytes=size,
            checksum_sha256=checksum_hex,
            status="uploaded",
            document_metadata={"safe_filename": safe_name},
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document, False
    except HTTPException:
        temp_path.unlink(missing_ok=True)
        raise
    except IntegrityError:
        db.rollback()
        temp_path.unlink(missing_ok=True)
        existing = db.scalar(
            select(Document).where(Document.checksum_sha256 == checksum.hexdigest())
        )
        if existing:
            return existing, True
        raise
    finally:
        file.file.close()
