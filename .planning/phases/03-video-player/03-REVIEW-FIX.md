---
phase: 03-video-player
fixed_at: 2026-04-29T13:19:00Z
review_path: .planning/phases/03-video-player/03-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-04-29T13:19:00Z
**Source review:** .planning/phases/03-video-player/03-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 6
- Fixed: 6
- Skipped: 0

## Fixed Issues

### CR-01: Path Traversal Vulnerability in Frame Service

**Files modified:** `api/services/frame_service.py`
**Commit:** 0fcb111
**Applied fix:** Added `_VIDEO_ID_PATTERN` regex validation (alphanumeric, underscores, hyphens only) in `_get_analysis_dir()` that raises `ValueError` for invalid video_ids. Added path resolution check in `get_annotated_image()` to verify the resolved file path is still under `ANALYSIS_DIR`, raising `FileNotFoundError("Access denied")` if traversal is detected.

### CR-02: issue_type Data Format Mismatch Between tennis_annotate.py and Backend Models

**Files modified:** `api/services/frame_service.py`
**Commit:** 0fcb111
**Applied fix:** Added `_ISSUE_TYPE_MAP` dictionary mapping all 21 snake_case keys from `tennis_annotate.py` (e.g., `"late_backswing"`) to the uppercase `IssueType` Literal values (e.g., `"LATE BACKSWING"`). Updated `_parse_body_part()` to look up the raw `issue_type` through this mapping before constructing `BodyPartAnnotation`, ensuring Pydantic validation passes.

### CR-03: Frame Index Off-By-One Between Frontend and Backend

**Files modified:** `web/src/components/AnnotatedVideoPlayer.vue`
**Commit:** c87a626
**Applied fix:** Added `+ 1` to the `getFrameNumber()` computation (`Math.floor(time * videoFps.value) + 1`) so the frontend uses 1-indexed frame numbers matching the backend's 1-indexed `frame_number` values from `tennis_annotate.py`.

### WR-01: Hardcoded 30fps Assumption for Time Calculation

**Files modified:** `api/services/frame_service.py`, `api/routers/frames.py`
**Commit:** 0fcb111 (service), fd846ef (router)
**Applied fix:** Added `fps: float = 30.0` parameter to `get_issue_frames()` in the service layer and to `list_issue_frames()` router endpoint. Time calculation now uses `(frame.frame_number - 1) / fps` instead of hardcoded `30.0`. Clients can pass the actual video FPS as a query parameter.

### WR-02: Canvas May Be Sized to Video Resolution Instead of Display Size

**Files modified:** `web/src/components/AnnotatedVideoPlayer.vue`
**Commit:** c87a626
**Applied fix:** Added guard `if (w === 0 || h === 0) return` in `resizeCanvas()` to prevent canvas from being initialized with zero dimensions before `loadedmetadata` fires. Uses `video.videoWidth || video.clientWidth` fallback pattern.

### WR-03: Annotated Image Endpoint Fails for JPEG Format

**Files modified:** `api/routers/frames.py`
**Commit:** fd846ef
**Applied fix:** Changed `FileResponse` to dynamically detect the actual file extension and set the correct `media_type` (`"image/jpeg"` for `.jpg`/`.jpeg`, `"image/png"` otherwise). The `filename` parameter now uses the actual `image_path.suffix` instead of hardcoded `.png`.

## Skipped Issues

None -- all in-scope findings were successfully fixed.

---

_Fixed: 2026-04-29T13:19:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
