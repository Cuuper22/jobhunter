"""Search configuration for JobSpy scraper."""

from dataclasses import dataclass, field


@dataclass
class SearchConfig:
    """Maps to JobSpy's scrape_jobs() parameters."""
    site_names: list[str] = field(default_factory=lambda: [
        "indeed", "linkedin"
    ])
    search_term: str = "Junior ML Engineer"
    location: str = "San Francisco Bay Area"
    distance: int = 50  # miles
    results_wanted: int = 30
    hours_old: int = 72  # only jobs from last 72 hours
    is_remote: bool = False
    country_indeed: str = "USA"

    # Anti-detection
    linkedin_fetch_description: bool = False  # don't fetch full desc from LinkedIn (risky)
    proxy: str | None = None  # e.g., "http://user:pass@host:port"


# Default searches — focused on warmest channels for Yousef's profile.
#
# Strategy: Target roles where Yousef's strengths (ML/AI teaching 250+ students,
# shipped Findhope chatbot, multilingual, product-builder portfolio) give highest odds.
# Only Indeed + LinkedIn to avoid rate limiting. 10 high-value searches.
DEFAULT_SEARCHES: list[SearchConfig] = [
    # --- Tier 1: Strongest competitive advantage ---
    SearchConfig(
        search_term="AI instructor",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Developer Advocate AI",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Developer Advocate machine learning",
        location="",
        is_remote=True,
    ),

    # --- Tier 2: Core ML/AI engineering ---
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
        location="",
        is_remote=True,
    ),

    # --- Tier 3: Data + NLP roles ---
    SearchConfig(
        search_term="Data Scientist junior",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="NLP Engineer",
        location="San Francisco Bay Area",
    ),

    # --- Tier 4: Accessible entry points ---
    SearchConfig(
        search_term="Technical Support Engineer AI",
        location="San Francisco Bay Area",
    ),
    SearchConfig(
        search_term="Python Automation Engineer",
        location="San Francisco Bay Area",
    ),
]
