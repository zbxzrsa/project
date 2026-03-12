import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.api_key import APIKey
from backend.schemas.api_key import APIKeyCreate, APIKeyWithSecret


def generate_api_key() -> tuple[str, str]:
    """Generate a new API key and its prefix."""
    key = f"sk_{secrets.token_urlsafe(32)}"
    prefix = key[:12]
    return key, prefix


def hash_api_key(key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(key.encode()).hexdigest()


async def create_api_key(
    db: AsyncSession,
    user_id: str,
    tenant_id: str,
    key_data: APIKeyCreate,
) -> APIKeyWithSecret:
    """Create a new API key."""
    key, prefix = generate_api_key()
    key_hash = hash_api_key(key)
    
    expires_at = None
    if key_data.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_days)
    
    api_key = APIKey(
        id=str(uuid4()),
        tenant_id=tenant_id,
        user_id=user_id,
        name=key_data.name,
        key_hash=key_hash,
        prefix=prefix,
        expires_at=expires_at,
    )
    
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    return APIKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        key=key,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
    )


async def list_api_keys(
    db: AsyncSession,
    user_id: str,
    tenant_id: str,
) -> List[APIKey]:
    """List all API keys for a user."""
    result = await db.execute(
        select(APIKey)
        .where(APIKey.user_id == user_id, APIKey.tenant_id == tenant_id)
        .order_by(APIKey.created_at.desc())
    )
    return result.scalars().all()


async def revoke_api_key(
    db: AsyncSession,
    api_key_id: str,
    user_id: str,
    tenant_id: str,
) -> bool:
    """Revoke an API key."""
    result = await db.execute(
        select(APIKey)
        .where(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id,
            APIKey.tenant_id == tenant_id,
        )
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        return False
    
    api_key.is_active = False
    await db.commit()
    return True


async def verify_api_key(
    db: AsyncSession,
    key: str,
) -> Optional[APIKey]:
    """Verify an API key and return the associated APIKey object."""
    key_hash = hash_api_key(key)
    
    result = await db.execute(
        select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        return None
    
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        return None
    
    api_key.last_used_at = datetime.utcnow()
    await db.commit()
    
    return api_key
