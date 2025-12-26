"""
Inference Client
================

Client for vLLM or OpenAI-compatible inference servers.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional, AsyncIterator
import httpx


@dataclass
class InferenceConfig:
    """Configuration for inference."""
    url: str = "http://localhost:8000"
    model: str = "deepseek-ai/deepseek-coder-6.7b-instruct"
    max_tokens: int = 4096
    temperature: float = 0.1
    top_p: float = 0.95
    timeout_seconds: int = 120


@dataclass
class CompletionResult:
    """Result of a completion request."""
    text: str
    tokens_used: int = 0
    finish_reason: str = "stop"
    model: str = ""
    latency_ms: int = 0


class InferenceClient:
    """
    Client for LLM inference.

    Supports:
    - vLLM (OpenAI-compatible API)
    - OpenAI API
    - Local Ollama
    """

    def __init__(self, config: Optional[InferenceConfig] = None):
        self.config = config or InferenceConfig()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.url,
                timeout=self.config.timeout_seconds,
            )
        return self._client

    async def close(self):
        """Close the client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def complete(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[list[str]] = None,
    ) -> CompletionResult:
        """
        Generate a completion.

        Args:
            prompt: The prompt to complete
            max_tokens: Override max tokens
            temperature: Override temperature
            stop: Stop sequences

        Returns:
            CompletionResult with generated text
        """
        import time

        client = await self._get_client()
        start = time.monotonic()

        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "top_p": self.config.top_p,
        }
        if stop:
            payload["stop"] = stop

        response = await client.post("/v1/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        latency_ms = int((time.monotonic() - start) * 1000)

        choice = data["choices"][0]
        return CompletionResult(
            text=choice["text"],
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
            model=data.get("model", self.config.model),
            latency_ms=latency_ms,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> CompletionResult:
        """
        Generate a chat completion.

        Args:
            messages: List of {"role": "...", "content": "..."}
            max_tokens: Override max tokens
            temperature: Override temperature

        Returns:
            CompletionResult with generated text
        """
        import time

        client = await self._get_client()
        start = time.monotonic()

        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "top_p": self.config.top_p,
        }

        response = await client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        latency_ms = int((time.monotonic() - start) * 1000)

        choice = data["choices"][0]
        return CompletionResult(
            text=choice["message"]["content"],
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
            model=data.get("model", self.config.model),
            latency_ms=latency_ms,
        )

    async def stream_complete(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a completion.

        Yields text chunks as they're generated.
        """
        client = await self._get_client()

        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "stream": True,
        }

        async with client.stream("POST", "/v1/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    import json
                    chunk = json.loads(data)
                    if chunk["choices"]:
                        yield chunk["choices"][0].get("text", "")

    async def health_check(self) -> bool:
        """Check if the inference server is healthy."""
        try:
            client = await self._get_client()
            response = await client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """List available models."""
        try:
            client = await self._get_client()
            response = await client.get("/v1/models")
            response.raise_for_status()
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception:
            return []


# Global client instance
_client: Optional[InferenceClient] = None


def get_client(config: Optional[InferenceConfig] = None) -> InferenceClient:
    """Get or create the global inference client."""
    global _client
    if _client is None:
        _client = InferenceClient(config)
    return _client


async def complete(prompt: str, **kwargs) -> CompletionResult:
    """Convenience function for quick completions."""
    client = get_client()
    return await client.complete(prompt, **kwargs)
