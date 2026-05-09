"""add chunk vector fields

Revision ID: 0004_add_chunk_vector_fields
Revises: 0003_create_chunks
Create Date: 2026-05-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_add_chunk_vector_fields"
down_revision: Union[str, None] = "0003_create_chunks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("chunks", sa.Column("vector_point_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("chunks", sa.Column("embedding_model", sa.String(length=120), nullable=True))
    op.add_column("chunks", sa.Column("embedded_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_chunks_vector_point_id", "chunks", ["vector_point_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_chunks_vector_point_id", table_name="chunks")
    op.drop_column("chunks", "embedded_at")
    op.drop_column("chunks", "embedding_model")
    op.drop_column("chunks", "vector_point_id")
