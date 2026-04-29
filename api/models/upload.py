"""Upload request/response models."""

from pydantic import BaseModel
from typing import Literal

AnalysisType = Literal["forehand", "backhand", "serve", "volley", "full"]


class VideoMetadata(BaseModel):
    """Video metadata extracted from uploaded file."""

    duration: float  # seconds
    width: int
    height: int
    size: int  # bytes
    file_format: str


class UploadResponse(BaseModel):
    """Response model for video upload endpoint."""

    video_id: str
    filename: str
    analysis_type: AnalysisType
    metadata: VideoMetadata
    message: str
