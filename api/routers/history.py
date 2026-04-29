"""History API routes for listing, viewing, and deleting analysis records."""

from fastapi import APIRouter, HTTPException

from models.history import HistoryEntry, HistoryList
from services.history_service import list_history, get_history_entry, delete_history_entry

router = APIRouter()


@router.get("/history", response_model=HistoryList)
async def get_history(
    search: str | None = None,
    analysis_type: str | None = None,
    status_filter: str | None = None,
):
    """List all history entries with optional search and filters."""
    return list_history(search=search, analysis_type=analysis_type, status_filter=status_filter)


@router.get("/history/{video_id}", response_model=HistoryEntry)
async def get_history_item(video_id: str):
    """Get a single history entry by video_id."""
    entry = get_history_entry(video_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"History entry '{video_id}' not found")
    return entry


@router.delete("/history/{video_id}")
async def delete_history_item(video_id: str):
    """Delete a history entry and all associated files."""
    success = delete_history_entry(video_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"History entry '{video_id}' not found")
    return {"message": f"History entry '{video_id}' deleted"}
