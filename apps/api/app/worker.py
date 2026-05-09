from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path
from uuid import UUID

from celery import Celery
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.ingestion_job import IngestionJob
from app.services.chunks import replace_document_chunks
from app.services.embeddings import get_embedding_provider
from app.services.extraction import EmptyDocumentError, extract_text
from app.services.vector_store import get_vector_store

configure_logging()
logger = logging.getLogger(__name__)

celery_app = Celery("production_rag_worker", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)


def _log(job: IngestionJob, message: str) -> None:
    logs = list(job.logs or [])
    logs.append({"at": datetime.now(timezone.utc).isoformat(), "message": message})
    job.logs = logs
    flag_modified(job, "logs")


@celery_app.task(name="health.ping")
def ping() -> str:
    return "pong"


@celery_app.task(bind=True, name="ingestion.process_document", max_retries=2)
def process_document(self, job_id: str) -> str:
    db = SessionLocal()
    try:
        job = db.get(IngestionJob, UUID(job_id))
        if job is None:
            raise ValueError(f"Ingestion job not found: {job_id}")

        document = db.get(Document, job.document_id)
        if document is None:
            raise ValueError(f"Document not found for ingestion job: {job_id}")

        now = datetime.now(timezone.utc)
        job.status = "running"
        job.started_at = job.started_at or now
        job.attempts = self.request.retries + 1
        job.error_message = None
        document.status = "processing"
        document.error_message = None
        _log(job, f"Starting extraction attempt {job.attempts}.")
        db.commit()
        logger.info(
            "ingestion_started",
            extra={"job_id": str(job.id), "document_id": str(document.id), "attempt": job.attempts},
        )

        text = extract_text(document.storage_path, document.file_extension)
        extraction_dir = Path(settings.extraction_dir)
        extraction_dir.mkdir(parents=True, exist_ok=True)
        extracted_path = extraction_dir / f"{document.id}.txt"
        extracted_path.write_text(text, encoding="utf-8")
        chunks = replace_document_chunks(db, document, text)

        metadata = dict(document.document_metadata or {})
        metadata["extraction"] = {
            "text_path": str(extracted_path),
            "character_count": len(text),
        }
        metadata["chunking"] = {
            "strategy": "fixed_token_window",
            "chunk_tokens": 800,
            "overlap_tokens": 150,
            "chunk_count": len(chunks),
        }
        document.document_metadata = metadata
        flag_modified(document, "document_metadata")
        document.extracted_text_path = str(extracted_path)
        db.flush()

        provider = get_embedding_provider()
        vector_store = get_vector_store()
        vector_store.ensure_collection()
        embeddings = provider.embed_texts([chunk.text for chunk in chunks])
        vector_store.upsert_chunks(document, chunks, embeddings)
        embedded_at = datetime.now(timezone.utc)
        for chunk in chunks:
            chunk.vector_point_id = chunk.id
            chunk.embedding_model = settings.ai_embedding_model
            chunk.embedded_at = embedded_at

        document.status = "embedded"
        job.status = "succeeded"
        job.completed_at = datetime.now(timezone.utc)
        _log(job, f"Extraction completed with {len(text)} characters.")
        _log(job, f"Chunking completed with {len(chunks)} chunks.")
        _log(job, f"Embedding completed for {len(chunks)} chunks.")
        db.commit()
        logger.info(
            "ingestion_succeeded",
            extra={
                "job_id": str(job.id),
                "document_id": str(document.id),
                "chunk_count": len(chunks),
                "embedding_model": settings.ai_embedding_model,
            },
        )
        return str(document.id)
    except EmptyDocumentError as exc:
        if "job" in locals():
            job.status = "failed"
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            _log(job, str(exc))
        if "document" in locals():
            document.status = "failed"
            document.error_message = str(exc)
        db.commit()
        logger.warning("ingestion_failed_empty_document", extra={"job_id": job_id, "error": str(exc)})
        return job_id
    except Exception as exc:
        if "job" in locals():
            job.attempts = self.request.retries + 1
            job.error_message = str(exc)
            _log(job, f"Extraction failed: {exc}")
            logger.warning(
                "ingestion_attempt_failed",
                extra={
                    "job_id": job_id,
                    "attempt": self.request.retries + 1,
                    "max_retries": self.max_retries,
                    "error_type": exc.__class__.__name__,
                    "error": str(exc),
                },
            )
            if self.request.retries < self.max_retries:
                job.status = "retrying"
                if "document" in locals():
                    document.status = "processing"
                    document.error_message = str(exc)
                db.commit()
                raise self.retry(exc=exc, countdown=1)

            job.status = "failed"
            job.completed_at = datetime.now(timezone.utc)
        if "document" in locals():
            document.status = "failed"
            document.error_message = str(exc)
        db.commit()
        return job_id
    except MaxRetriesExceededError:
        return job_id
    finally:
        db.close()
