from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request

from backend.core.security import get_current_user
from backend.core.permissions import UserRole, Permission, has_permission
from backend.core.exceptions import ForbiddenException, UnauthorizedException


class CurrentUser:
    def __init__(self, id: UUID, tenant_id: UUID, role: str):
        self.id = id
        self.tenant_id = tenant_id
        self.role = UserRole(role) if role else UserRole.USER


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> CurrentUser:
    if not current_user:
        raise UnauthorizedException()
    return CurrentUser(
        id=UUID(current_user["id"]),
        tenant_id=UUID(current_user["tenant_id"]),
        role=current_user["role"],
    )


def require_permission(permission: Permission):
    async def permission_checker(
        user: CurrentUser = Depends(get_current_active_user),
    ) -> CurrentUser:
        if not has_permission(user.role, permission):
            raise ForbiddenException(
                f"Permission denied: {permission.value} is required"
            )
        return user
    return permission_checker


def require_role(allowed_roles: list[UserRole]):
    async def role_checker(
        user: CurrentUser = Depends(get_current_active_user),
    ) -> CurrentUser:
        if user.role not in allowed_roles:
            raise ForbiddenException(
                f"Role {user.role.value} is not allowed to access this resource"
            )
        return user
    return role_checker


async def get_tenant_id(
    user: CurrentUser = Depends(get_current_active_user),
) -> UUID:
    return user.tenant_id
