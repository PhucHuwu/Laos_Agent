"""
Database models for the eKYC system
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database.connection import Base


class EKYCRecord(Base):
    """eKYC verification record"""
    __tablename__ = "ekyc_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    # Changed: session_id instead of user_id with foreign key
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    id_card_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    selfie_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    face_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChatLog(Base):
    """Chat history log"""
    __tablename__ = "chat_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    # Changed: session_id instead of user_id with foreign key
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,  # One chat log per session
        nullable=False,
        index=True
    )
    messages: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    context: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    progress: Mapped[str] = mapped_column(String(50), default="idle")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
