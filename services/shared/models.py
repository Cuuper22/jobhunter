"""Shared Pydantic models for Firestore documents and API payloads."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobSource(str, Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    GOOGLE = "google"
    ZIP_RECRUITER = "zip_recruiter"
    COMPANY_SITE = "company_site"


class ApplicationStatus(str, Enum):
    SCRAPED = "scraped"
    SCORED = "scored"
    DRAFT_READY = "draft_ready"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUBMITTING = "submitting"
    SUBMITTED = "submitted"
    REJECTED_BY_USER = "rejected_by_user"
    FAILED = "failed"


class LogLevel(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Job(BaseModel):
    """A scraped job listing."""
    id: Optional[str] = None
    title: str
    company: str
    location: str
    description: str
    url: str
    source: JobSource
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    date_posted: Optional[datetime] = None
    date_scraped: datetime = Field(default_factory=datetime.utcnow)
    is_remote: bool = False
    fit_score: Optional[int] = None  # 0-100
    fit_reasoning: Optional[str] = None


class Application(BaseModel):
    """A job application in progress."""
    id: Optional[str] = None
    job_id: str
    job_title: str
    company: str
    job_url: str
    status: ApplicationStatus = ApplicationStatus.SCRAPED
    cover_letter: Optional[str] = None
    cover_letter_edited: Optional[str] = None
    form_data: Optional[dict] = None  # pre-filled form field values
    screenshot_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    # Scoring fields (populated from job_scorer)
    fit_score: Optional[int] = None  # 0-100
    fit_reasoning: Optional[str] = None
    role_summary: Optional[str] = None
    company_summary: Optional[str] = None
    strengths: Optional[list[str]] = None
    gaps: Optional[list[str]] = None
    suggestions: Optional[list[str]] = None
    # Outreach fields (populated from outreach_email generator)
    outreach_subject: Optional[str] = None
    outreach_email: Optional[str] = None


class LogEntry(BaseModel):
    """Agent activity log."""
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: LogLevel = LogLevel.INFO
    message: str
    job_id: Optional[str] = None
    application_id: Optional[str] = None
    screenshot_url: Optional[str] = None
    metadata: Optional[dict] = None


class SearchCriteria(BaseModel):
    """User-defined job search parameters."""
    roles: list[str]
    locations: list[str]
    experience_level: str = "entry_level"
    excluded_companies: list[str] = []
    min_salary: Optional[float] = None
    is_remote_ok: bool = True
    hours_old: int = 72  # only jobs posted within this many hours
