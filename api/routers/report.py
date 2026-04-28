"""Report API routes for structured coach analysis reports."""

from fastapi import APIRouter, HTTPException

from models.report import CoachReport
from services.report_service import get_report_for_video

router = APIRouter()


@router.get("/report/{video_id}", response_model=CoachReport)
async def get_report(video_id: str):
    """Get structured coach analysis report for a video."""
    report = get_report_for_video(video_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report for video '{video_id}' not found")
    return report
