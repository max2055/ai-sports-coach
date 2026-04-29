---
phase: 01-project-setup
reviewed: 2026-04-29T00:00:00Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - web/src/main.ts
  - web/src/types/upload.ts
  - web/src/components/VideoUploader.vue
  - web/src/components/AnalysisTypeSelector.vue
  - web/src/views/UploadView.vue
  - web/src/router/index.ts
  - web/src/App.vue
  - web/src/api/upload.ts
  - web/src/composables/useUpload.ts
  - web/.env.development
  - api/main.py
  - api/routers/upload.py
  - api/models/upload.py
  - api/services/video_service.py
findings:
  critical: 2
  warning: 4
  info: 5
  total: 11
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-04-29T00:00:00Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Reviewed 14 source files across the Vue 3 frontend and FastAPI backend for the AI Tennis Coach application. The codebase is well-structured with good use of TypeScript typing and Vue composition API patterns. Two critical security issues were identified: (1) missing file size limits on uploads enabling potential DoS, and (2) hardcoded CORS origins that include production-like localhost ports. Several warnings relate to unhandled edge cases and error swallowing. The overall architecture is sound but needs hardening for production use.

## Critical Issues

### CR-01: No file size limit on video uploads

**File:** `api/routers/upload.py:50`
**Issue:** The upload endpoint reads the entire file into memory with `await file.read()` without any size validation. An attacker or careless user could upload a multi-gigabyte file, exhausting server memory (OOM) or filling disk space. The `save_uploaded_video` function writes raw bytes to disk without quota checks.

**Fix:**
```python
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB

@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    analysis_type: AnalysisType = Form(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check Content-Length header if available
    if file.size and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {MAX_UPLOAD_SIZE // (1024*1024)} MB")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {MAX_UPLOAD_SIZE // (1024*1024)} MB")
    # ... rest of handler
```

Additionally, consider configuring a middleware or server-level limit (e.g., `--limit-max-size` in uvicorn) for defense in depth.

### CR-02: CORS allows wildcard methods and headers

**File:** `api/main.py:18-22`
**Issue:** `allow_methods=["*"]` and `allow_headers=["*"]` with `allow_credentials=True` is a dangerous combination. While the origins list is restricted to localhost, this pattern is easy to copy into production and creates a permissive security posture. With credentials enabled, wildcard methods/headers may allow unexpected cross-origin requests.

**Fix:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

Read origins from environment variables so production can be configured safely, and explicitly list allowed methods and headers.

## Warnings

### WR-01: `AnalysisTypeSelector` ignores `props` and uses uninitialized local state

**File:** `web/src/components/AnalysisTypeSelector.vue:16`
**Issue:** The component receives `modelValue` via props but creates a local `selectedType` ref that ignores the prop's actual value due to missing `props` destructure. Line 16 reads `props.modelValue` but `props` is never declared from `defineProps`. The `defineProps` return value is not assigned, so `props` is undefined in the script scope -- this will cause a runtime error.

**Fix:**
```typescript
const props = defineProps<{ modelValue: AnalysisType }>()
const selectedType = ref<AnalysisType>(props.modelValue || 'full')
```

Or use `withDefaults`:
```typescript
const props = withDefaults(defineProps<{ modelValue: AnalysisType }>(), {
  modelValue: 'full',
})
const selectedType = ref<AnalysisType>(props.modelValue)
```

### WR-02: Empty catch block silently swallows history load errors

**File:** `web/src/views/UploadView.vue:84`
**Issue:** The `catch` block in `loadRecent()` is empty with only `/* ignore */`. If the history API is down or returns an error, `recentEntries.value` remains an empty array and `recentLoading.value` is set to `false`, making it appear as if there are no records rather than indicating a loading failure.

**Fix:**
```typescript
async function loadRecent() {
  try {
    const data = await getHistory()
    recentEntries.value = data.entries.slice(0, 5)
  } catch (err) {
    console.warn('Failed to load recent history:', err)
  } finally {
    recentLoading.value = false
  }
}
```

### WR-03: Race condition between `uploadStatus` and `error` state in VideoUploader

