---
phase: 04-charts
reviewed: 2026-04-29T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - api/models/chart.py
  - api/routers/charts.py
  - api/services/chart_service.py
  - web/src/api/charts.ts
  - web/src/components/ConsistencyRadar.vue
  - web/src/components/HitPointHeatmap.vue
  - web/src/components/IssueStatsChart.vue
  - web/src/components/ServeHeightChart.vue
findings:
  critical: 2
  warning: 9
  info: 5
  total: 16
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-04-29T00:00:00Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed 8 files comprising the ECharts visualization phase for the AI Tennis Coach app. The backend chart service extracts metrics from frame annotation JSON files and serves them via FastAPI endpoints. The frontend provides 4 Vue components wrapping ECharts for serve height trends, hit point heatmaps, consistency radar, and issue statistics.

Key concerns: a path traversal vulnerability in the `video_id` parameter used for file path construction, an unreliable floating-point exact equality comparison in the ServeHeightChart tooltip formatter, a non-functional legend in HitPointHeatmap, and missing error handling in API calls that would leave components in a silent failure state. The serve frame detection logic in `chart_service.py` also has a subtle bug when frame keys are non-sequential.

## Critical Issues

### CR-01: Path traversal via unvalidated video_id

**File:** `api/services/chart_service.py:27-29`
**Issue:** The `video_id` parameter is used directly in path construction (`ANALYSIS_DIR / video_id / "frames.json"`) without any validation. A malicious `video_id` such as `../../../etc/passwd%00` could escape the intended directory and read arbitrary files. The FastAPI router at `api/routers/charts.py:21` also interpolates `video_id` into error detail messages without sanitization.

**Fix:** Add a validation function and validate `video_id` before use:
```python
import re

def _validate_video_id(video_id: str) -> str:
    """Validate video_id contains only safe characters."""
    if not re.match(r'^[a-zA-Z0-9_\-]+$', video_id):
        raise ValueError(f"Invalid video_id: {video_id}")
    return video_id

def _get_frames_json_path(video_id: str) -> Path:
    video_id = _validate_video_id(video_id)
    path = ANALYSIS_DIR / video_id / "frames.json"
    # Ensure resolved path stays within ANALYSIS_DIR
    resolved = path.resolve()
    if not resolved.is_relative_to(ANALYSIS_DIR.resolve()):
        raise ValueError(f"Path traversal detected: {video_id}")
    return resolved
```

### CR-02: Floating-point exact equality comparison in tooltip formatter

**File:** `web/src/components/ServeHeightChart.vue:33`
**Issue:** The tooltip formatter uses exact equality (`===`) to match `time_seconds` values:
```ts
const point = props.points.find(p => p.time_seconds === data.value[0])
```
Floating-point numbers derived from arithmetic (`(frame_number - 1) / 30.0`) will almost never match exactly due to IEEE 754 representation. The backend rounds to 4 decimal places, but the ECharts axis value may have further rounding. This means the fallback branch (line 37) is always taken, and the frame number is never shown in tooltips.

**Fix:** Use an epsilon-based comparison or match by index instead:
```ts
formatter: (params: any) => {
  if (!params || !params.length) return ''
  const data = params[0]
  const timeVal = data.value[0]
  const point = props.points.find(p => Math.abs(p.time_seconds - timeVal) < 0.001)
  if (point) {
    return `帧号: ${point.frame_number}<br/>时间: ${timeVal.toFixed(2)}s<br/>高度: ${(100 - data.value[1]).toFixed(1)}%`
  }
  return `时间: ${timeVal.toFixed(2)}s<br/>高度: ${(100 - data.value[1]).toFixed(1)}%`
}
```

## Warnings

### WR-01: Serve frame detection assumes sequential frame keys starting at 1

**File:** `api/services/chart_service.py:90-91`
**Issue:** The condition `if frame_number <= 3` assumes frame keys are sequential integers starting from 1. If the `frames.json` dictionary keys are non-sequential (e.g., `{"100": ..., "101": ..., "102": ...}`), only one frame would be captured as a "serve frame" instead of three. The comment says "first 3 frames" but the code checks absolute frame number, not position in sequence.

