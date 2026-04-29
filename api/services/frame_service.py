"""Frame annotation service for retrieving tennis video frame data."""

import json
import logging
import re
from pathlib import Path
from typing import Optional

from models.frame import BodyPartAnnotation, FrameAnnotation, IssueFrame, IssueType, PlayerAnnotation

logger = logging.getLogger(__name__)

# Output directory for analysis results
ANALYSIS_DIR = Path("output/analysis")

# Validate video_id: alphanumeric, underscores, and hyphens only
_VIDEO_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')


def _get_analysis_dir(video_id: str) -> Path:
    """Get the analysis output directory for a video."""
    if not _VIDEO_ID_PATTERN.match(video_id):
        raise ValueError(f"Invalid video_id: {video_id}")
    return ANALYSIS_DIR / video_id


def _get_frames_json_path(video_id: str) -> Path:
    """Get the path to frames.json for a video."""
    return _get_analysis_dir(video_id) / "frames.json"


def _get_annotated_dir(video_id: str) -> Path:
    """Get the path to the annotated frames directory."""
    return _get_analysis_dir(video_id) / "annotated"


def get_frame_annotations(video_id: str) -> list[FrameAnnotation]:
    """Retrieve all frame annotations for a video.

    Args:
        video_id: Unique video identifier

    Returns:
        List of FrameAnnotation objects sorted by frame number

    Raises:
        FileNotFoundError: If frames.json doesn't exist
        ValueError: If frames.json is invalid
    """
    frames_path = _get_frames_json_path(video_id)

    if not frames_path.exists():
        raise FileNotFoundError(f"Frame annotations not found for video {video_id}")

    try:
        data = json.loads(frames_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in frames.json for video {video_id}: {e}")

    # Parse frames from the nested structure
    frames_data = data.get("frames", {})
    annotations: list[FrameAnnotation] = []

    for frame_key, frame_data in frames_data.items():
        try:
            frame_number = int(frame_key)
        except ValueError:
            logger.warning(f"Invalid frame key '{frame_key}' in video {video_id}, skipping")
            continue

        players_data = frame_data.get("players", [])
        players: list[PlayerAnnotation] = []

        for player_data in players_data:
            try:
                player = _parse_player_annotation(player_data)
                players.append(player)
            except (KeyError, TypeError) as e:
                logger.warning(
                    f"Invalid player data in frame {frame_number} of video {video_id}: {e}"
                )
                continue

        frame_annotation = FrameAnnotation(
            frame_number=frame_number,
            players=players,
            frame_summary=frame_data.get("frame_summary"),
        )
        annotations.append(frame_annotation)

    # Sort by frame number
    annotations.sort(key=lambda f: f.frame_number)
    return annotations


def _parse_player_annotation(data: dict) -> PlayerAnnotation:
    """Parse a player annotation from raw dict data."""
    return PlayerAnnotation(
        id=data.get("id"),
        body=_parse_body_part(data.get("body", {})),
        hand_l=_parse_body_part(data.get("hand_l", {})),
        hand_r=_parse_body_part(data.get("hand_r", {})),
        foot_l=_parse_body_part(data.get("foot_l", {})),
        foot_r=_parse_body_part(data.get("foot_r", {})),
    )


# Mapping from tennis_annotate.py snake_case keys to backend uppercase IssueType values
_ISSUE_TYPE_MAP = {
    "late_backswing": "LATE BACKSWING",
    "wrong_grip": "WRONG GRIP",
    "grip_change_error": "GRIP CHANGE ERR",
    "wrong_contact_point": "WRONG CONTACT",
    "elbow_drop": "ELBOW DROP",
    "no_hip_rotation": "NO HIP ROT",
    "shoulder_rot_late": "LATE SHOULDER",
    "poor_follow_through": "NO FOLLOW-THRU",
    "poor_footwork": "POOR FOOTWORK",
    "no_split_step": "NO SPLIT STEP",
    "late_weight_transfer": "LATE WEIGHT",
    "wrong_stance": "WRONG STANCE",
    "wrong_court_position": "WRONG POSITION",
    "poor_serve_toss": "BAD TOSS",
    "no_leg_drive": "NO LEG DRIVE",
    "off_balance": "OFF BALANCE",
    "telegraphing": "TELEGRAPH",
    "wrong_spin": "WRONG SPIN",
    "good_form": "GOOD FORM",
    "good_footwork": "GOOD FOOTWORK",
    "good_tactics": "GOOD TACTICS",
}


def _parse_body_part(data: dict) -> BodyPartAnnotation:
    """Parse a body part annotation from raw dict data."""
    raw_issue = data.get("issue_type", "")
    mapped_issue = _ISSUE_TYPE_MAP.get(raw_issue) if raw_issue else None
    return BodyPartAnnotation(
        x_pct=float(data.get("x_pct", 0.0)),
        y_pct=float(data.get("y_pct", 0.0)),
        radius_pct=float(data.get("radius_pct", 0.03)),
        issue_type=mapped_issue,
        issue_note=data.get("issue_note") if data.get("issue_note") else None,
    )


def get_issue_frames(
    video_id: str, issue_type: Optional[str] = None, fps: float = 30.0
) -> list[IssueFrame]:
    """Get frames that have issues, optionally filtered by issue type.

    Args:
        video_id: Unique video identifier
        issue_type: Optional issue type to filter by
        fps: Frame rate for time calculation (default 30.0)

    Returns:
        List of IssueFrame objects sorted by frame number
    """
    annotations = get_frame_annotations(video_id)
    issue_frames: list[IssueFrame] = []

    for frame in annotations:
        # Collect all issue types from this frame
        frame_issues: list[IssueType] = []

        for player in frame.players:
            for body_part in [player.body, player.hand_l, player.hand_r, player.foot_l, player.foot_r]:
                if body_part.issue_type:
                    frame_issues.append(body_part.issue_type)

        # Remove duplicates while preserving order
        unique_issues = list(dict.fromkeys(frame_issues))

        # Skip frames with no issues
        if not unique_issues:
            continue

        # Filter by requested issue type if specified
        if issue_type and issue_type not in unique_issues:
            continue

        # Calculate time based on frame number and actual FPS
        # Frame 1 = 0 seconds, Frame 2 = ~0.033s at 30fps, etc.
        time_seconds = (frame.frame_number - 1) / fps

        # Build thumbnail URL
        thumbnail_url = f"/api/annotated/{video_id}/{frame.frame_number}"

        issue_frame = IssueFrame(
            frame_number=frame.frame_number,
            issue_types=unique_issues,
            thumbnail_url=thumbnail_url,
            time_seconds=time_seconds,
        )
        issue_frames.append(issue_frame)

    return issue_frames


def get_annotated_image(video_id: str, frame_number: int) -> Path:
    """Get the path to an annotated frame image.

    Args:
        video_id: Unique video identifier
        frame_number: Frame number (1-indexed)

    Returns:
        Path to the annotated frame image

    Raises:
        FileNotFoundError: If the annotated image doesn't exist
    """
    annotated_dir = _get_annotated_dir(video_id)

    if not annotated_dir.exists():
        raise FileNotFoundError(f"Annotated frames directory not found for video {video_id}")

    # Try different image formats
    for ext in [".png", ".jpg", ".jpeg"]:
        # Try both frame_XXX.png and frame_X.png patterns
        for pattern in [f"frame_{frame_number:03d}{ext}", f"frame_{frame_number}{ext}"]:
            image_path = annotated_dir / pattern
            if image_path.exists():
                # Verify resolved path is still under ANALYSIS_DIR
                resolved = image_path.resolve()
                if not str(resolved).startswith(str(ANALYSIS_DIR.resolve())):
                    raise FileNotFoundError("Access denied")
                return image_path

    raise FileNotFoundError(
        f"Annotated frame {frame_number} not found for video {video_id}"
    )


def check_frames_exist(video_id: str) -> bool:
    """Check if frame annotations exist for a video.

    Args:
        video_id: Unique video identifier

    Returns:
        True if frames.json exists, False otherwise
    """
    return _get_frames_json_path(video_id).exists()