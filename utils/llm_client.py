"""Async Hugging Face Inference API client for DevMind agents."""

from __future__ import annotations

import asyncio

from huggingface_hub import InferenceClient

from config import HF_TOKEN, LLM_MAX_TOKENS, LLM_TEMPERATURE, MODEL_NAME


class LLMError(RuntimeError):
    """Raised when the Hugging Face LLM request fails or returns invalid data."""


class LLMClient:
    """Small async wrapper around huggingface_hub chat completions."""

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return the first assistant message content from the HF chat completion API."""

        if not HF_TOKEN:
            raise LLMError("HF_TOKEN is not set")

        try:
            completion = await asyncio.to_thread(
                self._complete_sync,
                system_prompt,
                user_prompt,
            )
        except Exception as exc:
            raise LLMError(f"Hugging Face request failed: {exc}") from exc

        try:
            content = completion.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMError("Hugging Face response did not include assistant content") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMError("Hugging Face response content was empty")
        return content

    def _complete_sync(self, system_prompt: str, user_prompt: str):
        client = InferenceClient(api_key=HF_TOKEN)
        return client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
        )
