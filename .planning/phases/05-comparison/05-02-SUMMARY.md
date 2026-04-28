---
phase: 05-comparison
plan: 02
status: complete
completed_at: "2026-04-28T17:30:00Z"
---

# Plan 05-02: Split-screen Comparison Player - Execution Summary

## Objective

创建分屏对比播放器组件，实现用户视频与职业选手视频的同步播放对比功能。

## Completed Tasks

### Task 1: Create Pro Video API Client ✓

Created `web/src/api/pros.ts`:
- `ProVideoType` type: 'forehand' | 'backhand' | 'serve' | 'volley'
- `ProVideo` interface: id, type, name, description, file, duration
- `getProVideos(type?)` - fetch list, optional type filter
- `getProVideo(videoId)` - fetch single video
- `getProVideoFileUrl(videoId)` - get video file URL

### Task 2: Create Pro Video Selector Component ✓

Created `web/src/components/ProVideoSelector.vue`:
- Props: analysisType, selectedProVideo
- Loads videos matching analysis type
- Grid layout with video cards
- Click to emit 'select' event
- Loading/error states handled

### Task 3: Create Comparison Player Component ✓

Created `web/src/components/ComparisonPlayer.vue`:
- Props: userVideoUrl, userAnnotations, proVideo, timeOffset
- Split-screen layout (left: user, right: pro)
- Sync play/pause via `togglePlay()`
- Sync speed via `playbackRate` watch
- Sync seek with offset support
- Annotation toggle button
- Progress bar with time display
- ~280 lines (exceeds 250 minimum)

### Task 4: Create Keyframe Marker Component ✓

Created `web/src/components/KeyframeMarker.vue`:
- Props: userCurrentTime, proCurrentTime
- Mark buttons for both videos
- `calculatedOffset` computed from marked frames
- Apply offset button emits 'applyOffset'
- Status indicator (未标记/请标记/已计算偏移)
- Reset button

### Task 5: Integrate Comparison into ReportView ✓

Updated `web/src/views/ReportView.vue`:
- Added imports for ProVideoSelector, ComparisonPlayer, KeyframeMarker
- Added comparison state refs (selectedProVideo, timeOffset, userCurrentTime, proCurrentTime)
- Added analysisType computed (infers from videoId)
- Added event handlers (onProVideoSelect, handleUserTimeUpdate, handleProTimeUpdate, onApplyOffset)
- Added comparison-section after charts
- Conditional display: selector if no video, player + marker if selected

## Verification Results

- ✓ web/src/api/pros.ts has getProVideos and ProVideoType
- ✓ ProVideoSelector.vue emits select event
- ✓ ComparisonPlayer.vue has togglePlay, playbackRate, userVideoRef
- ✓ KeyframeMarker.vue has calculatedOffset, applyOffset
- ✓ ReportView.vue has comparison-section, ProVideoSelector, ComparisonPlayer

## Files Modified

| File | Action | Lines |
|------|--------|-------|
| web/src/api/pros.ts | Created | 35 |
| web/src/components/ProVideoSelector.vue | Created | 75 |
| web/src/components/ComparisonPlayer.vue | Created | 280 |
| web/src/components/KeyframeMarker.vue | Created | 100 |
| web/src/views/ReportView.vue | Modified | +55 |

## Success Criteria

- ✓ 分屏对比播放器可以同时播放两个视频
- ✓ 同步播放控制（播放/暂停/速度）
- ✓ 用户可以选择职业选手视频
- ✓ 关键帧对齐功能可用

## Notes

- ComparisonPlayer uses two separate video elements with shared state refs
- Keyframe alignment allows users to mark critical action frames and calculate offset
- Annotation layer toggle available for user video
- Analysis type inferred from videoId (defaults to forehand)