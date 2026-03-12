from typing import Optional, List, Dict, Any
from enum import Enum
import asyncio

from backend.llm.base import LLMProvider, LLMResponse, LLMMessage, LLMError, LLMTimeoutError, LLMRateLimitError
from backend.llm.openai import OpenAIProvider
from backend.llm.anthropic import AnthropicProvider
from backend.llm.ollama import OllamaProvider
from backend.core.logging import logger
from backend.core.config import settings


class LLMProviderType(str, Enum):
    INTERNAL_OLLAMA = "internal_ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMRouter:
    def __init__(
        self,
        providers: Optional[List[LLMProvider]] = None,
        primary_provider: LLMProviderType = LLMProviderType.INTERNAL_OLLAMA,
        user_api_key: Optional[str] = None,
    ):
        self.providers: Dict[LLMProviderType, LLMProvider] = {}
        self._user_api_key = user_api_key
        
        if providers:
            for provider in providers:
                self.providers[provider.provider_name] = provider
        else:
            self._initialize_default_providers()
        
        self.primary = primary_provider
        self.fallback_order = self._parse_provider_order()
    
    def _parse_provider_order(self) -> List[LLMProviderType]:
        """Parse provider order from settings."""
        order = []
        for name in settings.LLM_PROVIDER_ORDER.split(","):
            name = name.strip()
            try:
                order.append(LLMProviderType(name))
            except ValueError:
                logger.warning(f"Unknown LLM provider: {name}")
        return order
    
    def _initialize_default_providers(self):
        """Initialize all available LLM providers."""
        
        # 1. Internal Ollama (Priority 1)
        try:
            internal_ollama = OllamaProvider(
                base_url=settings.INTERNAL_OLLAMA_URL,
                model=settings.INTERNAL_OLLAMA_MODEL
            )
            self.providers[LLMProviderType.INTERNAL_OLLAMA] = internal_ollama
            logger.info(f"Initialized internal Ollama: {settings.INTERNAL_OLLAMA_URL}")
        except Exception as e:
            logger.warning(f"Failed to initialize internal Ollama: {e}")
        
        # 2. OpenAI - use user's key first, then default key
        try:
            api_key = self._user_api_key or settings.OPENAI_API_KEY or settings.DEFAULT_OPENAI_API_KEY
            if api_key:
                openai = OpenAIProvider(api_key=api_key)
                self.providers[LLMProviderType.OPENAI] = openai
                logger.info("Initialized OpenAI provider")
            else:
                logger.warning("No OpenAI API key available")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI provider: {e}")
        
        # 3. Anthropic
        try:
            if settings.ANTHROPIC_API_KEY:
                anthropic = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
                self.providers[LLMProviderType.ANTHROPIC] = anthropic
                logger.info("Initialized Anthropic provider")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic provider: {e}")
        
        # 4. Local Ollama
        try:
            ollama = OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL
            )
            self.providers[LLMProviderType.OLLAMA] = ollama
            logger.info(f"Initialized local Ollama: {settings.OLLAMA_BASE_URL}")
        except Exception as e:
            logger.warning(f"Failed to initialize local Ollama: {e}")
    
    def set_user_api_key(self, api_key: str):
        """Set user-provided API key and reinitialize OpenAI provider."""
        self._user_api_key = api_key
        if LLMProviderType.OPENAI in self.providers:
            del self.providers[LLMProviderType.OPENAI]
        
        try:
            openai = OpenAIProvider(api_key=api_key)
            self.providers[LLMProviderType.OPENAI] = openai
            logger.info("Updated OpenAI provider with user API key")
        except Exception as e:
            logger.warning(f"Failed to update OpenAI provider: {e}")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        provider: Optional[LLMProviderType] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        errors = []
        
        providers_to_try = [provider] if provider else self._get_fallback_order()
        
        for provider_type in providers_to_try:
            if provider_type not in self.providers:
                continue
            
            llm_provider = self.providers[provider_type]
            
            try:
                logger.info(f"Attempting to generate with {provider_type}")
                
                # Use provider-specific model if not specified
                actual_model = model or self._get_default_model(provider_type)
                
                response = await llm_provider.generate(
                    messages=messages,
                    model=actual_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                logger.info(f"Successfully generated with {provider_type}")
                return response
                
            except LLMTimeoutError as e:
                logger.warning(f"Timeout from {provider_type}: {e.message}")
                errors.append(e)
                continue
                
            except LLMRateLimitError as e:
                logger.warning(f"Rate limit from {provider_type}: {e.message}")
                errors.append(e)
                continue
                
            except LLMError as e:
                logger.error(f"Error from {provider_type}: {e.message}")
                errors.append(e)
                continue
        
        raise LLMError(
            message=f"All providers failed. Errors: {[e.message for e in errors]}",
            provider="all"
        )
    
    def _get_fallback_order(self) -> List[LLMProviderType]:
        """Get provider fallback order based on priority."""
        order = []
        
        # Add primary first
        if self.primary in self.providers:
            order.append(self.primary)
        
        # Add rest in configured order
        for provider_type in self.fallback_order:
            if provider_type != self.primary and provider_type in self.providers:
                order.append(provider_type)
        
        return order
    
    def _get_default_model(self, provider: LLMProviderType) -> str:
        """Get default model for provider."""
        defaults = {
            LLMProviderType.INTERNAL_OLLAMA: settings.INTERNAL_OLLAMA_MODEL,
            LLMProviderType.OPENAI: "gpt-4o",
            LLMProviderType.ANTHROPIC: "claude-sonnet-4-20250514",
            LLMProviderType.OLLAMA: settings.OLLAMA_MODEL,
        }
        return defaults.get(provider, "gpt-4o")
    
    async def validate_all_providers(self) -> Dict[str, bool]:
        """Validate all available providers."""
        results = {}
        
        for provider_type, provider in self.providers.items():
            try:
                results[provider_type.value] = await provider.validate_connection()
            except Exception as e:
                logger.error(f"Failed to validate {provider_type}: {e}")
                results[provider_type.value] = False
        
        return results
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [p.value for p in self.providers.keys()]
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        status = {}
        for provider_type in LLMProviderType:
            status[provider_type.value] = {
                "available": provider_type in self.providers,
                "is_primary": provider_type == self.primary,
            }
        return status


# Global router instance with user API key support
_llm_router: Optional[LLMRouter] = None


def get_llm_router(user_api_key: Optional[str] = None) -> LLMRouter:
    """Get or create LLM router with optional user API key."""
    global _llm_router
    
    if user_api_key:
        # Create new router with user key
        return LLMRouter(user_api_key=user_api_key)
    
    if _llm_router is None:
        _llm_router = LLMRouter()
    
    return _llm_router


llm_router = get_llm_router()
