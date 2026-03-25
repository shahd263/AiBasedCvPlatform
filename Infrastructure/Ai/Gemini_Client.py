import asyncio
from typing import Any

from google.genai import Client, types

from Core.config import settings


class GeminiClient:
    def __init__(self) -> None:
        self.client = Client(api_key=settings.GEMINI_API_KEY)

    async def generate_text(self, prompt: str, model: str = "gemini-2.5-flash-lite") -> Any:
        """
        Generate text using Google Gemini. Uses async client (.aio) when available,
        otherwise runs sync generate_content in a thread.
        """
        if hasattr(self.client, "aio"):
            async with self.client.aio as aclient:
                return await aclient.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.4,
                        max_output_tokens=8192,
                    ),
                )
        # Sync client: run in thread so we don't block the event loop
        return await asyncio.to_thread(
            self.client.models.generate_content,
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=8192,
            ),
        )