**File:** `web/src/components/VideoUploader.vue:14,33`
**Issue:** Line 18 computes `hasError` from both `uploadStatus.value === 'error'` and `error.value`. However, line 33 calls `resetUpload()` which resets the composable's `error` ref to `null`, but `uploadStatus` is a separate local ref set to `'uploading'` on line 32. If the upload immediately fails, there is a brief window where `isUploading` and `hasError` could both be true, causing inconsistent UI state. More critically, `uploadStatus` is never reset back to `'idle'` on success or error -- it stays `'uploading'` or transitions to `'success'`/`'error'` but never resets when the user drops a new file.

**Fix:** Reset `uploadStatus` to `'idle'` before starting a new upload:
```typescript
async function handleFile(file: File) {
  if (!isValidVideo(file)) {
    // ...
  }
  uploadStatus.value = 'uploading'
  resetUpload()
  // uploadStatus stays 'uploading' here -- add idle reset in handleDrop for new files
```

A cleaner approach: reset `uploadStatus.value = 'idle'` before calling `resetUpload()`, then set to `'uploading'` after.

### WR-04: `extract_video_metadata` may return `0` for duration/width/height without raising error

**File:** `api/services/video_service.py:48-50`
**Issue:** When ffprobe succeeds but the stream metadata does not include duration, width, or height (common with certain video codecs or container formats), the `.get()` fallback returns `0`. This is treated as valid data and propagates to the API response as `duration: 0.0, width: 0, height: 0`. The caller has no way to distinguish "metadata missing" from "video is zero-length/zero-dimension."

**Fix:**
```python
duration = float(stream.get("duration", 0))
width = stream.get("width")
height = stream.get("height")

if not duration or not width or not height:
    raise RuntimeError("Incomplete video metadata: duration, width, or height missing")

return duration, int(width), int(height)
```

## Info

### IN-01: Redundant `Content-Type` header in axios upload request

**File:** `web/src/api/upload.ts:30`
**Issue:** Setting `'Content-Type': 'multipart/form-data'` manually causes axios to skip setting the proper boundary parameter. Axios should auto-detect `FormData` and set the correct `multipart/form-data; boundary=---...` header.

**Fix:** Remove the explicit `Content-Type` header and let axios set it automatically:
```typescript
const response = await axios.post<UploadResult>(`${API_BASE}/api/upload`, formData, {
  onUploadProgress: (progressEvent) => { ... }
})
```

### IN-02: `format` is a reserved word in Pydantic BaseModel

**File:** `api/models/upload.py:16`
**Issue:** Using `format` as a Pydantic field name works but shadows Python's built-in `str.format()` method on the model instance. This could cause confusion or issues if code tries to call `.format()` on a `VideoMetadata` instance.

**Fix:** Rename to `video_format` or `file_format`:
```python
class VideoMetadata(BaseModel):
    duration: float
    width: int
    height: int
    size: int
    file_format: str  # renamed from 'format'
```

### IN-03: `AnalysisTypeSelector` does not watch for prop changes

**File:** `web/src/components/AnalysisTypeSelector.vue:16`
**Issue:** The `selectedType` ref is initialized once from `props.modelValue` but never syncs if the parent updates the prop value externally (e.g., via the reset button in UploadView which changes `analysisType` to `'full'`). The component will still show the previously selected value.

**Fix:**
```typescript
import { ref, watch } from 'vue'
const props = defineProps<{ modelValue: AnalysisType }>()
const selectedType = ref<AnalysisType>(props.modelValue || 'full')

watch(() => props.modelValue, (newVal) => {
  selectedType.value = newVal
})
```

### IN-04: `UPLOAD_DIR` uses relative path that depends on working directory

**File:** `api/services/video_service.py:9`
**Issue:** `UPLOAD_DIR = Path("output/uploads")` is a relative path. If the server is started from a different working directory (e.g., via systemd, Docker, or process manager), the upload directory will be created in an unexpected location or fail to be created.

**Fix:**
```python
BASE_DIR = Path(__file__).resolve().parent.parent  # points to api/
UPLOAD_DIR = BASE_DIR / "output" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
```

### IN-05: Router has no fallback/404 route

**File:** `web/src/router/index.ts`
**Issue:** If a user navigates to an unknown path, Vue Router will render nothing (blank page) instead of a 404 page. This is a minor UX issue.

**Fix:**
```typescript
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ... existing routes
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../views/NotFound.vue') },
  ],
})
```

---

_Reviewed: 2026-04-29T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
