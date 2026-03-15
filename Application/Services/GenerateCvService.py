"""
Service layer for CV generation and output normalization.
Uses Google GenAI to produce ATS-optimized CV JSON from candidate data.
"""

import json

import re
from typing import Any
from Infrastructure.Ai.Gemini_Client import GeminiClient
from Infrastructure.Ai.Prompts.GenerateResumePrompt import CV_GENERATOR_PROMPT


class GenerateCvService:
    """Handles CV generation via GenAI and JSON output normalization."""

    @staticmethod
    async def enhance_cv_output(raw_text: str) -> dict[str, Any]:
        """
        Normalize and parse model output into valid JSON.
        Strips markdown code fences and fixes common JSON issues.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Model returned empty output.")

        text = raw_text.strip()

        json_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_block:
            text = json_block.group(1).strip()
        else:
            text = text.strip()

        text = re.sub(r",\s*([}\]])", r"\1", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            obj_match = re.search(r"\{[\s\S]*\}", text)
            if obj_match:
                try:
                    return json.loads(obj_match.group(0))
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Could not parse model output as JSON: {e}") from e

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
        client = GeminiClient()
        data_str = json.dumps(candidate_data, ensure_ascii=False, indent=2)
        prompt = CV_GENERATOR_PROMPT.format(data=data_str)

        response = await client.generate_text(prompt)

        raw_text = await self._extract_response_text(response)
        return await self.enhance_cv_output(raw_text)
