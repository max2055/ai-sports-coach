---
phase: 03-video-player
reviewed: 2026-04-29T12:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - api/models/frame.py
  - api/routers/frames.py
  - api/services/frame_service.py
  - web/src/api/frames.ts
  - web/src/components/AnnotatedVideoPlayer.vue
  - web/src/components/FrameTimeline.vue
  - web/src/components/IssueFrameList.vue
  - web/src/components/KeyframeMarker.vue
  - web/src/views/ReportView.vue
findings:
  critical: 3
  warning: 3
  info: 4
  total: 10
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-04-29
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Reviewed the video player with annotation overlay phase, covering backend frame annotation endpoints, frontend video player components, timeline scrubber, and issue frame list. The codebase has a well-structured separation of concerns, but there are **three critical issues** that will prevent the feature from working correctly or expose security vulnerabilities: (1) path traversal in file serving endpoints, (2) a data format mismatch between `tennis_annotate.py` output and the backend Pydantic models that will cause all frame annotation requests to return 500 errors, and (3) a frame indexing off-by-one error that will prevent annotations from rendering even if the data loads successfully.

## Critical Issues

### CR-01: Path Traversal Vulnerability in Frame Service

**File:** `api/services/frame_service.py:18`
**Issue:** The `video_id` parameter from user-controlled URL paths is used directly in filesystem path construction without any sanitization. An attacker can pass `video_id=../../../etc/passwd` to read arbitrary files via the `/api/annotated/{video_id}/{frame_number}` endpoint, or `video_id=../../` to access files outside the analysis directory via any frames endpoint. This is exploitable through `get_annotated_image()` (line 179-194) and `get_frame_annotations()` (line 44).

**Fix:** Validate `video_id` against a safe pattern (alphanumeric + hyphens only) and reject any path traversal characters:

```python
import re

_VIDEO_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

def _get_analysis_dir(video_id: str) -> Path:
    """Get the analysis output directory for a video."""
    if not _VIDEO_ID_PATTERN.match(video_id):
        raise ValueError(f"Invalid video_id: {video_id}")
    return ANALYSIS_DIR / video_id
```

Additionally, in `get_annotated_image()`, verify the resolved path is still under `ANALYSIS_DIR`:

```python
def get_annotated_image(video_id: str, frame_number: int) -> Path:
    # ... existing validation ...
    image_path = annotated_dir / pattern
    if image_path.exists():
        resolved = image_path.resolve()
        if not str(resolved).startswith(str(ANALYSIS_DIR.resolve())):
            raise FileNotFoundError("Access denied")
        return image_path
```

### CR-02: issue_type Data Format Mismatch Between tennis_annotate.py and Backend Models

**File:** `api/services/frame_service.py:108`, `api/models/frame.py:8-30`
**Issue:** `tennis_annotate.py` stores `issue_type` values in frames.json using **snake_case keys** (e.g., `"late_backswing"`, `"good_form"`) -- exactly as defined in the GPT-4o prompt (lines 48-75, 102-123). However, the backend `IssueType` Literal in `api/models/frame.py` expects **uppercase with spaces** (e.g., `"LATE BACKSWING"`, `"GOOD FORM"`). When Pydantic v2 tries to validate `"late_backswing"` against the `IssueType` Literal, validation fails. This propagates as an unhandled exception through `get_frame_annotations()`, and the router catches it as `ValueError`, returning HTTP 500 for every frame annotation request. **The entire `/api/frames/{video_id}` endpoint will never return data successfully.**

The `ISSUE_LABELS` dict in `tennis_annotate.py` (lines 48-75) does map snake_case to uppercase -- but this mapping is only used for drawing labels on images, NOT for the JSON data stored in frames.json.

**Fix:** Convert snake_case issue types to uppercase format during parsing in `_parse_body_part()`:

