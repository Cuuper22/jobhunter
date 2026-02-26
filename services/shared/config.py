"""Shared configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # GCP
    project_id: str = os.getenv("PROJECT_ID", "")
    region: str = os.getenv("REGION", "us-central1")

    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # Agent
    scrape_interval_hours: int = int(os.getenv("SCRAPE_INTERVAL_HOURS", "2"))
    max_steps_per_job: int = int(os.getenv("MAX_STEPS_PER_JOB", "50"))
    browser_timeout_ms: int = int(os.getenv("BROWSER_TIMEOUT_MS", "30000"))
    max_daily_gemini_cost: float = float(os.getenv("MAX_DAILY_GEMINI_COST_USD", "2.00"))

    # Search
    target_roles: list[str] = field(default_factory=lambda: [
        r.strip() for r in os.getenv(
            "TARGET_ROLES",
            "Junior ML Engineer,AI Engineer,Data Scientist"
        ).split(",")
    ])
    target_locations: list[str] = field(default_factory=lambda: [
        loc.strip() for loc in os.getenv(
            "TARGET_LOCATIONS",
            "San Francisco Bay Area,Remote"
        ).split(",")
    ])
    experience_level: str = os.getenv("EXPERIENCE_LEVEL", "entry_level")
    excluded_companies: list[str] = field(default_factory=lambda: [
        c.strip() for c in os.getenv("EXCLUDED_COMPANIES", "").split(",") if c.strip()
    ])


config = Config()
