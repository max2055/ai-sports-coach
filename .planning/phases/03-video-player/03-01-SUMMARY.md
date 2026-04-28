---
phase: 03-video-player
plan: 01
subsystem: backend
tags: [api, frames, annotations, video-player]
duration: 15m
completed_date: "2026-04-28"
requires:
  - Phase 2 analysis output (frames.json)
provides:
  - Frame annotation API endpoints
  - Issue frame filtering
  - Annotated image serving
affects:
  - Frontend video player component
key_decisions:
  - Used Pydantic models matching tennis_annotate.py output format
  - Issue types defined as Literal for type safety
  - Frame time calculation assumes 30fps
---

# Phase 3 Plan 01: Backend Frame Data Service Summary

## One-Liner

Created backend API to serve frame annotation data from tennis_annotate.py output, with filtering by issue type.

## Completed Tasks

### Task 1: Create Frame Data Service

**Commit:** e4b034a

**Files created:**
- `api/models/frame.py` - Frame annotation Pydantic models
- `api/services/frame_service.py` - Frame data parsing service

**Key changes:**
- Defined `IssueType` as Literal with 21 issue types from tennis_annotate.py
- Created `BodyPartAnnotation`, `PlayerAnnotation`, `FrameAnnotation`, `IssueFrame` models
- Implemented `get_frame_annotations()` to parse frames.json output
- Implemented `get_issue_frames()` with optional issue_type filtering
- Implemented `get_annotated_image()` to serve annotated frame images

### Task 2: Create Frame Router

**Commit:** 80cca20

**Files created/modified:**
- `api/routers/frames.py` - FastAPI router with 4 endpoints
- `api/main.py` - Added frames router registration

**API Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/frames/{video_id}` | Get all frame annotations |
| GET | `/api/issues/{video_id}` | Get frames with issues (optional `?issue_type=` filter) |
| GET | `/api/annotated/{video_id}/{frame_number}` | Get annotated frame image |
| GET | `/api/frames/{video_id}/exists` | Check if frames exist |

### Additional: Export Frame Models

**Commit:** d843222

**Files modified:**
- `api/models/__init__.py` - Added frame model exports

## Verification

- [x] `api/models/frame.py` exists with FrameAnnotation and IssueFrame models
- [x] `api/services/frame_service.py` contains frames.json parsing logic
- [x] `api/routers/frames.py` contains three main endpoints
- [x] `main.py` includes frames router
- [x] All Python imports verified working

## Deviations from Plan

None - plan executed exactly as written.

## Technical Notes

### Frame Data Structure

The service parses `output/analysis/{video_id}/frames.json` with structure:
```json
{
  "frames": {
    "1": {
      "players": [{
        "body": {"x_pct": 0.5, "y_pct": 0.5, "radius_pct": 0.06, "issue_type": "", "issue_note": ""},
        "hand_l": {...},
        "hand_r": {...},
        "foot_l": {...},
        "foot_r": {...}
      }]
    }
  }
}
```

### Issue Types Supported

21 issue types from tennis_annotate.py:
- Swing/contact issues: LATE BACKSWING, WRONG GRIP, GRIP CHANGE ERR, WRONG CONTACT, ELBOW DROP, NO HIP ROT, LATE SHOULDER, NO FOLLOW-THRU
- Footwork issues: POOR FOOTWORK, NO SPLIT STEP, LATE WEIGHT, WRONG STANCE, WRONG POSITION
- Serve issues: BAD TOSS, NO LEG DRIVE
- General issues: OFF BALANCE, TELEGRAPH, WRONG SPIN
- Positive labels: GOOD FORM, GOOD FOOTWORK, GOOD TACTICS

### Frame Time Calculation

Frame timestamps are calculated assuming 30fps:
- Frame 1 = 0 seconds
- Frame 2 = 0.033 seconds
- etc.

## Next Steps

- Phase 3 Plan 02: Frontend video player component
- Phase 3 Plan 03: Canvas overlay for annotations