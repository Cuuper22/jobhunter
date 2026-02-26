"""Playwright-based form pre-filling for job application sites.

Supports major ATS platforms: Greenhouse, Workday, Lever.
Each ATS has different form structures, so we use adapter functions.
"""

import logging
from typing import Optional

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from agent_browser.applicator.screenshot import capture_screenshot

logger = logging.getLogger(__name__)


async def detect_ats(page: Page) -> str:
    """Detect which ATS platform a career page uses."""
    url = page.url.lower()
    content = await page.content()
    content_lower = content.lower()

    if "greenhouse.io" in url or "boards.greenhouse.io" in content_lower:
        return "greenhouse"
    elif "myworkdayjobs.com" in url or "workday" in content_lower:
        return "workday"
    elif "lever.co" in url or "jobs.lever.co" in content_lower:
        return "lever"
    elif "icims.com" in url:
        return "icims"
    elif "bamboohr.com" in url:
        return "bamboohr"
    else:
        return "unknown"


async def fill_greenhouse_form(page: Page, form_data: dict) -> bool:
    """Fill a Greenhouse job application form.

    Greenhouse forms typically have:
    - First name, Last name, Email, Phone
    - Resume upload
    - Cover letter text area
    - Optional custom questions
    """
    try:
        # Basic fields
        for field_id, value in [
            ("#first_name", form_data.get("first_name", "")),
            ("#last_name", form_data.get("last_name", "")),
            ("#email", form_data.get("email", "")),
            ("#phone", form_data.get("phone", "")),
        ]:
            el = await page.query_selector(field_id)
            if el:
                await el.fill(value)

        # Cover letter
        cover_letter = form_data.get("cover_letter", "")
        if cover_letter:
            # Greenhouse uses a textarea or rich text editor
            cl_field = await page.query_selector("textarea[name*='cover_letter']")
            if not cl_field:
                cl_field = await page.query_selector("#cover_letter")
            if cl_field:
                await cl_field.fill(cover_letter)

        # Resume upload
        resume_path = form_data.get("resume_path")
        if resume_path:
            upload = await page.query_selector("input[type='file']")
            if upload:
                await upload.set_input_files(resume_path)

        logger.info("Greenhouse form filled successfully")
        return True
    except PlaywrightTimeout:
        logger.error("Greenhouse form fill timed out")
        return False
    except Exception as e:
        logger.error(f"Greenhouse form fill error: {e}")
        return False


async def fill_lever_form(page: Page, form_data: dict) -> bool:
    """Fill a Lever job application form."""
    try:
        for selector, value in [
            ("input[name='name']", f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}"),
            ("input[name='email']", form_data.get("email", "")),
            ("input[name='phone']", form_data.get("phone", "")),
            ("input[name='org']", form_data.get("current_company", "")),
        ]:
            el = await page.query_selector(selector)
            if el:
                await el.fill(value)

        # Cover letter in Lever is often a textarea
        cover_letter = form_data.get("cover_letter", "")
        cl_field = await page.query_selector("textarea[name='comments']")
        if cl_field and cover_letter:
            await cl_field.fill(cover_letter)

        # Resume upload
        resume_path = form_data.get("resume_path")
        if resume_path:
            upload = await page.query_selector("input[type='file']")
            if upload:
                await upload.set_input_files(resume_path)

        logger.info("Lever form filled successfully")
        return True
    except Exception as e:
        logger.error(f"Lever form fill error: {e}")
        return False


async def fill_workday_form(page: Page, form_data: dict) -> bool:
    """Fill a Workday job application form.

    Workday forms are notoriously complex with multi-step wizards.
    This handles the basic first page — subsequent pages need manual review.
    """
    try:
        # Workday uses data-automation-id attributes
        for auto_id, value in [
            ("legalNameSection_firstName", form_data.get("first_name", "")),
            ("legalNameSection_lastName", form_data.get("last_name", "")),
            ("email", form_data.get("email", "")),
            ("phone-number", form_data.get("phone", "")),
        ]:
            el = await page.query_selector(f"input[data-automation-id='{auto_id}']")
            if el:
                await el.fill(value)

        logger.info("Workday form (page 1) filled")
        return True
    except Exception as e:
        logger.error(f"Workday form fill error: {e}")
        return False


# ATS adapter registry
ATS_FILLERS = {
    "greenhouse": fill_greenhouse_form,
    "lever": fill_lever_form,
    "workday": fill_workday_form,
}


async def prefill_application(
    page: Page,
    job_url: str,
    form_data: dict,
    job_id: str,
) -> tuple[bool, str, Optional[str]]:
    """Navigate to a job URL, detect ATS, and pre-fill the application form.

    Args:
        page: Playwright page
        job_url: URL of the job application page
        form_data: Dict of field values to fill
        job_id: For screenshot naming

    Returns:
        Tuple of (success: bool, ats_type: str, screenshot_url: str|None)
    """
    try:
        await page.goto(job_url, wait_until="networkidle", timeout=30000)
    except PlaywrightTimeout:
        logger.warning(f"Page load timed out for {job_url}, proceeding anyway")

    ats_type = await detect_ats(page)
    logger.info(f"Detected ATS: {ats_type}")

    filler = ATS_FILLERS.get(ats_type)
    if not filler:
        # Unknown ATS — just take a screenshot for manual review
        screenshot_url = await capture_screenshot(page, job_id, "unknown_ats")
        return False, ats_type, screenshot_url

    success = await filler(page, form_data)

    # Try to answer any visible screening questions
    await _answer_screening_questions(page, form_data)

    # Always capture screenshot before submit (the approval step)
    screenshot_url = await capture_screenshot(page, job_id, "pre_submit")

    return success, ats_type, screenshot_url


async def _answer_screening_questions(page: Page, form_data: dict) -> None:
    """Detect and answer screening questions using AI."""
    try:
        # Find question-like labels near unfilled fields
        questions = await page.evaluate("""() => {
            const labels = document.querySelectorAll('label, .field-label, [data-automation-id*="label"]');
            const qs = [];
            for (const label of labels) {
                const text = label.textContent?.trim();
                if (text && text.length > 10 && text.length < 500 && text.includes('?')) {
                    qs.push(text);
                }
            }
            return qs.slice(0, 10);  // max 10 questions
        }""")

        if not questions:
            return

        logger.info(f"Found {len(questions)} screening questions")

        from agent_browser.ai.form_qa import answer_screening_questions
        from agent_browser.context.loader import get_user_context

        job_title = form_data.get("job_title", "")
        company = form_data.get("company", "")
        user_context = get_user_context()

        answers = answer_screening_questions(questions, job_title, company, user_context)
        logger.info(f"AI answered {len(answers)} screening questions")

        # Try to fill answers into matching textareas/inputs near the questions
        for question, answer in answers.items():
            await page.evaluate("""([q, a]) => {
                const labels = document.querySelectorAll('label, .field-label');
                for (const label of labels) {
                    if (label.textContent?.trim().includes(q.substring(0, 30))) {
                        const forId = label.getAttribute('for');
                        let field = forId ? document.getElementById(forId) : null;
                        if (!field) {
                            field = label.parentElement?.querySelector('textarea, input[type="text"]');
                        }
                        if (field && !field.value) {
                            field.value = a;
                            field.dispatchEvent(new Event('input', { bubbles: true }));
                            field.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                        break;
                    }
                }
            }""", [question, answer])

    except Exception as e:
        logger.warning(f"Screening question answering failed (non-fatal): {e}")