**Fix:** Track sorted frame keys and check position:
```python
sorted_frame_keys = sorted(int(k) for k in frames.keys())
serve_frame_numbers = set(sorted_frame_keys[:3])  # First 3 frames by number

# Then in the loop:
if frame_number in serve_frame_numbers:
    is_serve_frame = True
```
Or better: sort all frames first, then iterate by position rather than by key value.

### WR-02: overall_score not clamped to 0-10 range

**File:** `api/services/chart_service.py:222`
**Issue:** Individual dimension scores are clamped with `min(10, max(0, score))` on line 215, but `overall_score` (line 186, returned on line 222) is taken directly from the JSON without clamping. If `summary.json` contains a value outside 0-10, it will pass through to the frontend. The `ConsistencyRadar` model declares `overall_score: int` with no validation constraints.

**Fix:** Clamp overall_score before returning:
```python
overall_score = min(10, max(0, summary_data.get("overall_score", 5)))
```
Or add Pydantic validation:
```python
overall_score: int = Field(ge=0, le=10)
```

### WR-03: HitPointHeatmap legend is non-functional

**File:** `web/src/components/HitPointHeatmap.vue:85-89`
**Issue:** The chart config defines `legend: { data: ['正常', '问题'] }` but the scatter series has no `name` property. ECharts legend items only work when they match series names. Additionally, all points are in a single series with per-point colors, so the legend cannot toggle "normal" vs "problem" points independently. The legend in the template (lines 117-126) is purely visual and not connected to chart interactivity.

**Fix:** Either remove the legend config (keep only the template legend), or split into two series:
```ts
series: [
  { type: 'scatter', name: '正常', data: normalPoints, ... },
  { type: 'scatter', name: '问题', data: issuePoints, ... }
]
```

### WR-04: RadarDimension value type mismatch