```python
# Mapping from tennis_annotate.py snake_case keys to backend uppercase values
_ISSUE_TYPE_MAP = {
    "late_backswing": "LATE BACKSWING",
    "wrong_grip": "WRONG GRIP",
    "grip_change_error": "GRIP CHANGE ERR",
    "wrong_contact_point": "WRONG CONTACT",
    "elbow_drop": "ELBOW DROP",
    "no_hip_rotation": "NO HIP ROT",
    "shoulder_rot_late": "LATE SHOULDER",
    "poor_follow_through": "NO FOLLOW-THRU",
    "poor_footwork": "POOR FOOTWORK",
    "no_split_step": "NO SPLIT STEP",
    "late_weight_transfer": "LATE WEIGHT",
    "wrong_stance": "WRONG STANCE",
    "wrong_court_position": "WRONG POSITION",
    "poor_serve_toss": "BAD TOSS",
    "no_leg_drive": "NO LEG DRIVE",
    "off_balance": "OFF BALANCE",
    "telegraphing": "TELEGRAPH",
    "wrong_spin": "WRONG SPIN",
    "good_form": "GOOD FORM",
    "good_footwork": "GOOD FOOTWORK",
    "good_tactics": "GOOD TACTICS",
}

def _parse_body_part(data: dict) -> BodyPartAnnotation:
    raw_issue = data.get("issue_type", "")
    mapped_issue = _ISSUE_TYPE_MAP.get(raw_issue) if raw_issue else None
    return BodyPartAnnotation(
        x_pct=float(data.get("x_pct", 0.0)),
        y_pct=float(data.get("y_pct", 0.0)),
        radius_pct=float(data.get("radius_pct", 0.03)),
        issue_type=mapped_issue,
        issue_note=data.get("issue_note") or None,
    )
```

### CR-03: Frame Index Off-By-One Between Frontend and Backend

**File:** `web/src/components/AnnotatedVideoPlayer.vue:45-46`, `api/services/frame_service.py:150`
**Issue:** The backend uses **1-indexed** frame numbers (frame 1 = first frame, as produced by `tennis_annotate.py` line 298: `for i, frame_path in enumerate(frames, 1)`). The frontend `getFrameNumber()` uses `Math.floor(time * fps)` which returns **0-indexed** frame numbers (frame 0 at time 0). When `findFrameAnnotation()` searches for frame 0, it finds nothing since backend annotations start at frame 1. Annotations will never display.

**Fix:** Align the frontend to use 1-indexed frames:

```typescript
const getFrameNumber = (time: number): number => {
  return Math.floor(time * videoFps.value) + 1  // +1 to match backend 1-indexing
}
```

Alternatively, store 0-indexed frames in the backend. The `time_seconds` calculation on line 150 already accounts for 1-indexing (`(frame.frame_number - 1) / 30.0`), so the backend just needs consistency.

## Warnings

### WR-01: Hardcoded 30fps Assumption for Time Calculation

**File:** `api/services/frame_service.py:148-150`
**Issue:** `time_seconds` is calculated as `(frame.frame_number - 1) / 30.0`, assuming a fixed 30fps. If videos have different frame rates (24fps, 60fps, variable), all timestamps will be wrong. This affects the timeline markers, issue frame list time display, and seek-to-time functionality.

**Fix:** Either (a) accept `fps` as a configurable parameter stored per-video in metadata, or (b) calculate from actual video duration and total frame count:

```python
def get_issue_frames(
    video_id: str, issue_type: Optional[str] = None, fps: float = 30.0
) -> list[IssueFrame]:
    # ...
    time_seconds = (frame.frame_number - 1) / fps
```

### WR-02: Canvas May Be Sized to Video Resolution Instead of Display Size

**File:** `web/src/components/AnnotatedVideoPlayer.vue:161-162`
**Issue:** `resizeCanvas()` sets `canvas.width = video.videoWidth` (the native video resolution, e.g., 1920x1080) while the canvas is CSS-sized to fill the container (e.g., 800x450). Canvas pixel coordinates and CSS pixel coordinates differ at this scale. The annotation coordinates (percentages) happen to work because both canvas and video use the same aspect ratio, but the `player.id` label position on line 116 uses `player.body.x_pct * canvasWidth` which positions the label at the body center on the large canvas, then scales down. If the video display size and native resolution differ significantly, the visual alignment of labels and issue rings may appear slightly off.

