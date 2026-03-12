from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from backend.core.permissions import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    tenant_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    tenant_id: UUID
    role: str
    is_active: str
    is_superuser: str
    created_at: datetime
    updated_at: datetime
    github_id: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class OAuthUrlResponse(BaseModel):
    url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str


class GitHubUser(BaseModel):
    id: int
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
