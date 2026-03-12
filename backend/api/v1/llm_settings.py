from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from backend.llm import LLMProviderType, get_llm_router, llm_router
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.core.permissions import Permission


router = APIRouter(prefix="/llm", tags=["LLM Settings"])


class LLMProviderStatus(BaseModel):
    provider: str
    available: bool
    is_primary: bool
    models: Optional[List[str]] = None


class SetUserAPIKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=10, description="User's OpenAI API key")


class LLMGenerateRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class LLMGenerateResponse(BaseModel):
    content: str
    model: str
    usage: Dict[str, int]
    provider: str


@router.get("/providers/status", response_model=List[LLMProviderStatus])
async def get_providers_status(
    user: CurrentUser = Depends(get_current_active_user),
):
    """Get status of all LLM providers."""
    router = get_llm_router()
    status = router.get_provider_status()
    
    result = []
    for provider_name, info in status.items():
        result.append(LLMProviderStatus(
            provider=provider_name,
            available=info["available"],
            is_primary=info["is_primary"],
        ))
    
    return result


@router.post("/api-key", status_code=200)
async def set_user_api_key(
    request: SetUserAPIKeyRequest,
    user: CurrentUser = Depends(get_current_active_user),
):
    """Set user's custom API key for LLM calls."""
    router = get_llm_router(user_api_key=request.api_key)
    
    return {
        "message": "API key updated successfully",
        "provider": "openai",
    }


@router.delete("/api-key", status_code=200)
async def reset_user_api_key(
    user: CurrentUser = Depends(get_current_active_user),
):
    """Reset to default API key."""
    global llm_router
    llm_router = get_llm_router()
    
    return {
        "message": "API key reset to default",
    }


@router.post("/generate", response_model=LLMGenerateResponse)
async def generate_with_llm(
    request: LLMGenerateRequest,
    user: CurrentUser = Depends(get_current_active_user),
):
    """Generate response from LLM."""
    from backend.llm import LLMMessage
    
    router = get_llm_router()
    
    messages = [
        LLMMessage(role=msg["role"], content=msg["content"])
        for msg in request.messages
    ]
    
    try:
        response = await router.generate(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        return LLMGenerateResponse(
            content=response.content,
            model=response.model,
            usage=response.usage or {},
            provider=router.primary.value,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")


@router.get("/models")
async def list_available_models(
    user: CurrentUser = Depends(get_current_active_user),
):
    """List available models for each provider."""
    router = get_llm_router()
    
    result = {}
    for provider_type, provider in router.providers.items():
        try:
            if hasattr(provider, 'list_models'):
                models = await provider.list_models()
                result[provider_type.value] = models
            else:
                result[provider_type.value] = [router._get_default_model(provider_type)]
        except Exception:
            result[provider_type.value] = []
    
    return result
