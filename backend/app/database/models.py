"""
Database models for the eKYC system
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database.connection import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    ekyc_records: Mapped[list["EKYCRecord"]] = relationship(
        "EKYCRecord", back_populates="user", cascade="all, delete-orphan"
    )
    chat_log: Mapped[Optional["ChatLog"]] = relationship(
        "ChatLog", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class EKYCRecord(Base):
    """eKYC verification record"""
    __tablename__ = "ekyc_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    id_card_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    selfie_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    face_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ekyc_records")


class ChatLog(Base):
    """Chat history log for debugging"""
    __tablename__ = "chat_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,  # One chat log per user
        nullable=False
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

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_log")
