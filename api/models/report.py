"""Report data models for coach analysis reports."""

from pydantic import BaseModel
from typing import Literal


class Strength(BaseModel):
    """A strength/positive point from the analysis."""
    text: str
    frame_refs: list[str]  # ["Frame 1", "Frame 2"]


class Issue(BaseModel):
    """An issue found in the analysis."""
    text: str
    frame_refs: list[str]
    severity: Literal["high", "medium", "low"] = "medium"


class ImprovementSuggestion(BaseModel):
    """A numbered improvement suggestion."""
    text: str
    number: int


class IssueSummaryRow(BaseModel):
    """A row in the issue summary table from frames.json data."""
    frame_number: int
    issue_type: str
    body_part: str
    description: str
    priority: Literal["high", "medium", "low"]


class RadarScores(BaseModel):
    """6-dimension radar scores (1-10 each)."""
    hitting_technique: int = 5
    footwork: int = 5
    body_rotation: int = 5
    timing: int = 5
    fitness: int = 5
    tactics: int = 5


class CoachReport(BaseModel):
    """Complete structured coach analysis report."""
    video_id: str
    overall_score: int  # 1-10
    radar_scores: RadarScores
    strengths: list[Strength]
    issues: list[Issue]
    improvement_suggestions: list[ImprovementSuggestion]
    issue_summary: list[IssueSummaryRow]
    coach_summary: str
    training_plan: str  # 专项训练计划
