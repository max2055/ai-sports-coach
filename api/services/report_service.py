"""Service for parsing and generating coach analysis reports."""

import json
import re
from pathlib import Path
from typing import Optional

from models.report import (
    CoachReport,
    RadarScores,
    Strength,
    Issue,
    ImprovementSuggestion,
    IssueSummaryRow,
)

REPORT_DIR = Path("report/tennis")
ANALYSIS_DIR = Path("output/analysis")

# Issue type to body part mapping
ISSUE_BODY_MAP = {
    "LATE BACKSWING": "手臂",
    "WRONG GRIP": "手部",
    "GRIP CHANGE ERR": "手部",
    "WRONG CONTACT": "手臂",
    "ELBOW DROP": "手臂",
    "NO HIP ROT": "髋部",
    "LATE SHOULDER": "肩部",
    "NO FOLLOW-THRU": "手臂",
    "POOR FOOTWORK": "腿部",
    "NO SPLIT STEP": "腿部",
    "LATE WEIGHT": "腿部",
    "WRONG STANCE": "腿部",
    "WRONG POSITION": "全身",
    "BAD TOSS": "手臂",
    "NO LEG DRIVE": "腿部",
    "OFF BALANCE": "核心",
    "TELEGRAPH": "全身",
    "WRONG SPIN": "手臂",
}

# Priority mapping
PRIORITY_MAP = {
    "high": "high",
    "medium": "medium",
    "low": "low",
}


def extract_frame_refs(text: str) -> list[str]:
    """Extract Frame references from text using regex."""
    return re.findall(r"Frame\s+(\d+)", text)


def calculate_severity(frame_refs: list[str]) -> str:
    """Determine severity based on frame reference count."""
    count = len(frame_refs)
    if count >= 3:
        return "high"
    elif count >= 1:
        return "medium"
    return "low"


def parse_coach_report(markdown_path: Path) -> Optional[CoachReport]:
    """Parse a coach_*.md file into a structured CoachReport.

    Returns None if the file cannot be parsed.
    """
    if not markdown_path.exists():
        return None

    content = markdown_path.read_text(encoding="utf-8")

    # Parse Overall Score
    score_match = re.search(r"Overall Score:\s*(\d+)/10", content)
    overall_score = int(score_match.group(1)) if score_match else 5

    # Parse Strengths
    strengths = []
    strengths_section = re.search(r"## Strengths\n(.*?)(?=## |\Z)", content, re.DOTALL)
    if strengths_section:
        for line in strengths_section.group(1).strip().split("\n"):
            line = line.strip("- ").strip()
            if line:
                refs = extract_frame_refs(line)
                strengths.append(Strength(text=line, frame_refs=[f"Frame {r}" for r in refs]))

    # Parse Issues Found
    issues = []
    issues_section = re.search(r"## Issues Found\n(.*?)(?=## |\Z)", content, re.DOTALL)
    if issues_section:
        for line in issues_section.group(1).strip().split("\n"):
            line = line.strip("- ").strip()
            if line:
                refs = extract_frame_refs(line)
                severity = calculate_severity(refs)
                issues.append(
                    Issue(
                        text=line,
                        frame_refs=[f"Frame {r}" for r in refs],
                        severity=severity,
                    )
                )

    # Parse Improvement Suggestions
    suggestions = []
    improvements_section = re.search(r"## Improvement Suggestions\n(.*?)(?=## |\Z)", content, re.DOTALL)
    if improvements_section:
        for line in improvements_section.group(1).strip().split("\n"):
            line = line.strip()
            if line:
                num_match = re.match(r"(\d+)\.\s*(.*)", line)
                if num_match:
                    suggestions.append(
                        ImprovementSuggestion(
                            number=int(num_match.group(1)),
                            text=num_match.group(2),
                        )
                    )

    # Parse Coach Summary
    summary = ""
    summary_section = re.search(r"## Coach Summary\n(.*?)(?=## |\Z)", content, re.DOTALL)
    if summary_section:
        summary = summary_section.group(1).strip()

    return CoachReport(
        video_id="",  # Will be filled by caller
        overall_score=overall_score,
        radar_scores=RadarScores(),
        strengths=strengths,
        issues=issues,
        improvement_suggestions=suggestions,
        issue_summary=[],  # Filled from frames.json
        coach_summary=summary,
        training_plan="",  # Generated separately
    )


