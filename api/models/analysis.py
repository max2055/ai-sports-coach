"""Analysis status models for tracking async video analysis."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

AnalysisStatus = Literal["pending", "extracting", "analyzing", "annotating", "completed", "failed"]


class AnalysisState(BaseModel):
    """Full analysis state stored in status.json."""

    video_id: str
    status: AnalysisStatus
    progress: int  # 0-100
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_path: Optional[str] = None
    analysis_type: Optional[str] = None
    frames_dir: Optional[str] = None
    annotated_dir: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis API endpoints."""

    video_id: str
    status: AnalysisStatus
    progress: int
    message: str