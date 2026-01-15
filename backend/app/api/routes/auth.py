"""
Authentication API routes - login, register, logout
"""

from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.database.models import User, ChatLog
from app.utils.auth import hash_password, verify_password, create_access_token
from app.config import settings


router = APIRouter()


# Request/Response models
class RegisterRequest(BaseModel):
    phone: str
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    is_verified: bool


class UserResponse(BaseModel):
    id: str
    phone: str
    full_name: Optional[str]
    is_verified: bool


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if phone already exists
    result = await db.execute(select(User).where(User.phone == request.phone))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    # Create new user
    user = User(
        phone=request.phone,
        password_hash=hash_password(request.password),
        full_name=request.full_name,
    )
    db.add(user)
    await db.flush()  # Flush to get user.id

    # Create empty chat log for user
    chat_log = ChatLog(user_id=user.id, messages=[])
    db.add(chat_log)

    await db.commit()
    await db.refresh(user)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "phone": user.phone},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        user_id=str(user.id),
        is_verified=user.is_verified
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with phone and password"""
    # Find user by phone
    result = await db.execute(select(User).where(User.phone == request.phone))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "phone": user.phone},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        user_id=str(user.id),
        is_verified=user.is_verified
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str,  # Will be replaced with proper auth dependency
    db: AsyncSession = Depends(get_db)
):
    """Get current user info"""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(user.id),
        phone=user.phone,
        full_name=user.full_name,
        is_verified=user.is_verified
    )
