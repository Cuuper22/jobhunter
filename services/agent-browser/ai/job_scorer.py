"""Score job fit using Gemini 3.1 Pro — returns structured analysis."""

import json
import logging
import re
import time
from google import genai
from google.genai import types

from shared.config import config

logger = logging.getLogger(__name__)

client = genai.Client(api_key=config.gemini_api_key)
MODEL = "gemini-3.1-pro-preview"

SYSTEM_PROMPT = """You are a job fit scoring engine. Given a candidate profile and a job posting,
you output a JSON object with these fields:

- "score": integer 0-100 (how well the candidate fits this role)
- "reasoning": string (2-3 sentences explaining the score)
- "role_summary": string (1-2 sentences: what the role is about and what the company does)
- "company_summary": string (1-2 sentences: company overview, culture, size if known)
- "strengths": list of strings (3-5 bullet points: why the candidate IS a good fit)
- "gaps": list of strings (1-4 bullet points: where the candidate falls short)
- "suggestions": list of strings (1-3 bullet points: how the candidate could strengthen their application)

Scoring rubric:
- 80-100: Strong fit. Candidate meets most requirements, skills align well.
- 60-79: Good fit. Candidate meets core requirements, some gaps are minor.
- 40-59: Moderate fit. Significant gaps but transferable skills exist.
- 20-39: Weak fit. Major requirements unmet.
- 0-19: Poor fit. Wrong field or level entirely.

Key factors for THIS candidate (Yousef):
- Has ML/AI teaching experience (250+ students) — strong for education/advocacy roles
- Shipped an AI product (Findhope chatbot) — counts as real ML engineering
- 30+ GitHub projects spanning AI agents, web dev, automation, bots, SaaS — active builder
- No completed degree (76 credits) — penalize roles requiring BS/MS but not fatally
- EAD work authorization — flag roles explicitly requiring sponsorship or citizenship
- Multilingual (Arabic, English, French, Spanish) — bonus for global/diverse companies
- Located in OC, wants Bay Area — penalize roles requiring other locations

Output ONLY valid JSON, no markdown fencing. Use double quotes for keys and string values.
"""

# Default result when scoring fails
_DEFAULT_RESULT = {
    "score": 50,
    "reasoning": "Scoring unavailable — defaulting to 50",
    "role_summary": None,
    "company_summary": None,
    "strengths": [],
    "gaps": [],
    "suggestions": [],
}


def _parse_score_response(text: str) -> dict:
    """Parse Gemini's structured score response into a dict."""
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
        # Ensure required fields exist with correct types
        return {
            "score": min(100, max(0, int(result.get("score", 50)))),
            "reasoning": str(result.get("reasoning", "")),
            "role_summary": result.get("role_summary"),
            "company_summary": result.get("company_summary"),
            "strengths": result.get("strengths", []),
            "gaps": result.get("gaps", []),
            "suggestions": result.get("suggestions", []),
        }
    except (json.JSONDecodeError, KeyError):
        pass

    # Fallback: extract at least score and reasoning with regex
    score_match = re.search(r'"?score"?\s*[=:]\s*(\d+)', text)
    reasoning_match = re.search(r'"?reasoning"?\s*[=:]\s*"([^"]+)"', text)

    if score_match:
        score = min(100, max(0, int(score_match.group(1))))
        reasoning = reasoning_match.group(1) if reasoning_match else "Score extracted from non-standard format"
        return {**_DEFAULT_RESULT, "score": score, "reasoning": reasoning}

    raise ValueError(f"Could not extract score from: {text[:200]}")


def score_job(job_title: str, company: str, job_description: str, user_context: str) -> dict:
    """Score how well a job matches the candidate profile.

    Returns:
        Dict with keys: score, reasoning, role_summary, company_summary,
        strengths, gaps, suggestions.
    """
    prompt = f"""Score this job for the candidate.

## Job
**Title:** {job_title}
**Company:** {company}
**Description:**
{job_description[:3000]}

## Candidate
{user_context[:3000]}
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    max_output_tokens=1024,
                ),
            )
            return _parse_score_response(response.text)
        except ValueError as e:
            logger.warning(f"Failed to parse score response: {e}")
            return {**_DEFAULT_RESULT, "reasoning": "Score parsing failed — defaulting to 50"}
        except Exception as e:
            err_str = str(e)
            is_transient = any(k in err_str for k in ("503", "UNAVAILABLE", "SSL", "EOF", "timeout", "429"))
            if is_transient and attempt < max_retries - 1:
                wait = (2 ** attempt) * 5
                logger.warning(f"Gemini scoring transient error (attempt {attempt+1}), retrying in {wait}s: {e}")
                time.sleep(wait)
            else:
                logger.error(f"Job scoring failed: {e}")
                return {**_DEFAULT_RESULT, "reasoning": f"Scoring error: {e}"}

    return {**_DEFAULT_RESULT, "reasoning": "Scoring failed after retries"}
