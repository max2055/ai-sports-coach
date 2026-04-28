"""Pro video models for comparison feature."""

from pydantic import BaseModel
from typing import Literal

ProVideoType = Literal["forehand", "backhand", "serve", "volley"]


class ProVideo(BaseModel):
    """Single pro video metadata."""
    id: str
    type: ProVideoType
    name: str
    description: str
    file: str
    duration: float | None = None


class ProVideoList(BaseModel):
    """List of pro videos."""
    videos: list[ProVideo]