import json
import re
from typing import Any


async def enhance_ai_output(raw_text: str) -> dict[str, Any]:
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