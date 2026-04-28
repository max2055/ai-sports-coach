"""Frame annotation models for tennis video analysis."""

from typing import Literal, Optional

from pydantic import BaseModel

# Issue types from tennis_annotate.py
IssueType = Literal[
    "LATE BACKSWING",
    "WRONG GRIP",
    "GRIP CHANGE ERR",
    "WRONG CONTACT",
    "ELBOW DROP",
    "NO HIP ROT",
    "LATE SHOULDER",
    "NO FOLLOW-THRU",
    "POOR FOOTWORK",
    "NO SPLIT STEP",
    "LATE WEIGHT",
    "WRONG STANCE",
    "WRONG POSITION",
    "BAD TOSS",
    "NO LEG DRIVE",
    "OFF BALANCE",
    "TELEGRAPH",
    "WRONG SPIN",
    "GOOD FORM",
    "GOOD FOOTWORK",
    "GOOD TACTICS",
]


class BodyPartAnnotation(BaseModel):
    """Annotation for a single body part."""

    x_pct: float  # X coordinate as percentage of image width (0.0-1.0)
    y_pct: float  # Y coordinate as percentage of image height (0.0-1.0)
    radius_pct: float  # Radius as percentage of image width
    issue_type: Optional[IssueType] = None
    issue_note: Optional[str] = None


class PlayerAnnotation(BaseModel):
    """Annotation for a single player in a frame."""

    id: Optional[str] = None  # Player identifier (e.g., "P1")
    body: BodyPartAnnotation
    hand_l: BodyPartAnnotation  # Racket hand (dominant hand)
    hand_r: BodyPartAnnotation  # Off hand (non-dominant hand)
    foot_l: BodyPartAnnotation  # Front/lead foot
    foot_r: BodyPartAnnotation  # Back foot


class FrameAnnotation(BaseModel):
    """Complete annotation for a single frame."""

    frame_number: int
    players: list[PlayerAnnotation]
    frame_summary: Optional[str] = None  # Frame-level summary text


class IssueFrame(BaseModel):
    """Summary of a frame with issues for the issue list."""

    frame_number: int
    issue_types: list[IssueType]
    thumbnail_url: str  # URL to annotated frame image
    time_seconds: float  # Frame timestamp in seconds


class FrameData(BaseModel):
    """Root model for frames.json structure."""

    frames: dict[str, FrameAnnotation]