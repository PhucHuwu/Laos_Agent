"""
EKYC Profile API routes - fetch user's ekyc records for sidebar display
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.api.deps_auth import get_current_user_id
from app.database import get_db
from app.database.models import EKYCRecord


router = APIRouter()


class EKYCProfileResponse(BaseModel):
    """Response model for ekyc profile"""
    success: bool
    is_verified: bool = False
    id_card_image_url: Optional[str] = None
    selfie_image_url: Optional[str] = None
    ocr_data: Optional[dict] = None
    face_match_score: Optional[float] = None
    verified_at: Optional[str] = None
    error: Optional[str] = None


@router.get("/ekyc/profile", response_model=EKYCProfileResponse)
async def get_ekyc_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the latest eKYC profile for authenticated user.
    Returns OCR data extracted from ID card for sidebar display.
    """
    try:
        # Get latest ekyc record for user (ordered by created_at desc)
        result = await db.execute(
            select(EKYCRecord)
            .where(EKYCRecord.user_id == UUID(user_id))
            .order_by(EKYCRecord.created_at.desc())
            .limit(1)
        )
        record = result.scalar_one_or_none()

        if not record:
            return EKYCProfileResponse(
                success=True,
                is_verified=False,
                ocr_data=None
            )

        return EKYCProfileResponse(
            success=True,
            is_verified=record.is_verified,
            id_card_image_url=record.id_card_image_url,
            selfie_image_url=record.selfie_image_url,
            ocr_data=record.ocr_data,
            face_match_score=record.face_match_score,
            verified_at=record.verified_at.isoformat() if record.verified_at else None
        )

    except Exception as e:
        return EKYCProfileResponse(success=False, error=str(e))
