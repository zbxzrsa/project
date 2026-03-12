from typing import Optional, List, Dict, Any
from enum import Enum
import asyncio

from backend.llm.base import LLMProvider, LLMResponse, LLMMessage, LLMError, LLMTimeoutError, LLMRateLimitError
from backend.llm.openai import OpenAIProvider
from backend.llm.anthropic import AnthropicProvider
from backend.llm.ollama import OllamaProvider
from backend.core.logging import logger


class LLMProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMRouter:
    def __init__(
        self,
        providers: Optional[List[LLMProvider]] = None,
        primary_provider: LLMProviderType = LLMProviderType.OPENAI
    ):
        self.providers: Dict[LLMProviderType, LLMProvider] = {}
        
        if providers:
            for provider in providers:
                self.providers[provider.provider_name] = provider
        else:
            self._initialize_default_providers()
        
        self.primary = primary_provider
        self.fallback_order = [
            LLMProviderType.OPENAI,
            LLMProviderType.ANTHROPIC,
            LLMProviderType.OLLAMA,
        ]

    def _initialize_default_providers(self):
        try:
            openai = OpenAIProvider()
            self.providers[LLMProviderType.OPENAI] = openai
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI provider: {e}")

        try:
            anthropic = AnthropicProvider()
            self.providers[LLMProviderType.ANTHROPIC] = anthropic
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic provider: {e}")

        try:
            ollama = OllamaProvider()
            self.providers[LLMProviderType.OLLAMA] = ollama
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama provider: {e}")

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
                response = await llm_provider.generate(
                    messages=messages,
                    model=model or self._get_default_model(provider_type),
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
        order = []
        found_primary = False
        
        for provider_type in self.fallback_order:
            if provider_type == self.primary:
                found_primary = True
                order.insert(0, provider_type)
            elif provider_type in self.providers:
                order.append(provider_type)
        
        if not found_primary and self.primary in self.providers:
            order.insert(0, self.primary)
            
        return order

    def _get_default_model(self, provider: LLMProviderType) -> str:
        defaults = {
            LLMProviderType.OPENAI: "gpt-4",
            LLMProviderType.ANTHROPIC: "claude-3-sonnet-20240229",
            LLMProviderType.OLLAMA: "llama2",
        }
        return defaults.get(provider, "gpt-4")

    async def validate_all_providers(self) -> Dict[str, bool]:
        results = {}
        
        for provider_type, provider in self.providers.items():
            try:
                results[provider_type] = await provider.validate_connection()
            except Exception as e:
                logger.error(f"Failed to validate {provider_type}: {e}")
                results[provider_type] = False
        
        return results

    def get_available_providers(self) -> List[str]:
        return [p.value for p in self.providers.keys()]


llm_router = LLMRouter()
