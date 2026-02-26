"""Answer screening questions on job application forms using Gemini."""

import json
import logging
from google import genai
from google.genai import types

from shared.config import config

logger = logging.getLogger(__name__)

client = genai.Client(api_key=config.gemini_api_key)
MODEL = "gemini-3.1-pro-preview"

SYSTEM_PROMPT = """You answer job application screening questions honestly on behalf of a candidate.

Rules:
- Be truthful — never fabricate credentials or experience
- For yes/no questions about degree: the candidate does NOT have a completed degree
- For years of experience: count relevant experience (teaching ML = ML experience)
- For visa/sponsorship: candidate has EAD (Employment Authorization Document), can work legally
- For salary expectations: give a reasonable range for the role level, not too low
- For "Why do you want to work here?": give an authentic 2-3 sentence answer

Output JSON: {"answers": [{"question": "...", "answer": "..."}]}
Only output valid JSON, no markdown fencing.
"""


def answer_screening_questions(
    questions: list[str],
    job_title: str,
    company: str,
    user_context: str,
) -> dict[str, str]:
    """Answer a list of screening questions from an application form.

    Args:
        questions: List of question strings from the form
        job_title: Role being applied to
        company: Company name
        user_context: Candidate background

    Returns:
        Dict mapping question -> answer
    """
    prompt = f"""Answer these screening questions for a {job_title} role at {company}.

## Questions
{json.dumps(questions, indent=2)}

## Candidate Background
{user_context[:3000]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
                max_output_tokens=1024,
            ),
        )
        result = json.loads(response.text)
        return {a["question"]: a["answer"] for a in result.get("answers", [])}
    except Exception as e:
        logger.error(f"Form Q&A failed: {e}")
        return {}