**File:** `api/models/chart.py:41`, `api/services/chart_service.py:215`
**Issue:** `RadarDimension.value` is declared as `int`, but `score` from `summary_data.get("scores", {})` may be a float (JSON numbers are parsed as float by Python's `json.loads` when they have decimals). Pydantic v2 will coerce float to int by truncation, which silently loses precision. A score of `7.9` becomes `7`.

**Fix:** Change the model to accept float:
```python
class RadarDimension(BaseModel):
    name: str
    value: float  # 0-10 score
```
Or explicitly round in the service:
```python
value=round(min(10, max(0, score)))
```

### WR-05: ConsistencyRadar dimension count hardcoded

**File:** `web/src/components/ConsistencyRadar.vue:66`
**Issue:** The "target standard" data series hardcodes `[8, 8, 8, 8, 8, 8]` (6 values). If the backend ever returns a different number of dimensions, this array will be mismatched and the radar chart will render incorrectly. The dimension count is derived from `props.dimensions.length`, so the hardcoded array should use that:

**Fix:**
```ts
value: Array(props.dimensions.length).fill(8),
```

### WR-06: ConsistencyRadar overallScore default is 0 not undefined

**File:** `web/src/components/ConsistencyRadar.vue:8`, `web/src/components/ConsistencyRadar.vue:112`
**Issue:** The prop declares `overallScore?: number` (optional, so `undefined`), but if the parent component passes `0` (which is falsy but a valid score), the template condition `v-if="overallScore !== undefined"` would still render it. However, the real issue is that `overallScore` defaults to `undefined` in Vue props, so if the parent doesn't pass it at all, the score display is hidden. The parent (ReportView) likely always passes it, but this could confuse consumers.

**Fix:** Add a default value or use `null` sentinel:
```ts
const props = defineProps<{
  dimensions: RadarDimension[]
  overallScore: number  // required, always provided by parent
}>()
```

### WR-07: IssueStatsChart tooltip formatter uses `any` without null check

**File:** `web/src/components/IssueStatsChart.vue:49-52`
**Issue:** The tooltip formatter accepts `params: any` and immediately accesses `params[0]` without checking if `params` is a non-empty array. If ECharts calls the formatter with an empty array (e.g., on mouse leave), this will throw `TypeError: Cannot read properties of undefined`.

**Fix:**
```ts
formatter: (params: any) => {
  if (!params || !params.length) return ''
  const data = params[0]
  return `${data.name}<br/>次数: ${data.value}`
}
```

### WR-08: ServeHeightChart tooltip formatter uses `any` without null check

**File:** `web/src/components/ServeHeightChart.vue:31-38`
**Issue:** Same as WR-07. The tooltip formatter accesses `params[0]` without checking if `params` is populated. ECharts may call the formatter with empty params in certain edge cases.

**Fix:** Add null/length check as the first line:
```ts
if (!params || !params.length) return ''
```

### WR-09: No error handling in API calls - silent failure

**File:** `web/src/api/charts.ts:29-46`
**Issue:** All four API functions return `res.data` directly without any error handling. If the backend returns 404, 500, or a network error occurs, the calling component receives a rejected promise. None of the Vue components show loading states or error messages when data fails to load. Users will see empty charts with no indication of what went wrong.

**Fix:** At minimum, re-throw with context:
```ts
export async function getServeHeightData(videoId: string): Promise<{ points: ServeHeightPoint[] }> {
  try {
    const res = await axios.get(`${API_BASE}/api/charts/${videoId}/serve-height`)
    return res.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to load serve height data: ${error.response?.status} ${error.response?.data?.detail || error.message}`)
    }
    throw error
  }
}
```
Parent components should catch these errors and display user-friendly messages.

## Info

### IN-01: Dead code in radar dimension matching - English keywords unreachable

**File:** `api/services/chart_service.py:194-206`
**Issue:** The dimension matching loop checks `name.lower()` and `name[:2].lower()` (first two Chinese characters) before the English keyword fallbacks. Since all 6 predefined `dimension_names` are in Chinese, the Chinese character substring match will always succeed before English keywords are evaluated. The English keyword branches (`"technique"`, `"footwork"`, etc.) are dead code.

**Fix:** Simplify the matching logic to only check the keys in `scores` against the dimension names directly, or remove the English fallbacks if not needed.

### IN-02: Serve frame detection double-counts early frames with BAD TOSS

**File:** `api/services/chart_service.py:86-91`
**Issue:** If an early frame (frame_number <= 3) also has `issue_type == "BAD TOSS"`, the `is_serve_frame` flag is set twice. This is logically harmless (boolean stays True) but indicates the conditions overlap and the code structure is confusing. The `break` on line 103 means only the first player with a serve-related body part is captured per frame.

**Fix:** Restructure with clearer logic:
```python
is_serve_frame = (issue_type == "BAD TOSS") or (frame_number in first_three_frames)
```

### IN-03: TypeScript `any` usage in tooltip formatters

**File:** `web/src/components/ServeHeightChart.vue:31`, `web/src/components/HitPointHeatmap.vue:46`, `web/src/components/IssueStatsChart.vue:49`
**Issue:** All three chart components use `params: any` in their ECharts tooltip formatters. ECharts provides typed callback parameters; using `any` forfeits type checking. If the ECharts types are available, use the proper type.

**Fix:** Use the ECharts callback type or define a local interface:
```ts
interface TooltipParams {
  data: { value: number[]; name?: string; frame?: number; issue?: string }
  dataIndex: number
}
formatter: (params: TooltipParams[]) => { ... }
```

### IN-04: Issue severity classification thresholds are low

**File:** `api/services/chart_service.py:266-269`
**Issue:** The severity classification uses `count > 3` for "high" and `count >= 2` for "medium". In a video with many frames, an issue appearing only 4 times is classified as "high" severity. This may be intentional for the use case (even rare issues are important to fix), but the thresholds seem low and may not scale well with longer videos.

**Fix:** Consider making thresholds relative to total frames or configurable:
```python
ratio = count / max(total_frames, 1)
if ratio > 0.1:
    severity = "high"
elif ratio > 0.05:
    severity = "medium"
```

### IN-05: Missing `video_id` path parameter documentation in router

**File:** `api/routers/charts.py:21,40,58,76`
**Issue:** All four endpoints use `{video_id}` as a path parameter but do not specify a type constraint or description. FastAPI will accept any string, including empty strings or strings with path separator characters. A `Path` constraint with regex validation would improve API documentation and provide early validation.

**Fix:**
```python
from fastapi import Path as PathParam

@router.get("/charts/{video_id}/serve-height", response_model=ServeHeightData)
async def serve_height_chart(
    video_id: str = PathParam(..., min_length=1, max_length=128, pattern="^[a-zA-Z0-9_\-]+$")
) -> ServeHeightData:
```

---

_Reviewed: 2026-04-29T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
