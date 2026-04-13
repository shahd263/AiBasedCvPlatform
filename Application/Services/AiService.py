"""
Service layer for CV generation and output normalization.
Uses Google GenAI to produce ATS-optimized CV JSON from candidate data.
"""

import json

import re
from typing import Any
from Infrastructure.Ai.Gemini_Client import GeminiClient
from Infrastructure.Ai.Prompts.CoverLetterPrompt import COVER_LETTER_PROMPT
from Infrastructure.Ai.Prompts.CvParserPrompt import CV_PARSER_PROMPT
from Infrastructure.Ai.Prompts.GenerateResumePrompt import CV_GENERATOR_PROMPT
from Utils.enhance_ai_output import enhance_ai_output
from playwright.sync_api import sync_playwright


class AiService:
    """Handles AI generation via GenAI and JSON output normalization."""

    
    def __init__(self, client: GeminiClient):
        self._client = client

    async def _extract_response_text(self, response: Any) -> str:
        raw = getattr(response, "text", None) or ""
        if raw:
            return raw
        if hasattr(response, "candidates") and response.candidates:
            parts = getattr(response.candidates[0].content, "parts", None) or []
            if parts and hasattr(parts[0], "text"):
                return parts[0].text
        return ""



    async def generate_cv(self, candidate_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate ATS-optimized CV JSON from candidate data using GenAI.
        """
        data_str = json.dumps(candidate_data, ensure_ascii=False, indent=2)
        prompt = CV_GENERATOR_PROMPT.replace("{data}", data_str)

        response = await self._client.generate_text(prompt)

        raw_text = await self._extract_response_text(response)
        return await enhance_ai_output(raw_text)


    async def generate_cover_letter(self, cv_data: str, job_description: str) -> dict[str, Any]:
        response = await self._client.generate_text(
            prompt=COVER_LETTER_PROMPT.format(
                cv_data=cv_data,
                job_description=job_description
            ),
        )   
        raw_text = await self._extract_response_text(response)
        return await enhance_ai_output(raw_text)


    async def parse_cv(self, cv_text: str) -> dict[str, Any]:
        prompt = CV_PARSER_PROMPT.replace("{cv_text}", cv_text)
        response = await self._client.generate_text(
            prompt=prompt,
        )
        raw_text = await self._extract_response_text(response)
        return await enhance_ai_output(raw_text)





  
