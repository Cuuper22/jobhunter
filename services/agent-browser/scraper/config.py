"""Search configuration for JobSpy scraper."""

from dataclasses import dataclass, field


@dataclass
class SearchConfig:
    """Maps to JobSpy's scrape_jobs() parameters."""
    site_names: list[str] = field(default_factory=lambda: [
        "indeed", "linkedin", "glassdoor", "google", "zip_recruiter"
    ])
    search_term: str = "Junior ML Engineer"
    location: str = "San Francisco Bay Area"
    distance: int = 50  # miles
    results_wanted: int = 50
    hours_old: int = 72  # only jobs from last 72 hours
    is_remote: bool = False
    country_indeed: str = "USA"

    # Anti-detection
    linkedin_fetch_description: bool = False  # don't fetch full desc from LinkedIn (risky)
    proxy: str | None = None  # e.g., "http://user:pass@host:port"


# Default searches — optimized for warmest channels and best competitive advantage.
#
# Strategy: Yousef's strengths are ML/AI teaching (250+ students), shipped AI product
# (Findhope), multilingual, product-building GitHub portfolio, and automation expertise.
# These searches target roles where those strengths give the highest interview odds.
DEFAULT_SEARCHES: list[SearchConfig] = [
    # --- Tier 1: Strongest fit (teaching + AI hands-on) ---
    SearchConfig(
        search_term="AI instructor",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Machine Learning instructor",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Developer Advocate AI",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Developer Advocate AI",
        location="",
        is_remote=True,
    ),
    SearchConfig(
        search_term="Technical Evangelist machine learning",
        location="San Francisco Bay Area",
    ),

    # --- Tier 2: Strong fit (AI/ML engineering, entry-level) ---
    SearchConfig(
        search_term="Junior ML Engineer",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="AI Engineer entry level",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Machine Learning Engineer junior",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Junior ML Engineer",
        location="",
        is_remote=True,
    ),

    # --- Tier 3: Good fit (data roles, NLP, chatbots) ---
    SearchConfig(
        search_term="Data Scientist junior",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="NLP Engineer entry level",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="chatbot developer",
        location="San Francisco Bay Area",
    ),

    # --- Tier 4: Accessible entry points at AI companies ---
    SearchConfig(
        search_term="Technical Support Engineer AI",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Solutions Engineer AI startup",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="AI startup associate",
        location="San Francisco Bay Area",
    ),

    # --- Tier 5: Automation/scraping (GitHub portfolio match) ---
    SearchConfig(
        search_term="Automation Engineer Python",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="web scraping engineer",
        location="San Francisco Bay Area",
    ),
]
