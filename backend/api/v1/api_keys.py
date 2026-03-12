from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyWithSecret
from backend.services import api_key as api_key_service


router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new API key."""
    return await api_key_service.create_api_key(
        db=db,
        user_id=user.id,
        tenant_id=user.tenant_id,
        key_data=key_data,
    )


@router.get("", response_model=List[APIKeyResponse])
async def list_api_keys(
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all API keys for the current user."""
    return await api_key_service.list_api_keys(
        db=db,
        user_id=user.id,
        tenant_id=user.tenant_id,
    )


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    api_key_id: UUID,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an API key."""
    success = await api_key_service.revoke_api_key(
        db=db,
        api_key_id=str(api_key_id),
        user_id=user.id,
        tenant_id=user.tenant_id,
    )
    if not success:
        from backend.core.exceptions import NotFoundException
        raise NotFoundException("API Key", str(api_key_id))
