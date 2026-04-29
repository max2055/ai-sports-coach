"""Frame annotation API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from models.frame import FrameAnnotation, IssueFrame
from services.frame_service import (
    check_frames_exist,
    get_annotated_image,
    get_frame_annotations,
    get_issue_frames,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/frames/{video_id}", response_model=list[FrameAnnotation])
async def list_frame_annotations(video_id: str) -> list[FrameAnnotation]:
    """Get all frame annotations for a video.

    Args:
        video_id: Unique video identifier

    Returns:
        List of frame annotations with player positions and issue data

    Raises:
        HTTPException: 404 if video analysis not found
    """
    try:
        return get_frame_annotations(video_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Frame annotations not found for video {video_id}",
        )
    except ValueError as e:
        logger.error(f"Invalid frame data for video {video_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Invalid frame data: {e}",
        )


@router.get("/issues/{video_id}", response_model=list[IssueFrame])
async def list_issue_frames(
    video_id: str,
    issue_type: Optional[str] = None,
    fps: float = 30.0,
) -> list[IssueFrame]:
    """Get frames that have issues, optionally filtered by type.

    Args:
        video_id: Unique video identifier
        issue_type: Optional issue type to filter by (e.g., "LATE BACKSWING")
        fps: Frame rate for time calculation (default 30.0)

    Returns:
        List of frames with issues, including thumbnail URLs and timestamps

    Raises:
        HTTPException: 404 if video analysis not found
    """
    try:
        return get_issue_frames(video_id, issue_type, fps)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Frame annotations not found for video {video_id}",
        )
    except ValueError as e:
        logger.error(f"Invalid frame data for video {video_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Invalid frame data: {e}",
        )


@router.get("/annotated/{video_id}/{frame_number}")
async def get_annotated_frame(video_id: str, frame_number: int) -> FileResponse:
    """Get an annotated frame image.

    Args:
        video_id: Unique video identifier
        frame_number: Frame number (1-indexed)

    Returns:
        Annotated frame image file

    Raises:
        HTTPException: 404 if annotated frame not found
    """
    try:
        image_path = get_annotated_image(video_id, frame_number)
        media_type = "image/jpeg" if image_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        return FileResponse(
            path=image_path,
            media_type=media_type,
            filename=f"frame_{frame_number:03d}{image_path.suffix}",
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Annotated frame {frame_number} not found for video {video_id}",
        )


@router.get("/frames/{video_id}/exists")
async def check_frames(video_id: str) -> dict:
    """Check if frame annotations exist for a video.

    Args:
        video_id: Unique video identifier

    Returns:
        JSON with exists boolean
    """
    exists = check_frames_exist(video_id)
    return {"video_id": video_id, "exists": exists}