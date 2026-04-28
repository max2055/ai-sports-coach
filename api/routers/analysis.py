"""Analysis API router for starting and querying video analysis."""

from fastapi import APIRouter, BackgroundTasks, HTTPException

from models.analysis import AnalysisState, AnalysisResponse, AnalysisStatus
from services.analysis_service import (
    get_analysis_status,
    start_analysis,
    run_analysis,
    _find_video_path,
)

router = APIRouter()


@router.post("/analyze/{video_id}", response_model=AnalysisResponse)
async def start_video_analysis(
    video_id: str,
    background_tasks: BackgroundTasks,
    analysis_type: str = "full",
) -> AnalysisResponse:
    """Start asynchronous video analysis.

    Args:
        video_id: Unique video identifier from upload
        background_tasks: FastAPI background tasks for async execution
        analysis_type: Type of analysis (forehand, backhand, serve, volley, full)

    Returns:
        AnalysisResponse with initial status

    Raises:
        HTTPException: If video not found or analysis already running
    """
    # Validate video exists
    video_path = _find_video_path(video_id)
    if not video_path:
        raise HTTPException(
            status_code=404,
            detail=f"Video not found: {video_id}",
        )

    # Check for existing running analysis
    existing = get_analysis_status(video_id)
    if existing and existing.status in ("pending", "extracting", "analyzing", "annotating"):
        raise HTTPException(
            status_code=409,
            detail=f"Analysis already in progress for video {video_id}. Current status: {existing.status}",
        )

    # Start background analysis
    background_tasks.add_task(run_analysis, video_id, video_path, analysis_type)

    return AnalysisResponse(
        video_id=video_id,
        status="pending",
        progress=0,
        message="Analysis started successfully",
    )


@router.get("/status/{video_id}", response_model=AnalysisState)
async def get_video_analysis_status(video_id: str) -> AnalysisState:
    """Get current analysis status for a video.

    Args:
        video_id: Unique video identifier

    Returns:
        AnalysisState with current progress and status

    Raises:
        HTTPException: If no analysis found for this video
    """
    status = get_analysis_status(video_id)
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for video {video_id}",
        )

    return status


@router.post("/retry/{video_id}", response_model=AnalysisResponse)
async def retry_analysis(
    video_id: str,
    background_tasks: BackgroundTasks,
    analysis_type: str = "full",
) -> AnalysisResponse:
    """Retry a failed analysis.

    Args:
        video_id: Unique video identifier
        background_tasks: FastAPI background tasks
        analysis_type: Type of analysis

    Returns:
        AnalysisResponse with new status

    Raises:
        HTTPException: If video not found or analysis not in failed state
    """
    # Validate video exists
    video_path = _find_video_path(video_id)
    if not video_path:
        raise HTTPException(
            status_code=404,
            detail=f"Video not found: {video_id}",
        )

    # Check previous status
    existing = get_analysis_status(video_id)
    if existing and existing.status not in ("failed", "completed"):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot retry: current status is {existing.status}",
        )

    # Start new analysis
    background_tasks.add_task(run_analysis, video_id, video_path, analysis_type)

    return AnalysisResponse(
        video_id=video_id,
        status="pending",
        progress=0,
        message="Analysis retry started",
    )