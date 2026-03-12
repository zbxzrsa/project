from typing import Optional, Dict, Any, List
import asyncio
from openai import AsyncOpenAI, RateLimitError, Timeout as OpenAITimeout

from backend.llm.base import LLMProvider, LLMResponse, LLMMessage, LLMError, LLMTimeoutError, LLMRateLimitError
from backend.core.config import settings


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key=api_key or settings.OPENAI_API_KEY)
        
        # Support custom base_url for LM Studio and other OpenAI-compatible APIs
        if base_url:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=base_url,
                timeout=settings.LLM_TIMEOUT_SECONDS,
                max_retries=3,
            )
        else:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=settings.LLM_TIMEOUT_SECONDS,
                max_retries=3,
            )
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @provider_name.setter
    def provider_name(self, value: str):
        self._provider_name = value

    async def generate(
        self,
        messages: List[LLMMessage],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[msg.model_dump() for msg in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id,
                }
            )
        except OpenAITimeout as e:
            raise LLMTimeoutError("Request timed out", self.provider_name, e)
        except RateLimitError as e:
            raise LLMRateLimitError("Rate limit exceeded", self.provider_name, e)
        except Exception as e:
            raise LLMError(f"Failed to generate: {str(e)}", self.provider_name, e)

    async def validate_connection(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
