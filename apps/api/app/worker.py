from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from celery import Celery
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.ingestion_job import IngestionJob
from app.services.extraction import EmptyDocumentError, extract_text

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

        text = extract_text(document.storage_path, document.file_extension)
        extraction_dir = Path(settings.extraction_dir)
        extraction_dir.mkdir(parents=True, exist_ok=True)
        extracted_path = extraction_dir / f"{document.id}.txt"
        extracted_path.write_text(text, encoding="utf-8")

        metadata = dict(document.document_metadata or {})
        metadata["extraction"] = {
            "text_path": str(extracted_path),
            "character_count": len(text),
        }
        document.document_metadata = metadata
        flag_modified(document, "document_metadata")
        document.extracted_text_path = str(extracted_path)
        document.status = "ready"
        job.status = "succeeded"
        job.completed_at = datetime.now(timezone.utc)
        _log(job, f"Extraction completed with {len(text)} characters.")
        db.commit()
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
        return job_id
    except Exception as exc:
        if "job" in locals():
            job.attempts = self.request.retries + 1
            job.error_message = str(exc)
            _log(job, f"Extraction failed: {exc}")
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
