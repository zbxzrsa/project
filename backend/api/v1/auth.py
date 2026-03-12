from datetime import timedelta
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from backend.core.exceptions import (
    ValidationException,
    ConflictException,
    UnauthorizedException,
    NotFoundException,
)
from backend.core.permissions import UserRole
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.models import Tenant, User
from backend.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from backend.core.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise ConflictException("Email already registered")

    if user_data.tenant_id is None:
        tenant = Tenant(name=f"Tenant-{user_data.email.split('@')[0]}")
        db.add(tenant)
        await db.flush()
        tenant_id = tenant.id
    else:
        tenant_id = user_data.tenant_id

    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.USER.value,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash or ""):
        raise UnauthorizedException("Invalid email or password")

    if user.is_active != "true":
        raise UnauthorizedException("User account is inactive")

    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(token_data.refresh_token)

    if payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid token type")

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    role = payload.get("role")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user or user.is_active != "true":
        raise UnauthorizedException("User not found or inactive")

    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == user.id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise NotFoundException("User", str(user.id))
    return current_user
