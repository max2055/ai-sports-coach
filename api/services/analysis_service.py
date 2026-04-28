"""Analysis service for async video processing.

Wraps coach.py and tennis_annotate.py for FastAPI BackgroundTasks.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from models.analysis import AnalysisState, AnalysisStatus

load_dotenv()

logger = logging.getLogger(__name__)

# Output directories
ANALYSIS_DIR = Path("output/analysis")
UPLOAD_DIR = Path("output/uploads")


def _get_status_path(video_id: str) -> Path:
    """Get path to status.json for a video."""
    return ANALYSIS_DIR / video_id / "status.json"


def _get_analysis_dir(video_id: str) -> Path:
    """Get analysis output directory for a video."""
    return ANALYSIS_DIR / video_id


def _ensure_analysis_dir(video_id: str) -> Path:
    """Ensure analysis directory exists and return path."""
    dir_path = _get_analysis_dir(video_id)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def _save_status(video_id: str, state: AnalysisState) -> None:
    """Save analysis state to status.json."""
    status_path = _get_status_path(video_id)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")


def get_analysis_status(video_id: str) -> Optional[AnalysisState]:
    """Read analysis status from JSON file.

    Args:
        video_id: Unique video identifier

    Returns:
        AnalysisState if status file exists, None otherwise
    """
    status_path = _get_status_path(video_id)
    if not status_path.exists():
        return None

    try:
        data = json.loads(status_path.read_text(encoding="utf-8"))
        return AnalysisState(**data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse status file for {video_id}: {e}")
        return None


def _find_video_path(video_id: str) -> Optional[Path]:
    """Find uploaded video file by video_id.

    Args:
        video_id: Unique video identifier

    Returns:
        Path to video file if found, None otherwise
    """
    for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        pattern = f"{video_id}_*{ext}"
        matches = list(UPLOAD_DIR.glob(pattern))
        if matches:
            return matches[0]
    return None


def _update_status(
    video_id: str,
    status: AnalysisStatus,
    progress: int,
    error: Optional[str] = None,
    result_path: Optional[str] = None,
    frames_dir: Optional[str] = None,
    annotated_dir: Optional[str] = None,
) -> None:
    """Update analysis status file."""
    current = get_analysis_status(video_id)
    if current is None:
        current = AnalysisState(
            video_id=video_id,
            status=status,
            progress=progress,
            started_at=datetime.utcnow(),
        )
    else:
        current.status = status
        current.progress = progress

    if error:
        current.error = error
    if result_path:
        current.result_path = result_path
    if frames_dir:
        current.frames_dir = frames_dir
    if annotated_dir:
        current.annotated_dir = annotated_dir
    if status == "completed":
        current.completed_at = datetime.utcnow()

    _save_status(video_id, current)


def run_analysis(video_id: str, video_path: Path, analysis_type: str = "full") -> None:
    """Run video analysis asynchronously.

    This function wraps coach.py and tennis_annotate.py logic:
    1. Extract frames from video
    2. Analyze frames with GPT-4o Vision (coach.py)
    3. Generate annotated frames and report (tennis_annotate.py)

    Args:
        video_id: Unique identifier for the video
        video_path: Path to the uploaded video file
        analysis_type: Type of analysis (forehand, backhand, serve, volley, full)
    """
    analysis_dir = _ensure_analysis_dir(video_id)
    frames_dir = analysis_dir / "frames"
    annotated_dir = analysis_dir / "annotated"

    try:
        # Step 1: Initialize status
        _update_status(
            video_id,
            status="pending",
            progress=0,
            frames_dir=str(frames_dir),
            annotated_dir=str(annotated_dir),
        )

        # Step 2: Extract frames
        _update_status(video_id, status="extracting", progress=10)

        from src.video import extract_frames, FrameExtractionError

        frames = extract_frames(video_path, frames_dir, num_frames=12)
        logger.info(f"Extracted {len(frames)} frames for video {video_id}")
        _update_status(video_id, status="extracting", progress=25)

        # Step 3: Analyze frames with GPT-4o (coach.py style)
        _update_status(video_id, status="analyzing", progress=30)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        from src.analyzer import analyze_frames, AnalyzerError

        context = f"Tennis training video - {analysis_type} analysis"
        result = analyze_frames(frames, context, api_key=api_key)
        logger.info(f"Analysis complete for {video_id}: {result.sport}, score {result.score}/10")
        _update_status(video_id, status="analyzing", progress=60)

        # Step 4: Generate coach report
        from src.report import generate_report
        from src.search import fetch_reference_images

        refs_dir = analysis_dir / "references"
        references = fetch_reference_images(result.sport, refs_dir)
        report_path = generate_report(
            result=result,
            context=context,
            frames=frames,
            references=references,
            output_dir=analysis_dir,
        )
        logger.info(f"Generated coach report at {report_path}")
        _update_status(video_id, status="annotating", progress=70)

        # Step 5: Run tennis annotation (tennis_annotate.py style)
        annotated_dir.mkdir(parents=True, exist_ok=True)

        # Import tennis annotation functions
        from tennis_annotate import call_gpt4o, annotate_frame, generate_report as generate_tennis_report

        # Get frame-annotated analysis from GPT-4o
        annotation_data = call_gpt4o(frames)
        logger.info(f"GPT-4o tennis annotation complete for {video_id}")
        _update_status(video_id, status="annotating", progress=85)

        # Annotate each frame
        annotated_map: dict[str, Path] = {}
        for i, frame_path in enumerate(frames, 1):
            fn_key = str(i)
            finfo = annotation_data.get("frames", {}).get(fn_key, {})
            out_path = annotated_dir / frame_path.name
            try:
                annotate_frame(frame_path, finfo, out_path)
                annotated_map[fn_key] = out_path
            except Exception as e:
                logger.warning(f"Failed to annotate frame {i}: {e}")
                # Copy original frame if annotation fails
                import shutil
                shutil.copy(frame_path, out_path)
                annotated_map[fn_key] = out_path

        _update_status(video_id, status="annotating", progress=95)

        # Generate tennis report
        tennis_report = generate_tennis_report(annotation_data, annotated_map)
        tennis_report_path = analysis_dir / f"tennis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        tennis_report_path.write_text(tennis_report, encoding="utf-8")
        logger.info(f"Generated tennis report at {tennis_report_path}")

        # Step 6: Mark complete
        _update_status(
            video_id,
            status="completed",
            progress=100,
            result_path=str(analysis_dir),
        )

    except FrameExtractionError as e:
        logger.error(f"Frame extraction failed for {video_id}: {e}")
        _update_status(video_id, status="failed", progress=0, error=str(e))

    except AnalyzerError as e:
        logger.error(f"Analysis failed for {video_id}: {e}")
        _update_status(video_id, status="failed", progress=0, error=str(e))

    except RuntimeError as e:
        logger.error(f"Runtime error for {video_id}: {e}")
        _update_status(video_id, status="failed", progress=0, error=str(e))

    except Exception as e:
        logger.exception(f"Unexpected error analyzing {video_id}: {e}")
        _update_status(video_id, status="failed", progress=0, error=f"Unexpected error: {e}")


async def run_analysis_async(video_id: str, video_path: Path, analysis_type: str = "full") -> None:
    """Async wrapper for run_analysis to be used with BackgroundTasks.

    Args:
        video_id: Unique identifier for the video
        video_path: Path to the uploaded video file
        analysis_type: Type of analysis
    """
    # Run the synchronous analysis in a thread pool
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_analysis, video_id, video_path, analysis_type)


def start_analysis(video_id: str, analysis_type: str = "full") -> tuple[bool, Optional[str]]:
    """Start a new analysis for a video.

    Validates that the video exists and no analysis is already running.

    Args:
        video_id: Unique video identifier
        analysis_type: Type of analysis to perform

    Returns:
        Tuple of (success, error_message)
    """
    # Check if video exists
    video_path = _find_video_path(video_id)
    if not video_path:
        return False, f"Video not found: {video_id}"

    # Check for existing analysis
    existing = get_analysis_status(video_id)
    if existing and existing.status in ("pending", "extracting", "analyzing", "annotating"):
        return False, f"Analysis already in progress for video {video_id}"

    # Initialize pending status
    _update_status(video_id, status="pending", progress=0, frames_dir=None, annotated_dir=None)

    return True, None