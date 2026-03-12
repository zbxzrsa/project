from typing import Optional, Dict, Any, List
import anthropic

from backend.llm.base import LLMProvider, LLMResponse, LLMMessage, LLMError, LLMTimeoutError, LLMRateLimitError
from backend.core.config import settings


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key or settings.ANTHROPIC_API_KEY)
        self.client = anthropic.AsyncAnthropic(
            api_key=self.api_key,
            timeout=settings.LLM_TIMEOUT_SECONDS,
            max_retries=3,
        )

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def generate(
        self,
        messages: List[LLMMessage],
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        try:
            system_message = ""
            filtered_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    filtered_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model,
                system=system_message,
                messages=[{"role": msg.role, "content": msg.content} for msg in filtered_messages],
                temperature=temperature,
                max_tokens=max_tokens or 4096,
                **kwargs
            )
            
            content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
            
            return LLMResponse(
                content=content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                metadata={
                    "stop_reason": response.stop_reason,
                    "id": response.id,
                }
            )
        except anthropic.APIConnectionError as e:
            raise LLMTimeoutError("Connection error", self.provider_name, e)
        except anthropic.RateLimitError as e:
            raise LLMRateLimitError("Rate limit exceeded", self.provider_name, e)
        except Exception as e:
            raise LLMError(f"Failed to generate: {str(e)}", self.provider_name, e)

    async def validate_connection(self) -> bool:
        try:
            await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
