"""Generate tailored cover letters using Gemini 3.1 Pro."""

import logging
import time
from google import genai
from google.genai import types

from shared.config import config

logger = logging.getLogger(__name__)

# Initialize Gemini client
client = genai.Client(api_key=config.gemini_api_key)
MODEL = "gemini-3.1-pro-preview"

SYSTEM_PROMPT = """You are an expert career coach and cover letter writer.
You write concise, authentic, compelling cover letters that:
- Are 250-350 words max
- Open with a specific hook about the company/role (not generic)
- Highlight 2-3 most relevant experiences from the candidate's background
- Show enthusiasm without being sycophantic
- Close with a clear call to action
- Never fabricate experiences — only use what's in the candidate's context
- Adapt tone to the company culture (startup = casual, corporate = formal)

IMPORTANT: The candidate does NOT have a completed degree. He has 76 credits
from Minerva University. Do NOT say "Bachelor's degree" — say "coursework in
AI and Physics at Minerva University" or similar honest framing.
"""


def _call_gemini_with_retry(prompt: str, system: str, temperature: float = 0.7,
                             max_tokens: int = 1024, max_retries: int = 3) -> str:
    """Call Gemini with exponential backoff retry on transient errors."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            return response.text
        except Exception as e:
            err_str = str(e)
            is_transient = any(k in err_str for k in ("503", "UNAVAILABLE", "SSL", "EOF", "timeout", "429"))
            if is_transient and attempt < max_retries - 1:
                wait = (2 ** attempt) * 5  # 5s, 10s, 20s
                logger.warning(f"Gemini transient error (attempt {attempt+1}/{max_retries}), retrying in {wait}s: {e}")
                time.sleep(wait)
            else:
                raise


def generate_cover_letter(
    job_title: str,
    company: str,
    job_description: str,
    user_context: str,
) -> str:
    """Generate a tailored cover letter for a specific job."""
    prompt = f"""Write a cover letter for the following position.

## Job Details
**Title:** {job_title}
**Company:** {company}
**Description:**
{job_description[:3000]}

## Candidate Background
{user_context[:5000]}

Write the cover letter now. Address it to "Hiring Manager" unless a specific
name is mentioned in the job description.
"""

    try:
        return _call_gemini_with_retry(prompt, SYSTEM_PROMPT)
    except Exception as e:
        logger.error(f"Cover letter generation failed after retries: {e}")
        raise
