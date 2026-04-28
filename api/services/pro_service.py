"""Service for managing pro video library."""

import json
import subprocess
from pathlib import Path
from models.pro import ProVideo, ProVideoType

PROS_DIR = Path("static/pros")
MANIFEST_FILE = PROS_DIR / "manifest.json"


def load_manifest() -> dict:
    """Load manifest.json from static/pros."""
    if not MANIFEST_FILE.exists():
        return {"videos": []}
    with open(MANIFEST_FILE) as f:
        return json.load(f)


def get_video_duration(file_path: Path) -> float | None:
    """Get video duration using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:
        pass
    return None


def list_pro_videos(video_type: ProVideoType | None = None) -> list[ProVideo]:
    """List all pro videos, optionally filtered by type."""
    manifest = load_manifest()
    videos = []
    for v in manifest.get("videos", []):
        if video_type and v.get("type") != video_type:
            continue
        file_path = PROS_DIR / v["file"]
        duration = get_video_duration(file_path) if file_path.exists() else None
        videos.append(ProVideo(
            id=v["id"],
            type=v["type"],
            name=v["name"],
            description=v["description"],
            file=v["file"],
            duration=duration
        ))
    return videos


def get_pro_video(video_id: str) -> ProVideo | None:
    """Get a single pro video by ID."""
    manifest = load_manifest()
    for v in manifest.get("videos", []):
        if v["id"] == video_id:
            file_path = PROS_DIR / v["file"]
            duration = get_video_duration(file_path) if file_path.exists() else None
            return ProVideo(
                id=v["id"],
                type=v["type"],
                name=v["name"],
                description=v["description"],
                file=v["file"],
                duration=duration
            )
    return None


def get_pro_video_path(video_id: str) -> Path | None:
    """Get the file path for a pro video."""
    video = get_pro_video(video_id)
    if video:
        return PROS_DIR / video.file
    return None