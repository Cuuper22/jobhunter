"""Generate warm outreach/networking emails using Gemini 3.1 Pro."""

import json
import logging
import re
import time
from google import genai
from google.genai import types

from shared.config import config

logger = logging.getLogger(__name__)

# Initialize Gemini client
client = genai.Client(api_key=config.gemini_api_key)
MODEL = "gemini-3.1-pro-preview"

SYSTEM_PROMPT = """You are an expert networking coach who writes warm, genuine outreach emails.

Your emails are sent by Yousef Anas — an ML/AI builder who has:
- Taught 250+ students across 20+ colleges
- Shipped the Findhope mental health chatbot (real AI product in production)
- 30+ GitHub projects spanning AI agents, web dev, automation, and SaaS
- Coursework in AI and Physics at Minerva University (76 credits)
- Multilingual: Arabic, English, French, Spanish

You write emails that get replies. Follow these rules:

**STRUCTURE:**
1. Subject line: Short, specific, human. Never generic like "Networking Request." Reference the role or a shared interest.
2. Opening (1-2 sentences): Mention something specific about the person, their work, or the company. Show you did your homework.
3. Bridge (2-3 sentences): Connect Yousef's experience to the role or company. Be specific — mention a project, metric, or skill that maps to what they do.
4. Ask (1-2 sentences): Make a clear, low-friction request — a 15-minute coffee chat, a referral, or advice on the team. Never ask for a job directly.
5. Close (1 sentence): Thank them, keep it warm and brief.

**RULES:**
- The email body MUST be 150-200 words. This is non-negotiable.
- Be specific, not generic. Reference the actual role, company, or person's work.
- Tone: professional but human. No corporate buzzwords, no sycophancy.
- If a contact name is provided, address them by first name. Otherwise use "Hi there" or similar.
- Never fabricate experiences — only reference what's in the candidate context.
- Never say "I am writing to..." or "I hope this email finds you well."
- Sign off with "Best,\nYousef"

**OUTPUT FORMAT:**
Return ONLY valid JSON with exactly two keys:
- "subject": the email subject line (string)
- "body": the full email body including greeting and sign-off (string)

Output ONLY valid JSON, no markdown fencing. Use double quotes for keys and string values.
Use \\n for newlines within the body string.
"""

_DEFAULT_RESULT = {
    "subject": "Interested in connecting — Yousef Anas",
    "body": "Hi,\n\nI came across your team and would love to connect about opportunities. I have experience in ML/AI and have shipped several projects including an AI chatbot and various automation tools.\n\nWould you be open to a brief chat?\n\nBest,\nYousef",
}


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


def _parse_email_response(text: str) -> dict:
    """Parse Gemini's JSON response into a dict with subject and body."""
    text = text.strip()

    # Strip markdown JSON fencing
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    # Try standard JSON parse
    try:
        result = json.loads(text)
        subject = str(result.get("subject", "")).strip()
        body = str(result.get("body", "")).strip()
        if subject and body:
            return {"subject": subject, "body": body}
    except (json.JSONDecodeError, KeyError):
        pass

    # Fallback: extract subject and body with regex
    subject_match = re.search(r'"subject"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
    body_match = re.search(r'"body"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)

    if subject_match and body_match:
        subject = subject_match.group(1).encode().decode("unicode_escape")
        body = body_match.group(1).encode().decode("unicode_escape")
        return {"subject": subject.strip(), "body": body.strip()}

    raise ValueError(f"Could not extract email from response: {text[:200]}")


def generate_outreach_email(
    job_title: str,
    company: str,
    job_description: str,
    user_context: str,
    contact_name: str | None = None,
) -> dict:
    """Generate a warm outreach/networking email for a specific role.

    Args:
        job_title: The target role title.
        company: The company name.
        job_description: Full or partial job description text.
        user_context: Candidate background and resume context.
        contact_name: Optional name of the person to address.

    Returns:
        Dict with "subject" and "body" keys.
    """
    contact_line = f"**Contact:** {contact_name}" if contact_name else "**Contact:** Unknown (use a generic but warm greeting)"

    prompt = f"""Write a warm outreach email for networking about this role. The email body MUST be 150-200 words.

## Target Role
**Title:** {job_title}
**Company:** {company}
{contact_line}
**Description:**
{job_description[:3000]}

## Candidate Background
{user_context[:5000]}

Write the outreach email now as JSON with "subject" and "body" keys.
"""

    try:
        raw = _call_gemini_with_retry(prompt, SYSTEM_PROMPT)
        return _parse_email_response(raw)
    except ValueError as e:
        logger.warning(f"Failed to parse outreach email response: {e}")
        return {**_DEFAULT_RESULT}
    except Exception as e:
        logger.error(f"Outreach email generation failed: {e}")
        return {**_DEFAULT_RESULT}
