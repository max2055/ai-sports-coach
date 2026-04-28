---
phase: 03-video-player
plan: 02
subsystem: frontend-video-player
tags: [vue, canvas, video-player, annotations, timeline]
dependencies:
  requires: [03-01]
  provides: [PLAY-01, PLAY-02, PLAY-03, PLAY-04, PLAY-05, FRAME-02, FRAME-04]
  affects: [ReportView]
tech-stack:
  added: [Canvas API, HTML5 Video, Vue Composition API]
  patterns: [Video-Canvas overlay, Event-driven sync, Component composition]
key-files:
  created:
    - web/src/api/frames.ts
    - web/src/components/AnnotatedVideoPlayer.vue
    - web/src/components/FrameTimeline.vue
    - web/src/components/IssueFrameList.vue
  modified:
    - web/src/views/ReportView.vue
decisions:
  - Canvas overlay positioned over video element for real-time annotation rendering
  - Color coding matches tennis_annotate.py (blue=body, green=hand, orange=foot)
  - Issue types translated to Chinese labels for user-friendly display
  - FPS defaults to 30 if not provided by backend
metrics:
  duration: "15 min"
  tasks_completed: 4
  files_created: 4
  files_modified: 1
  commits: 4
---

# Phase 3 Plan 02: Frontend Video Player Components Summary

**One-liner:** Vue video player with Canvas annotation overlay, custom timeline with issue markers, and filterable issue frame list with thumbnail navigation.

## Tasks Completed

| Task | Description | Commit | Status |
|------|-------------|--------|--------|
| 1 | Create Frame API Client | 0a4ecb3 | Done |
| 2 | Create AnnotatedVideoPlayer | af68f28 | Done |
| 3 | Create Timeline and Frame List | 0b76e41 | Done |
| 4 | Integrate into ReportView | f96e2ea | Done |

## Implementation Details

### Frame API Client (web/src/api/frames.ts)
- TypeScript interfaces matching backend models
- `getFrameAnnotations(videoId)` - fetch frame annotations
- `getIssueFrames(videoId, issueType?)` - fetch issue frames with optional filter
- `getAnnotatedImageUrl(videoId, frameNumber)` - URL for annotated frame images
- `getVideoUrl(videoId)` - URL for original video file

### AnnotatedVideoPlayer Component
- HTML5 video element with Canvas overlay for annotations
- Body parts drawn as color-coded circles (blue=body, green=hand, orange=foot)
- Issue rings (red) drawn around problematic body parts with labels
- Annotation visibility toggle button
- Syncs with video timeupdate events for real-time annotation display
- Exposes `seek()` and `seekToFrame()` methods for parent control

### FrameTimeline Component
- Custom progress bar with issue frame markers
- Red markers for problem frames, green for correct actions
- Click/drag to seek video
- Legend explaining marker colors

### IssueFrameList Component
- Thumbnail grid of issue frames with annotated images
- Issue type dropdown filter (Chinese labels)
- Click thumbnail to seek video to that frame
- Shows frame number, time, and issue tags

### ReportView Integration
- Layout: video player + timeline (left 2/3), frame list (right 1/3)
- Stats summary: annotated frames, issues, correct actions, duration
- Loading spinner and error state with Chinese messages
- Responsive design with sticky frame list sidebar

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- [x] web/src/api/frames.ts exists with correct API functions
- [x] AnnotatedVideoPlayer.vue contains Canvas overlay logic and timeupdate sync
- [x] FrameTimeline.vue shows issue frame markers with click-to-seek
- [x] IssueFrameList.vue shows thumbnails with filter dropdown
- [x] ReportView.vue integrates all components

## Self-Check: PASSED

All files created, all commits verified in git log.

---
*Completed: 2026-04-28*