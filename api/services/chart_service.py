"""Chart data extraction service.

Extracts metrics from analysis results for ECharts visualization.
"""

import json
import logging
from pathlib import Path

from models.chart import (
    ConsistencyRadar,
    HitPoint,
    HitPointHeatmap,
    IssueStat,
    IssueStatistics,
    RadarDimension,
    ServeHeightData,
    ServeHeightPoint,
)

logger = logging.getLogger(__name__)

ANALYSIS_DIR = Path("output/analysis")


def _get_frames_json_path(video_id: str) -> Path:
    """Get path to frames.json for a video."""
    return ANALYSIS_DIR / video_id / "frames.json"


def _get_summary_json_path(video_id: str) -> Path:
    """Get path to summary.json for a video."""
    return ANALYSIS_DIR / video_id / "summary.json"


def _load_frames_data(video_id: str) -> dict:
    """Load frames.json data for a video."""
    frames_path = _get_frames_json_path(video_id)
    if not frames_path.exists():
        raise FileNotFoundError(f"Frames data not found for video {video_id}")
    return json.loads(frames_path.read_text(encoding="utf-8"))


def _load_summary_data(video_id: str) -> dict | None:
    """Load summary.json data for a video."""
    summary_path = _get_summary_json_path(video_id)
    if not summary_path.exists():
        return None
    return json.loads(summary_path.read_text(encoding="utf-8"))


def get_serve_height_data(video_id: str) -> ServeHeightData:
    """Extract serve height data from frames.json.

    Serve frames are identified by:
    - issue_type containing "BAD TOSS" (serve toss issue)
    - Or frames during serve motion (first few frames)

    Args:
        video_id: Unique video identifier

    Returns:
        ServeHeightData with time series of body.y_pct values
    """
    frames_data = _load_frames_data(video_id)
    frames = frames_data.get("frames", {})

    points: list[ServeHeightPoint] = []

    for frame_key, frame_data in frames.items():
        try:
            frame_number = int(frame_key)
        except ValueError:
            continue

        # Check for serve-related frames (BAD TOSS indicates serve motion)
        is_serve_frame = False
        players = frame_data.get("players", [])

        for player in players:
            body = player.get("body", {})
            issue_type = body.get("issue_type")

            # BAD TOSS indicates serve frame
            if issue_type == "BAD TOSS":
                is_serve_frame = True

            # Also check first 3 frames as typical serve motion
            if frame_number <= 3:
                is_serve_frame = True

            if is_serve_frame and body:
                y_pct = body.get("y_pct", 0.5)
                time_seconds = (frame_number - 1) / 30.0  # Assuming 30fps
                points.append(
                    ServeHeightPoint(
                        frame_number=frame_number,
                        time_seconds=round(time_seconds, 3),
                        height_pct=round(y_pct, 4),
                    )
                )
                break  # One point per frame

    return ServeHeightData(points=points)


def get_hit_point_heatmap(video_id: str) -> HitPointHeatmap:
    """Extract hit point positions from frames.json.

    Uses hand_l (racket hand) x_pct/y_pct for hit point positions.

    Args:
        video_id: Unique video identifier

    Returns:
        HitPointHeatmap with all hit point positions
    """
    frames_data = _load_frames_data(video_id)
    frames = frames_data.get("frames", {})

    points: list[HitPoint] = []

    for frame_key, frame_data in frames.items():
        try:
            frame_number = int(frame_key)
        except ValueError:
            continue

        players = frame_data.get("players", [])

        for player in players:
            hand_l = player.get("hand_l", {})
            if hand_l:
                x_pct = hand_l.get("x_pct", 0.5)
                y_pct = hand_l.get("y_pct", 0.5)
                issue_type = hand_l.get("issue_type")

                points.append(
                    HitPoint(
                        frame_number=frame_number,
                        x_pct=round(x_pct, 4),
                        y_pct=round(y_pct, 4),
                        issue_type=issue_type,
                    )
                )

    return HitPointHeatmap(points=points)


def get_consistency_radar(video_id: str) -> ConsistencyRadar:
    """Extract 6-dimension consistency scores from summary.json.

    Dimensions:
    1. 击球技术 (Stroke Technique)
    2. 步法移动 (Footwork)
    3. 身体旋转 (Body Rotation)
    4. 击球节奏 (Stroke Rhythm)
    5. 体能分配 (Stamina/Endurance)
    6. 战术执行 (Tactical Execution)

    Args:
        video_id: Unique video identifier

    Returns:
        ConsistencyRadar with 6 dimensions and overall score
    """
    summary_data = _load_summary_data(video_id)

    # Default dimension names
    dimension_names = [
        "击球技术",
        "步法移动",
        "身体旋转",
        "击球节奏",
        "体能分配",
        "战术执行",
    ]

    dimensions: list[RadarDimension] = []
    overall_score = 5  # Default

    if summary_data:
        # Try to extract scores from summary
        scores = summary_data.get("scores", {})
        overall_score = summary_data.get("overall_score", 5)

        # Map scores to dimensions
        for name in dimension_names:
            # Look for matching score key (case-insensitive partial match)
            score = None
            for key, value in scores.items():
                key_lower = key.lower()
                if any(
                    kw in key_lower
                    for kw in [
                        name.lower(),
                        name[:2].lower(),
                        "technique" if "击球" in name else "",
                        "footwork" if "步法" in name else "",
                        "rotation" if "旋转" in name else "",
                        "rhythm" if "节奏" in name else "",
                        "stamina" if "体能" in name else "",
                        "tactic" if "战术" in name else "",
                    ]
                    if kw
                ):
                    score = value
                    break

            # Use overall_score as fallback if no specific score found
            if score is None:
                score = overall_score

            dimensions.append(RadarDimension(name=name, value=min(10, max(0, score))))

    else:
        # No summary data, use default scores
        for name in dimension_names:
            dimensions.append(RadarDimension(name=name, value=5))

    return ConsistencyRadar(dimensions=dimensions, overall_score=overall_score)


def get_issue_statistics(video_id: str) -> IssueStatistics:
    """Count issue types from frames.json.

    Args:
        video_id: Unique video identifier

    Returns:
        IssueStatistics with counts per issue type
    """
    frames_data = _load_frames_data(video_id)
    frames = frames_data.get("frames", {})

    issue_counts: dict[str, int] = {}
    total_frames = 0

    for frame_key, frame_data in frames.items():
        total_frames += 1
        players = frame_data.get("players", [])

        # Track issues in this frame (avoid counting same issue twice per frame)
        frame_issues: set[str] = set()

        for player in players:
            for body_part in ["body", "hand_l", "hand_r", "foot_l", "foot_r"]:
                part_data = player.get(body_part, {})
                issue_type = part_data.get("issue_type")
                if issue_type and issue_type not in ["GOOD FORM", "GOOD FOOTWORK", "GOOD TACTICS"]:
                    frame_issues.add(issue_type)

        for issue in frame_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

    # Sort by count descending
    sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

    # Build stats with severity
    stats: list[IssueStat] = []
    total_issues = 0

    for issue_type, count in sorted_issues:
        severity: Literal["high", "medium", "low"] = "low"
        if count > 3:
            severity = "high"
        elif count >= 2:
            severity = "medium"

        stats.append(IssueStat(issue_type=issue_type, count=count, severity=severity))
        total_issues += count

    return IssueStatistics(stats=stats, total_issues=total_issues, total_frames=total_frames)