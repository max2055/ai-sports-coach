"""History data models for analysis record management."""

from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class HistoryEntry(BaseModel):
    """A single history analysis record."""
    video_id: str
    filename: str
    analysis_type: str
    status: Literal["completed", "failed", "pending"]
    created_at: datetime
    completed_at: datetime | None = None
    overall_score: int | None = None
    duration: float | None = None


class HistoryList(BaseModel):
    """Paginated history list response."""
    entries: list[HistoryEntry]
    total: int
