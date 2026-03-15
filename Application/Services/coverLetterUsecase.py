from Infrastructure.Ai.Prompts.CoverLetterPrompt import COVER_LETTER_PROMPT
from Infrastructure.Ai.Gemini_Client import GeminiClient


client = GeminiClient()

async def generate_cover_letter(cv_data: str, job_description: str):
    

    response = await client.generate_text(
        prompt=COVER_LETTER_PROMPT.format(
            cv_data=cv_data,
            job_description=job_description
        ),
        model="gemini-2.5-flash"
    )    # Convert escaped newlines to actual line breaks for readability
    return  response.text

