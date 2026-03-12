from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, require_permission
from backend.core.permissions import Permission
from backend.core.exceptions import NotFoundException
from backend.models import Tenant
from backend.schemas import TenantCreate, TenantUpdate, TenantResponse


router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    user: CurrentUser = Depends(require_permission(Permission.READ_TENANT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    user: CurrentUser = Depends(require_permission(Permission.READ_TENANT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise NotFoundException("Tenant", str(tenant_id))
    return tenant


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    user: CurrentUser = Depends(require_permission(Permission.CREATE_TENANT)),
    db: AsyncSession = Depends(get_db),
):
    tenant = Tenant(**tenant_data.model_dump())
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    user: CurrentUser = Depends(require_permission(Permission.UPDATE_TENANT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise NotFoundException("Tenant", str(tenant_id))

    update_data = tenant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)
    return tenant
