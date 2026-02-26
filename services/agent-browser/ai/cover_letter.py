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

You write compelling, authentic cover letters that follow this EXACT structure:

**Paragraph 1 — Hook (3-4 sentences):**
Open with a specific, genuine reason you're excited about THIS company and role.
Reference something concrete: a product they built, a mission statement, recent news, or a value that resonates. Do NOT use generic openings like "I am writing to express my interest."

**Paragraph 2 — Fit & Experience (5-7 sentences):**
Connect your 2-3 most relevant experiences to the job requirements. Be specific:
mention numbers (250+ students taught, 20+ colleges served, 30+ GitHub projects).
Show HOW your experience maps to what they need, not just THAT it does.

**Paragraph 3 — Projects & Technical Depth (4-6 sentences):**
Highlight 1-2 relevant technical projects from your GitHub portfolio or past work.
Be specific about technologies used and outcomes achieved. If the role involves
AI/ML, emphasize the Findhope chatbot, AI agents, or LLM work. If it involves
web dev, mention the SaaS starter kit, business tools, or API projects.

**Paragraph 4 — Close & Call to Action (2-3 sentences):**
Express enthusiasm for contributing, mention willingness to discuss further,
and close professionally. Keep it warm but not sycophantic.

RULES:
- The letter MUST be 250-350 words. This is non-negotiable.
- Never fabricate experiences — only use what's in the candidate's context
- The candidate does NOT have a completed degree. He has 76 credits from Minerva University. Do NOT say "Bachelor's degree" — say "coursework in AI and Physics at Minerva University" or similar honest framing.
- Adapt tone to the company culture (startup = casual, corporate = formal)
- Include the greeting "Dear Hiring Manager," (unless a specific name is in the job description)
- End with "Sincerely," followed by "Yousef Anas"
"""


def _call_gemini_with_retry(prompt: str, system: str, temperature: float = 0.7,
                             max_tokens: int = 2048, max_retries: int = 3) -> str:
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


def _count_words(text: str) -> int:
    """Count words in text, ignoring greeting/closing lines."""
    return len(text.split())


def generate_cover_letter(
    job_title: str,
    company: str,
    job_description: str,
    user_context: str,
) -> str:
    """Generate a tailored cover letter for a specific job.

    Includes word count validation — retries once if too short.
    """
    prompt = f"""Write a cover letter for the following position. It MUST be 250-350 words
and have exactly 4 paragraphs as specified in your instructions.

## Job Details
**Title:** {job_title}
**Company:** {company}
**Description:**
{job_description[:3000]}

## Candidate Background
{user_context[:5000]}

Write the cover letter now. Follow the 4-paragraph structure exactly.
"""

    try:
        letter = _call_gemini_with_retry(prompt, SYSTEM_PROMPT)

        # Validate word count — retry once if too short
        word_count = _count_words(letter)
        if word_count < 150:
            logger.info(f"Cover letter too short ({word_count} words), retrying with explicit length instruction")
            retry_prompt = f"""The previous cover letter was only {word_count} words. That is too short.

Write a NEW cover letter that is EXACTLY 250-350 words with 4 full paragraphs.
Each paragraph should have 3-7 sentences. Do NOT be brief — elaborate on experiences
and show genuine knowledge of the company.

## Job Details
**Title:** {job_title}
**Company:** {company}
**Description:**
{job_description[:3000]}

## Candidate Background
{user_context[:5000]}

Write the FULL 4-paragraph cover letter now. It must be at least 250 words.
"""
            letter = _call_gemini_with_retry(retry_prompt, SYSTEM_PROMPT)

        return letter

    except Exception as e:
        logger.error(f"Cover letter generation failed after retries: {e}")
        raise
