---
phase: 02-analysis-pipeline
reviewed: 2026-04-29T12:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - api/main.py
  - api/models/__init__.py
  - api/models/analysis.py
  - api/routers/analysis.py
  - api/services/analysis_service.py
  - web/src/api/analysis.ts
  - web/src/composables/useAnalysis.ts
  - web/src/views/AnalysisView.vue
  - web/src/views/ReportView.vue
  - web/src/router/index.ts
findings:
  critical: 3
  warning: 6
  info: 5
  total: 14
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-04-29T12:00:00Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

This review covers the analysis pipeline implementation for the AI Tennis Coach app, including backend endpoints for video analysis (frame extraction, AI scoring, report generation), frontend pages for viewing analysis progress and results, and the integration layer between them. Three critical issues were identified that would prevent the analysis pipeline from functioning at all (missing module imports, unimported type), plus several warnings around data extraction logic, error handling gaps, and UX concerns.

## Critical Issues

### CR-01: Missing module imports will cause ImportError at runtime

**File:** `api/services/analysis_service.py:155, 168, 176-177, 195`

**Issue:** The `run_analysis` function dynamically imports from `src.video`, `src.analyzer`, `src.report`, `src.search` (lines 155, 168, 176-177), but the `api/src/` directory does not exist on disk. Only `tennis_annotate.py` exists at the project root level (line 195). When the analysis pipeline runs, it will immediately crash with `ModuleNotFoundError` on the first frame extraction step.

**Fix:** Either create the missing `api/src/` modules (`video.py`, `analyzer.py`, `report.py`, `search.py`) or import from the correct location. If these are planned but not yet implemented, the analysis_service.py should be stubbed or removed from main.py's router imports until the dependencies exist.

```python
# Current (broken):
from src.video import extract_frames, FrameExtractionError
from src.analyzer import analyze_frames, AnalyzerError
from src.report import generate_report
from src.search import fetch_reference_images

# Fix: Ensure these modules exist at api/src/ or correct the import paths
# For example, if they are at the project root:
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.video import extract_frames, FrameExtractionError
```

### CR-02: Missing `Literal` import causes NameError

**File:** `api/services/chart_service.py:264`

**Issue:** `Literal` is used in a type annotation on line 264 but is never imported. This will cause a `NameError` when `get_issue_statistics()` is called.

**Fix:**
```python
# Add to imports at top of file:
from typing import Literal

# Current imports:
import json
import logging
from pathlib import Path
# Should become:
import json
import logging
from pathlib import Path
from typing import Literal
```

### CR-03: `extract_issue_summary` reads wrong field -- returns empty results

**File:** `api/services/report_service.py:155-157`

**Issue:** The `extract_issue_summary` function looks for `player.get("issue_type", "")` directly on the player object. But the data structure from `frames.json` nests `issue_type` inside each body part (`player.body`, `player.hand_l`, etc.), not on the player object itself. The player object has `body`, `hand_l`, `hand_r`, `foot_l`, `foot_r` fields (see `frame_service.py:132-135` for the correct traversal pattern). This function will always return an empty list.

**Fix:** Iterate through body parts like `get_issue_frames` does in `frame_service.py`:

```python
# Current (broken):
for player in frame_data.get("players", []):
    issue_type = player.get("issue_type", "")
    if issue_type and not issue_type.startswith("GOOD"):
        ...

# Fix:
for player in frame_data.get("players", []):
    for body_part in ["body", "hand_l", "hand_r", "foot_l", "foot_r"]:
        part_data = player.get(body_part, {})
        issue_type = part_data.get("issue_type", "")
        if issue_type and not issue_type.startswith("GOOD"):
            ...
```

## Warnings

### WR-01: Unhandled JSON parse error in `extract_issue_summary`

**File:** `api/services/report_service.py:146-147`

**Issue:** `extract_issue_summary` uses bare `open()` + `json.load()` without catching `json.JSONDecodeError`. If `frames.json` is corrupted, a 500 error will leak back to the client. Compare with `frame_service.py` which properly catches and wraps this as a `ValueError`.

**Fix:**
```python
def extract_issue_summary(frames_json_path: Path) -> list[IssueSummaryRow]:
    if not frames_json_path.exists():
        return []
    try:
        with open(frames_json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid frames.json: {e}")
        return []
    # ... rest of function
```

### WR-02: `analysis_type` not validated or passed through retry

**File:** `api/routers/analysis.py:20, 121` and `web/src/composables/useAnalysis.ts:91`

**Issue:** The `analysis_type` parameter defaults to `"full"` in the `start_video_analysis` and `retry_analysis` endpoints but is never validated against the `AnalysisType` enum (`"forehand"`, `"backhand"`, `"serve"`, `"volley"`, `"full"`). Additionally, the frontend `retry()` function in `useAnalysis.ts` does not pass `analysis_type` to the API, so retries always default to `"full"` regardless of the original request.

**Fix:**
```python
# Backend -- validate analysis_type:
from models.upload import AnalysisType
analysis_type: AnalysisType = "full",

# Frontend -- accept and pass analysis_type:
async function retry(analysisType?: string) {
    const result = await retryAnalysis(videoId, analysisType)
    ...
}
```

### WR-03: `status` assignment is not type-safe after API call

**File:** `web/src/composables/useAnalysis.ts:66, 92`

**Issue:** Both `start()` and `retry()` cast `result.status as AnalysisStatus`, but the API returns `AnalysisResponse.status` which is typed as `AnalysisStatus` (a union literal). However, the `startAnalysis` and `retryAnalysis` functions in `api/analysis.ts` return `{ video_id: string; status: string }` (a plain string, not the union literal). The `as AnalysisStatus` cast masks potential type mismatches if the backend returns an unexpected status value.

**Fix:** Tighten the API client return types to match `AnalysisState.status`:
```typescript
// In api/analysis.ts:
export async function startAnalysis(videoId: string): Promise<{
  video_id: string
  status: 'pending' | 'extracting' | 'analyzing' | 'annotating' | 'completed' | 'failed'
}> {
```

### WR-04: Auto-redirect watch fires on every `isCompleted` change

**File:** `web/src/views/AnalysisView.vue:15`

**Issue:** The `watch(isCompleted, ...)` will fire every time `isCompleted` changes value, including on initial mount when it transitions from `undefined` to `false`. While the `setTimeout` delay means the user likely won't notice, the watcher should use `{ once: true }` or check the value to prevent unnecessary side effects.

**Fix:**
```typescript
watch(isCompleted, (completed) => {
  if (completed) {
    setTimeout(() => router.push(`/report/${videoId}`), 1000)
  }
})
```

### WR-05: No error handling if `getAnalysisStatus` returns 404 immediately

**File:** `web/src/composables/useAnalysis.ts:70-73`

**Issue:** After `startAnalysis` succeeds, polling begins immediately with `setInterval`. If the status endpoint returns 404 (e.g., the status file hasn't been written yet because the background task is slow), the catch block clears polling but the user sees a "failed" state even though the analysis might just be starting.

**Fix:** Add a retry mechanism for the first few polling attempts, or delay the first poll by 1 second:
```typescript
// Delay first poll to give background task time to initialize
pollInterval = setInterval(pollStatus, 2000)
setTimeout(async () => await pollStatus(), 1000)
```

### WR-06: `datetime.utcnow()` is deprecated in Python 3.12+

**File:** `api/services/analysis_service.py:105, 120`

**Issue:** `datetime.utcnow()` is deprecated as of Python 3.12 and will be removed in a future version. It also produces naive datetime objects that don't carry timezone information.

**Fix:**
```python
from datetime import datetime, timezone

# Replace datetime.utcnow() with:
datetime.now(timezone.utc)
```

## Info

### IN-01: `start_analysis` function in service layer is unused

**File:** `api/services/analysis_service.py:264-289`

**Issue:** The `start_analysis` function duplicates validation logic from the router (`_find_video_path` check, existing running analysis check) and is never called by `api/routers/analysis.py`. The router directly calls `run_analysis` via `BackgroundTasks.add_task`. Either use `start_analysis` for the initial pending state before adding the background task, or remove it.

### IN-02: `run_analysis_async` wrapper is defined but never used

**File:** `api/services/analysis_service.py:251-261`

**Issue:** An async wrapper around `run_analysis` exists but the router uses `BackgroundTasks.add_task(run_analysis, ...)` directly. The async wrapper would be useful if using `asyncio.create_task` instead of `BackgroundTasks`, but is currently dead code.

### IN-03: `getAnalysisStatus` endpoint should be called once before starting polling

**File:** `web/src/composables/useAnalysis.ts:60-73`

**Issue:** The `start()` function calls `startAnalysis`, then starts polling. But if the user refreshes the page while analysis is running, `startAnalysis` will return a 409 Conflict (already running) and the composable will treat this as a failure. The `start()` function should first check the current status via `getAnalysisStatus` and only call `startAnalysis` if no analysis exists.

### IN-04: Hardcoded polling interval of 2 seconds

**File:** `web/src/composables/useAnalysis.ts:70, 96`

**Issue:** Both `start()` and `retry()` poll at a fixed 2-second interval. For a pipeline that takes 1-3 minutes, this results in 30-90 unnecessary API calls. Consider using exponential backoff (e.g., start at 2s, increase to 5s, then 10s).

### IN-05: `models/__init__.py` re-exports `IssueType` that is not used by analysis pipeline

**File:** `api/models/__init__.py:5`

**Issue:** The `__init__.py` imports and re-exports `IssueType` from `models.frame`, but this export is never used in any router or service. Minor cleanup -- removing it from `__all__` would reduce the import surface.

---

_Reviewed: 2026-04-29T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
