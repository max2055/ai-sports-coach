"""Chart data models for ECharts visualization."""

from typing import Literal

from pydantic import BaseModel


class ServeHeightPoint(BaseModel):
    """Single data point for serve height chart."""

    frame_number: int
    time_seconds: float
    height_pct: float  # body.y_pct (lower = higher height)


class ServeHeightData(BaseModel):
    """Serve height data for line chart."""

    points: list[ServeHeightPoint]


class HitPoint(BaseModel):
    """Single hit point for heatmap/scatter plot."""

    frame_number: int
    x_pct: float
    y_pct: float
    issue_type: str | None = None


class HitPointHeatmap(BaseModel):
    """Hit point positions for scatter/heatmap visualization."""

    points: list[HitPoint]


class RadarDimension(BaseModel):
    """Single dimension for radar chart."""

    name: str
    value: float  # 0-10 score


class ConsistencyRadar(BaseModel):
    """6-dimension consistency radar chart data."""

    dimensions: list[RadarDimension]
    overall_score: float


class IssueStat(BaseModel):
    """Statistics for a single issue type."""

    issue_type: str
    count: int
    severity: Literal["high", "medium", "low"]


class IssueStatistics(BaseModel):
    """Issue statistics for bar chart."""

    stats: list[IssueStat]
    total_issues: int
    total_frames: int