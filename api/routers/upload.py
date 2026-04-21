"""Upload API router for handling video file uploads."""

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pathlib import Path

from models.upload import UploadResponse, VideoMetadata, AnalysisType
from services.video_service import (
    extract_video_metadata,
    generate_video_id,
    save_uploaded_video,
    get_file_size,
    get_video_format,
)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(..., description="Video file to upload"),
    analysis_type: AnalysisType = Form(..., description="Type of analysis to perform"),
) -> UploadResponse:
    """Upload a video file for analysis.

    Args:
        file: The video file to upload (mp4, mov, avi, mkv supported)
        analysis_type: Type of analysis (forehand, backhand, serve, volley, full)

    Returns:
        UploadResponse with video_id, metadata, and confirmation message

    Raises:
        HTTPException: If file is invalid or processing fails
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed: {', '.join(sorted(allowed_extensions))}",
        )

    try:
        # Read file content
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")

        # Generate unique ID and save file
        video_id = generate_video_id()
        file_path = save_uploaded_video(content, file.filename, video_id)

        # Extract metadata
        duration, width, height = extract_video_metadata(file_path)
        size = get_file_size(file_path)
        format_str = get_video_format(file.filename)

        metadata = VideoMetadata(
            duration=duration,
            width=width,
            height=height,
            size=size,
            format=format_str,
        )

        return UploadResponse(
            video_id=video_id,
            filename=file.filename,
            analysis_type=analysis_type,
            metadata=metadata,
            message="Video uploaded successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process upload: {str(e)}"
        ) from e