More critically, if `videoWidth`/`videoHeight` are 0 (before `loadedmetadata` fires), the canvas gets 0 dimensions and annotations are invisible.

**Fix:** Use `video.clientWidth` and `video.clientHeight` consistently, and add a guard for zero dimensions:

```typescript
const resizeCanvas = () => {
  const video = videoRef.value
  const canvas = canvasRef.value
  if (!video || !canvas) return

  const w = video.videoWidth || video.clientWidth
  const h = video.videoHeight || video.clientHeight
  if (w === 0 || h === 0) return  // Guard against zero dimensions

  canvas.width = w
  canvas.height = h
  drawAnnotations()
}
```

### WR-03: Annotated Image Endpoint Fails for JPEG Format

**File:** `api/services/frame_service.py:185-190`
**Issue:** `tennis_annotate.py` saves annotated frames as **JPEG** files (line 567: `combined.save(out_path, "JPEG", quality=90)`) with `.jpg` extension. The `get_annotated_image()` function checks for `.png`, `.jpg`, `.jpeg` in that order. The `FileResponse` in `api/routers/frames.py:99` hardcodes `media_type="image/png"`, which will be incorrect for JPEG images. Browsers may refuse to render the image or display it with wrong MIME type.

**Fix:** Detect the actual file extension and set the correct media type:

```python
@router.get("/annotated/{video_id}/{frame_number}")
async def get_annotated_frame(video_id: str, frame_number: int) -> FileResponse:
    try:
        image_path = get_annotated_image(video_id, frame_number)
        media_type = "image/jpeg" if image_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        return FileResponse(
            path=image_path,
            media_type=media_type,
            filename=f"frame_{frame_number:03d}{image_path.suffix}",
        )
    except FileNotFoundError:
        # ...
```

## Info

### IN-01: Unused Imports

**Files:**
- `api/routers/frames.py:9` -- `IssueFrame` imported but never used (only passed as `response_model` which uses `list[IssueFrame]` syntax inline)
- `web/src/api/frames.ts:2` -- `AnalysisType` imported but never referenced
- `web/src/components/KeyframeMarker.vue:2` -- `watch` imported but never used (the watch on line 58 is a no-op)

**Fix:** Remove unused imports to reduce confusion and bundle size.

### IN-02: Redundant Logic in isPositiveIssue

**File:** `web/src/components/IssueFrameList.vue:75-77`
**Issue:** `isPositiveIssue()` checks `type.startsWith('GOOD')` AND then redundantly checks for `'GOOD FORM'`, `'GOOD FOOTWORK'`, `'GOOD TACTICS'` individually. The `startsWith('GOOD')` check already covers all three cases. Same redundant pattern exists in `FrameTimeline.vue:34-36`.

**Fix:**
```typescript
const isPositiveIssue = (type: IssueType): boolean => {
  return type.startsWith('GOOD')
}
```

### IN-03: Empty video_id Edge Case Not Handled

**File:** `api/services/frame_service.py:46`
**Issue:** If `video_id` is an empty string, `_get_frames_json_path("")` returns `output/analysis/frames.json`, which could be a legitimate file. No validation prevents empty or whitespace-only video IDs.

**Fix:** Add validation at the router level or in `_get_analysis_dir()`:

```python
def _get_analysis_dir(video_id: str) -> Path:
    if not video_id or not video_id.strip():
        raise ValueError("video_id cannot be empty")
    return ANALYSIS_DIR / video_id
```

### IN-04: Missing preventDefault on Timeline Mouse Events

**File:** `web/src/components/FrameTimeline.vue:59-66`
**Issue:** `handleMouseDown` and `handleMouseMove` do not call `event.preventDefault()`. During drag operations on the timeline, the browser may select text or trigger other default behaviors, creating a jarring user experience.

**Fix:**
```typescript
const handleMouseDown = (event: MouseEvent) => {
  event.preventDefault()
  isDragging.value = true
  handleTimelineClick(event)
}
```

---

_Reviewed: 2026-04-29_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
