"""Pro video API routes."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from models.pro import ProVideo, ProVideoList, ProVideoType
from services.pro_service import list_pro_videos, get_pro_video, get_pro_video_path

router = APIRouter()


@router.get("/pros", response_model=ProVideoList)
async def list_pros(type: ProVideoType | None = None):
    """List all pro videos, optionally filtered by type."""
    videos = list_pro_videos(type)
    return {"videos": videos}


@router.get("/pros/{video_id}", response_model=ProVideo)
async def get_pro(video_id: str):
    """Get a single pro video by ID."""
    video = get_pro_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Pro video '{video_id}' not found")
    return video


@router.get("/pros/{video_id}/file")
async def get_pro_file(video_id: str):
    """Get the video file for a pro video."""
    path = get_pro_video_path(video_id)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail=f"Pro video file '{video_id}' not found")
    return FileResponse(path, media_type="video/mp4")