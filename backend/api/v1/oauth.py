from urllib.parse import urlencode
import httpx
import secrets
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from backend.core.exceptions import (
    ConflictException,
    UnauthorizedException,
)
from backend.core.permissions import UserRole
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.models import Tenant, User
from backend.schemas import (
    OAuthUrlResponse,
    OAuthCallbackRequest,
    TokenResponse,
    UserResponse,
    GitHubUser,
)
from backend.core.config import settings


router = APIRouter(prefix="/oauth", tags=["OAuth"])

GITHUB_OAUTH_STATES: dict[str, dict] = {}


def get_github_authorization_url() -> tuple[str, str]:
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "user:email read:user",
        "state": state,
    }
    GITHUB_OAUTH_STATES[state] = {"created_at": "now"}
    return f"https://github.com/login/oauth/authorize?{urlencode(params)}", state


async def exchange_code_for_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:
            raise UnauthorizedException("Failed to exchange code for token")
        
        data = response.json()
        return data.get("access_token")


async def get_github_user(access_token: str) -> GitHubUser:
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        
        user_response = await client.get(
            "https://api.github.com/user",
            headers=headers,
        )
        if user_response.status_code != 200:
            raise UnauthorizedException("Failed to get GitHub user info")
        
        user_data = user_response.json()
        
        email = user_data.get("email")
        if not email:
            emails_response = await client.get(
                "https://api.github.com/user/emails",
                headers=headers,
            )
            if emails_response.status_code == 200:
                emails = emails_response.json()
                primary_email = next(
                    (e["email"] for e in emails if e.get("primary")), None
                )
                email = primary_email or (emails[0]["email"] if emails else None)
        
        return GitHubUser(
            id=user_data["id"],
            login=user_data["login"],
            name=user_data.get("name"),
            email=email,
            avatar_url=user_data.get("avatar_url"),
        )


@router.get("/github", response_model=OAuthUrlResponse)
async def github_oauth_start():
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured",
        )
    
    url, state = get_github_authorization_url()
    return OAuthUrlResponse(url=url, state=state)


@router.post("/github/callback", response_model=TokenResponse)
async def github_oauth_callback(
    callback_data: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    state = callback_data.state
    if state not in GITHUB_OAUTH_STATES:
        raise UnauthorizedException("Invalid OAuth state")
    
    del GITHUB_OAUTH_STATES[state]
    
    access_token = await exchange_code_for_token(callback_data.code)
    github_user = await get_github_user(access_token)
    
    result = await db.execute(
        select(User).where(User.github_id == str(github_user.id))
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.github_access_token = access_token
        await db.commit()
    else:
        result = await db.execute(
            select(User).where(User.email == github_user.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            existing_user.github_id = str(github_user.id)
            existing_user.github_access_token = access_token
            if github_user.avatar_url:
                existing_user.avatar_url = github_user.avatar_url
            await db.commit()
            user = existing_user
        else:
            tenant = Tenant(name=f"Tenant-{github_user.login}")
            db.add(tenant)
            await db.flush()
            
            user = User(
                id=str(uuid4()),
                tenant_id=tenant.id,
                email=github_user.email or f"{github_user.login}@github.local",
                full_name=github_user.name or github_user.login,
                github_id=str(github_user.id),
                github_access_token=access_token,
                avatar_url=github_user.avatar_url,
                role=UserRole.USER.value,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
    
    jwt_access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    )
    
    return TokenResponse(
        access_token=jwt_access_token,
        refresh_token=refresh_token,
    )


@router.post("/github/link", response_model=UserResponse)
async def link_github_account(
    callback_data: OAuthCallbackRequest,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    access_token = await exchange_code_for_token(callback_data.code)
    github_user = await get_github_user(access_token)
    
    result = await db.execute(
        select(User).where(User.github_id == str(github_user.id))
    )
    existing_github_user = result.scalar_one_or_none()
    
    if existing_github_user and existing_github_user.id != user.id:
        raise ConflictException("This GitHub account is already linked to another user")
    
    result = await db.execute(
        select(User).where(User.id == user.id)
    )
    current_user = result.scalar_one_or_none()
    
    current_user.github_id = str(github_user.id)
    current_user.github_access_token = access_token
    if github_user.avatar_url:
        current_user.avatar_url = github_user.avatar_url
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.delete("/github/unlink", response_model=UserResponse)
async def unlink_github_account(
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == user.id)
    )
    current_user = result.scalar_one_or_none()
    
    if not current_user.github_id:
        raise UnauthorizedException("GitHub account is not linked")
    
    current_user.github_id = None
    current_user.github_access_token = None
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user
