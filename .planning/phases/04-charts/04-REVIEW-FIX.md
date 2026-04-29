---
phase: 04-charts
fixed_at: 2026-04-29T00:00:00Z
review_path: .planning/phases/04-charts/04-REVIEW.md
iteration: 1
findings_in_scope: 11
fixed: 11
skipped: 0
status: all_fixed
---

# Phase 04: Code Review Fix Report

**Fixed at:** 2026-04-29T00:00:00Z
**Source review:** .planning/phases/04-charts/04-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 11
- Fixed: 11
- Skipped: 0

## Fixed Issues

### CR-01: Path traversal via unvalidated video_id

**Files modified:** `api/services/chart_service.py`
**Commit:** c7e2f6c
**Applied fix:** Added `_validate_video_id()` function with regex validation (`^[a-zA-Z0-9_\-]+$`) and path traversal check using `resolve().is_relative_to()`. Both `_get_frames_json_path()` and `_get_summary_json_path()` now validate `video_id` before path construction.

### CR-02: Floating-point exact equality comparison in tooltip formatter

**Files modified:** `web/src/components/ServeHeightChart.vue`
**Commit:** ac865ee
**Applied fix:** Replaced `===` with `Math.abs(p.time_seconds - timeVal) < 0.001` epsilon comparison for tooltip frame lookup.

### WR-01: Serve frame detection assumes sequential frame keys starting at 1

**Files modified:** `api/services/chart_service.py`
**Commit:** c7e2f6c
**Applied fix:** Sort all frame keys with `sorted(int(k) for k in frames.keys())` and use `set(sorted_frame_keys[:3])` to identify first 3 frames. Check `frame_number in serve_frame_numbers` instead of `frame_number <= 3`.

### WR-02: overall_score not clamped to 0-10 range

**Files modified:** `api/services/chart_service.py`
**Commit:** c7e2f6c
**Applied fix:** Changed `overall_score = summary_data.get("overall_score", 5)` to `overall_score = min(10, max(0, summary_data.get("overall_score", 5)))`.

### WR-03: HitPointHeatmap legend is non-functional

**Files modified:** `web/src/components/HitPointHeatmap.vue`
**Commit:** f934d77
**Applied fix:** Removed the `legend` config from the chart options since the series has no `name` property and the visual legend is already rendered in the template (lines 117-126).

### WR-04: RadarDimension value type mismatch

**Files modified:** `api/models/chart.py`
**Commit:** 4bc296b
**Applied fix:** Changed `RadarDimension.value` from `int` to `float` and `ConsistencyRadar.overall_score` from `int` to `float` to prevent silent truncation of float scores.

### WR-05: ConsistencyRadar dimension count hardcoded

**Files modified:** `web/src/components/ConsistencyRadar.vue`
**Commit:** 19cd157
**Applied fix:** Replaced hardcoded `[8, 8, 8, 8, 8, 8]` with `Array(props.dimensions.length).fill(8)` so the target standard adapts to the actual dimension count.

### WR-06: ConsistencyRadar overallScore default is 0 not undefined

**Files modified:** `web/src/components/ConsistencyRadar.vue`
**Commit:** 19cd157
**Applied fix:** Changed `overallScore?: number` to `overallScore: number` (required prop) and removed the unnecessary `v-if="overallScore !== undefined"` guard in the template.

### WR-07: IssueStatsChart tooltip formatter uses `any` without null check

**Files modified:** `web/src/components/IssueStatsChart.vue`
**Commit:** 72f5023
**Applied fix:** Added `if (!params || !params.length) return ''` guard before accessing `params[0]` in the tooltip formatter.

### WR-08: ServeHeightChart tooltip formatter uses `any` without null check

**Files modified:** `web/src/components/ServeHeightChart.vue`
**Commit:** ac865ee
**Applied fix:** Added `if (!params || !params.length) return ''` guard as the first line of the tooltip formatter.

### WR-09: No error handling in API calls - silent failure

**Files modified:** `web/src/api/charts.ts`
**Commit:** 11fbb0d
**Applied fix:** Wrapped all 4 API functions (`getServeHeightData`, `getHitPointData`, `getRadarData`, `getIssueStats`) with try/catch blocks. AxiosError is re-thrapped with contextual message including HTTP status and detail.

## Skipped Issues

None -- all findings were successfully fixed.

---

_Fixed: 2026-04-29T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