def extract_issue_summary(frames_json_path: Path) -> list[IssueSummaryRow]:
    """Extract issue summary from frames.json analysis data."""
    if not frames_json_path.exists():
        return []

    try:
        with open(frames_json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Invalid frames.json: {e}")
        return []

    rows = []
    frames = data.get("frames", {})
    issue_counts: dict[str, int] = {}

    for frame_num_str, frame_data in frames.items():
        frame_num = int(frame_num_str)
        for player in frame_data.get("players", []):
            for body_part in ["body", "hand_l", "hand_r", "foot_l", "foot_r"]:
                part_data = player.get(body_part, {})
                issue_type = part_data.get("issue_type", "")
                if issue_type and not issue_type.startswith("GOOD"):
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
                    rows.append(
                        IssueSummaryRow(
                            frame_number=frame_num,
                            issue_type=issue_type,
                            body_part=ISSUE_BODY_MAP.get(issue_type, "未知"),
                            description=issue_type,
                            priority="high" if issue_counts[issue_type] > 2 else "medium",
                        )
                    )

    return rows


def calculate_radar_scores(summary_path: Path) -> RadarScores:
    """Read radar scores from summary.json, or return defaults."""
    defaults = RadarScores()

    if not summary_path.exists():
        return defaults

    with open(summary_path) as f:
        summary = json.load(f)

    # Map summary keys to RadarScores
    mapping = {
        "击球技术": "hitting_technique",
        "步法移动": "footwork",
        "身体旋转": "body_rotation",
        "击球节奏": "timing",
        "体能分配": "fitness",
        "战术执行": "tactics",
    }

    scores_dict = {}
    if "dimensions" in summary:
        for dim in summary["dimensions"]:
            name = dim.get("name", "")
            value = dim.get("value", 5)
            key = mapping.get(name)
            if key:
                scores_dict[key] = value

    return RadarScores(**{k: scores_dict.get(k, 5) for k in RadarScores.model_fields})


def generate_training_plan(issues: list[Issue], radar_scores: RadarScores) -> str:
    """Generate a training plan based on identified issues and scores."""
    if not issues and not radar_scores:
        return "暂无训练建议。"

    plan_parts = []

    # Group issues by body part / type
    issue_texts = [i.text for i in issues]

    if any("髋肩" in t or "旋转" in t or "HIP" in t for t in issue_texts):
        plan_parts.append("1. 身体旋转练习：每天进行10分钟的髋肩旋转模拟训练，提高击球时的核心力量传导。")

    if any("击球点" in t or "CONTACT" in t or "位置" in t for t in issue_texts):
        plan_parts.append("2. 击球点定位练习：使用发球机或搭档喂球，专注于在身体最佳位置击球。")

    if any("随挥" in t or "FOLLOW" in t for t in issue_texts):
        plan_parts.append("3. 随挥完整性训练：每次击球后刻意完成完整随挥动作，形成肌肉记忆。")

    if any("步法" in t or "FOOT" in t or "移动" in t for t in issue_texts):
        plan_parts.append("4. 步法敏捷训练：进行绳梯、锥桶等步法敏捷性训练，提高移动速度和分步反应。")

    if any("平衡" in t or "BALANCE" in t for t in issue_texts):
        plan_parts.append("5. 核心稳定性训练：平板支撑、平衡板等核心力量练习，提升击球时的身体控制。")

    if radar_scores.footwork <= 4:
        plan_parts.append("步法专项训练：每周3次，每次20分钟的场上移动和分步练习。")

    if radar_scores.hitting_technique <= 4:
        plan_parts.append("击球技术专项：分解动作练习，重点关注引拍、击球、随挥三个阶段的连贯性。")

    if not plan_parts:
        plan_parts.append("继续保持当前训练强度，重点关注动作细节的打磨。")

    return "\n".join(plan_parts)


def get_report_for_video(video_id: str) -> Optional[CoachReport]:
    """Get a complete structured report for a video by ID.

    Searches for:
    1. output/analysis/{video_id}/summary.json
    2. output/analysis/{video_id}/frames.json
    3. Latest coach_*.md file as fallback

    Returns None if no report data is found.
    """
    report = None

    # Try to find coach report in output/analysis directory first
    analysis_dir = ANALYSIS_DIR / video_id
    if analysis_dir.exists():
        # Check for coach_*.md in analysis directory
        coach_files = list(analysis_dir.glob("coach_*.md"))
        if coach_files:
            report = parse_coach_report(max(coach_files, key=lambda p: p.stat().st_mtime))

    # Fallback: search report/tennis for latest coach file
    if report is None:
        coach_files = list(REPORT_DIR.glob("coach_*.md"))
        if coach_files:
            report = parse_coach_report(max(coach_files, key=lambda p: p.stat().st_mtime))

    if report is None:
        return None

    # Fill video_id
    report.video_id = video_id

    # Read radar scores from summary.json if available
    summary_path = analysis_dir / "summary.json"
    if summary_path.exists():
        report.radar_scores = calculate_radar_scores(summary_path)

    # Extract issue summary from frames.json if available
    frames_path = analysis_dir / "frames.json"
    if frames_path.exists():
        report.issue_summary = extract_issue_summary(frames_path)

    # Generate training plan
    report.training_plan = generate_training_plan(report.issues, report.radar_scores)

    return report
