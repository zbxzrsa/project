from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, get_current_active_user, require_permission
from backend.core.permissions import Permission
from backend.core.exceptions import NotFoundException, ForbiddenException
from backend.models import User
from backend.schemas import UserCreate, UserUpdate, UserResponse
from backend.core.security import get_password_hash


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user: CurrentUser = Depends(require_permission(Permission.READ_USER)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .where(User.tenant_id == user.tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user: CurrentUser = Depends(require_permission(Permission.READ_USER)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == user.tenant_id)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise NotFoundException("User", str(user_id))
    return db_user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: CurrentUser = Depends(require_permission(Permission.CREATE_USER)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ForbiddenException("Email already exists")

    new_user = User(
        id=UUID,
        tenant_id=user.tenant_id,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role.value if user_data.role else "user",
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: CurrentUser = Depends(require_permission(Permission.UPDATE_USER)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == user.tenant_id)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise NotFoundException("User", str(user_id))

    if user_data.email:
        db_user.email = user_data.email
    if user_data.full_name:
        db_user.full_name = user_data.full_name
    if user_data.password:
        db_user.password_hash = get_password_hash(user_data.password)
    if user_data.role:
        db_user.role = user_data.role.value
    if user_data.is_active is not None:
        db_user.is_active = "true" if user_data.is_active else "false"

    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(require_permission(Permission.DELETE_USER)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == user.tenant_id)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise NotFoundException("User", str(user_id))

    await db.delete(db_user)
    await db.commit()
