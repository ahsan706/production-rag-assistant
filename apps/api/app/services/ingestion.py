from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.ingestion_job import IngestionJob
from app.worker import celery_app


def create_ingestion_job(db: Session, document: Document) -> IngestionJob:
    job = IngestionJob(
        document_id=document.id,
        status="queued",
        attempts=0,
        max_attempts=3,
        logs=[{"at": datetime.now(UTC).isoformat(), "message": "Ingestion job queued."}],
    )
    document.status = "queued"
    document.error_message = None
    db.add(job)
    db.commit()
    db.refresh(job)
    db.refresh(document)

    celery_app.send_task("ingestion.process_document", args=[str(job.id)])
    return job
