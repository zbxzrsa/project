from typing import Optional, Dict, Any, List
import httpx

from backend.llm.base import LLMProvider, LLMResponse, LLMMessage, LLMError, LLMTimeoutError
from backend.core.config import settings


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url or settings.OLLAMA_BASE_URL
        )
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )
        self.default_model = settings.OLLAMA_MODEL

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def generate(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        try:
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            request_data = {
                "model": model or self.default_model,
                "messages": formatted_messages,
                "temperature": temperature,
                "stream": False,
            }
            
            if max_tokens:
                request_data["options"] = {"num_predict": max_tokens}
            
            request_data.update(kwargs)
            
            response = await self.client.post("/api/chat", json=request_data)
            response.raise_for_status()
            
            data = response.json()
            
            return LLMResponse(
                content=data.get("message", {}).get("content", ""),
                model=data.get("model", self.default_model),
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                },
                metadata={
                    "done": data.get("done", True),
                }
            )
        except httpx.TimeoutException as e:
            raise LLMTimeoutError("Request timed out", self.provider_name, e)
        except httpx.HTTPStatusError as e:
            raise LLMError(f"HTTP error: {e.response.status_code}", self.provider_name, e)
        except Exception as e:
            raise LLMError(f"Failed to generate: {str(e)}", self.provider_name, e)

    async def validate_connection(self) -> bool:
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        try:
            response = await self.client.get("/api/tags")
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []
