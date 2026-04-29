---
phase: 01-project-setup
reviewed: 2026-04-29T01:00:00Z
findings_in_scope: 11
fixed: 8
skipped: 3
iteration: 1
status: partial
---

# Phase 01: Code Review Fix Report

**Date:** 2026-04-29
**Findings in scope:** 11 (Critical: 2, Warning: 4, Info: 5)
**Fixed:** 8 | **Skipped:** 3

## Fixed Issues

### CR-01: No file size limit on video uploads ✓
**File:** `api/routers/upload.py`
**Fix:** Added `MAX_UPLOAD_SIZE = 500 MB` constant. Check `file.size` header before reading, then verify `len(content)` after reading. Returns HTTP 413 if exceeded.

### CR-02: CORS wildcard methods + credentials ✓
**File:** `api/main.py`
**Fix:** Replaced `allow_methods=["*"]` and `allow_headers=["*"]` with explicit lists. Origins now read from `CORS_ORIGINS` environment variable with sensible defaults.

### WR-01: AnalysisTypeSelector props not captured ✓
**File:** `web/src/components/AnalysisTypeSelector.vue`
**Fix:** Assigned `defineProps` return value to `const props`. Added `watch` to sync `selectedType` when parent updates `modelValue` prop.

### WR-02: Empty catch block silently swallows errors ✓
**File:** `web/src/views/UploadView.vue`
**Fix:** Changed `catch { /* ignore */ }` to `catch (err) { console.warn('Failed to load recent history:', err) }`.

### WR-03: Race condition in VideoUploader ✓
**File:** `web/src/components/VideoUploader.vue`
**Fix:** Reset `uploadStatus.value = 'idle'` before `resetUpload()`, then set to `'uploading'` after. Ensures clean state for subsequent uploads.

### WR-04: Missing metadata defaults to 0 ✓
**File:** `api/services/video_service.py`
**Fix:** Changed from `.get()` with `0` default to strict None check. Raises `RuntimeError("Incomplete video metadata")` if duration, width, or height is missing.

### IN-01: Redundant Content-Type header ✓
**File:** `web/src/api/upload.ts`
**Fix:** Removed explicit `'Content-Type': 'multipart/form-data'` header. Axios auto-detects FormData and sets correct boundary.

### IN-02: `format` field shadows Python built-in ✓
**File:** `api/models/upload.py`, `api/routers/upload.py`
**Fix:** Renamed `format` to `file_format` in VideoMetadata model and updated router usage.

### IN-04: UPLOAD_DIR uses relative path ✓
**File:** `api/services/video_service.py`
**Fix:** Changed to `BASE_DIR = Path(__file__).resolve().parent.parent` then `UPLOAD_DIR = BASE_DIR / "output" / "uploads"`.

## Skipped Issues

### IN-03: AnalysisTypeSelector watches prop ✓
Already fixed as part of WR-01 fix (added watch).

### IN-05: No 404 fallback route
**Reason:** Requires creating a new NotFound.vue component. Minor UX issue — defer to later.

### Other services with relative paths
**Files:** `analysis_service.py`, `frame_service.py`, `chart_service.py`, `history_service.py`, `pro_service.py`, `report_service.py`
**Reason:** Not Phase 01 files — created in later phases. Fix should be applied to those phase reviews.

## Files Modified

| File | Changes |
|------|---------|
| `api/main.py` | CORS: explicit methods/headers, env-based origins |
| `api/routers/upload.py` | 500MB upload limit, file_format rename |
| `api/models/upload.py` | format → file_format |
| `api/services/video_service.py` | BASE_DIR pattern, strict metadata check |
| `web/src/api/upload.ts` | Remove redundant Content-Type header |
| `web/src/components/AnalysisTypeSelector.vue` | Capture props, add watch |
| `web/src/components/VideoUploader.vue` | Fix upload status race condition |
| `web/src/views/UploadView.vue` | Log history load errors |
