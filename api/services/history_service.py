"""Service for managing analysis history — scan, search, filter, delete."""

import glob
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.history import HistoryEntry, HistoryList

ANALYSIS_DIR = Path("output/analysis")
UPLOAD_DIR = Path("output/uploads")
REPORT_DIR = Path("report/tennis")

ANALYSIS_TYPE_MAP = {
    "forehand": "forehand",
    "backhand": "backhand",
    "serve": "serve",
    "volley": "volley",
    "full": "full",
}


def _read_status_json(video_id: str) -> dict | None:
    """Read status.json for a given video_id."""
    status_path = ANALYSIS_DIR / video_id / "status.json"
    if not status_path.exists():
        return None
    with open(status_path) as f:
        return json.load(f)


def _read_summary_json(video_id: str) -> dict | None:
    """Read summary.json for a given video_id."""
    summary_path = ANALYSIS_DIR / video_id / "summary.json"
    if not summary_path.exists():
        return None
    with open(summary_path) as f:
        return json.load(f)


def _infer_filename(video_id: str) -> str:
    """Try to infer the original filename from status.json or uploads dir."""
    # Check status.json for filename
    status = _read_status_json(video_id)
    if status and status.get("filename"):
        return status["filename"]

    # Search uploads dir for matching files
    patterns = [f"{video_id}_*", f"*{video_id}*"]
    for pattern in patterns:
        matches = list(UPLOAD_DIR.glob(pattern))
        if matches:
            return matches[0].name

    return f"{video_id}"


def _entry_from_dir(video_id: str) -> Optional[HistoryEntry]:
    """Build a HistoryEntry from an analysis directory."""
    status = _read_status_json(video_id)
    if not status:
        return None

    raw_status = status.get("status", "pending")
    if raw_status not in ("completed", "failed", "pending"):
        raw_status = "pending"

    started_at = status.get("started_at")
    completed_at = status.get("completed_at")
    analysis_type = status.get("analysis_type", "full")
    duration = status.get("duration")

    # Parse timestamps
    created_at_dt = None
    completed_at_dt = None
    try:
        if started_at:
            created_at_dt = datetime.fromisoformat(started_at)
    except (ValueError, TypeError):
        pass
    try:
        if completed_at:
            completed_at_dt = datetime.fromisoformat(completed_at)
    except (ValueError, TypeError):
        pass

    if not created_at_dt:
        # Fallback to directory mtime
        dir_path = ANALYSIS_DIR / video_id
        if dir_path.exists():
            created_at_dt = datetime.fromtimestamp(dir_path.stat().st_mtime)
        else:
            created_at_dt = datetime.now()

    # Get overall_score from summary.json
    overall_score = None
    summary = _read_summary_json(video_id)
    if summary:
        overall_score = summary.get("overall_score")

    filename = _infer_filename(video_id)

    return HistoryEntry(
        video_id=video_id,
        filename=filename,
        analysis_type=analysis_type,
        status=raw_status,
        created_at=created_at_dt,
        completed_at=completed_at_dt,
        overall_score=overall_score,
        duration=duration,
    )


def list_history(
    search: str | None = None,
    analysis_type: str | None = None,
    status_filter: str | None = None,
) -> HistoryList:
    """Scan output/analysis/ and return history entries with optional filters."""
    if not ANALYSIS_DIR.exists():
        return HistoryList(entries=[], total=0)

    entries = []
    for video_dir in sorted(ANALYSIS_DIR.iterdir()):
        if not video_dir.is_dir():
            continue
        entry = _entry_from_dir(video_dir.name)
        if entry is None:
            continue

        # Apply filters
        if search and search.lower() not in entry.filename.lower():
            continue
        if analysis_type and entry.analysis_type != analysis_type:
            continue
        if status_filter and entry.status != status_filter:
            continue

        entries.append(entry)

    # Sort by created_at descending (newest first)
    entries.sort(key=lambda e: e.created_at, reverse=True)

    return HistoryList(entries=entries, total=len(entries))


def get_history_entry(video_id: str) -> Optional[HistoryEntry]:
    """Get a single history entry by video_id."""
    return _entry_from_dir(video_id)


def delete_history_entry(video_id: str) -> bool:
    """Delete analysis directory, associated uploads, and coach report files.

    Returns True if the analysis directory was found and deleted.
    """
    analysis_path = ANALYSIS_DIR / video_id
    if not analysis_path.exists():
        return False

    # Delete analysis directory
    shutil.rmtree(analysis_path)

    # Delete associated upload files
    if UPLOAD_DIR.exists():
        for upload_file in UPLOAD_DIR.glob(f"{video_id}_*"):
            upload_file.unlink(missing_ok=True)
        # Also try pattern without underscore
        for upload_file in UPLOAD_DIR.glob(f"*{video_id}*"):
            upload_file.unlink(missing_ok=True)

    # Delete associated coach report files
    if REPORT_DIR.exists():
        for report_file in REPORT_DIR.glob(f"coach_{video_id}*"):
            report_file.unlink(missing_ok=True)

    return True
