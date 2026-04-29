"""Video processing service for extracting metadata and saving files."""

import json
import subprocess
import uuid
from pathlib import Path
from typing import Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "output" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def extract_video_metadata(file_path: Path) -> Tuple[float, int, int]:
    """Extract video metadata using ffprobe.

    Args:
        file_path: Path to the video file

    Returns:
        Tuple of (duration_seconds, width, height)

    Raises:
        RuntimeError: If ffprobe fails or returns invalid data
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,duration",
        "-of",
        "json",
        str(file_path),
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=30
        )
        data = json.loads(result.stdout)

        if not data.get("streams"):
            raise RuntimeError("No video streams found in file")

        stream = data["streams"][0]
        duration = stream.get("duration")
        width = stream.get("width")
        height = stream.get("height")

        if not duration or not width or not height:
            raise RuntimeError("Incomplete video metadata: duration, width, or height missing")

        return float(duration), int(width), int(height)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed: {e.stderr}") from e
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise RuntimeError(f"Failed to parse ffprobe output: {e}") from e


def generate_video_id() -> str:
    """Generate a unique video ID."""
    return uuid.uuid4().hex[:12]


def save_uploaded_video(file_content: bytes, filename: str, video_id: str) -> Path:
    """Save uploaded video file to disk.

    Args:
        file_content: Raw bytes of the uploaded file
        filename: Original filename
        video_id: Unique identifier for this video

    Returns:
        Path to the saved file
    """
    # Sanitize filename: keep only safe characters
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    if not safe_filename:
        safe_filename = "video.mp4"

    file_path = UPLOAD_DIR / f"{video_id}_{safe_filename}"
    file_path.write_bytes(file_content)
    return file_path


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    return file_path.stat().st_size


def get_video_format(filename: str) -> str:
    """Extract video format from filename extension."""
    ext = Path(filename).suffix.lower()
    return ext.lstrip(".") if ext else "unknown"
