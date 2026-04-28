---
phase: 02-analysis-pipeline
plan: 01
subsystem: api
tags: [fastapi, background-tasks, async, analysis-service]
requires: []
provides: [async-analysis-api, status-tracking]
affects: [api/main.py, api/routers, api/services]
key-files:
  created:
    - api/models/analysis.py
    - api/services/analysis_service.py
    - api/routers/analysis.py
  modified:
    - api/models/__init__.py
    - api/main.py
decisions:
  - Use FastAPI BackgroundTasks for async execution (simple, no extra dependencies)
  - Store status in JSON file output/analysis/{video_id}/status.json
  - Wrap existing coach.py and tennis_annotate.py logic directly
  - Import from src/video.py, src/analyzer.py, src/report.py instead of CLI
metrics:
  duration_minutes: 15
  completed_date: 2026-04-28
  task_count: 2
  file_count: 5
---

# Phase 2 Plan 01: Backend Analysis Service Summary

## One-Liner

Created async analysis service using FastAPI BackgroundTasks to wrap coach.py and tennis_annotate.py for on-demand video analysis with status tracking.

## Tasks Completed

| Task | Name | Commit | Status |
|------|------|--------|--------|
| 1 | Create Analysis Service | b93b31f | Done |
| 2 | Create Analysis Router | feb0407 | Done |

## Key Files Created

- **api/models/analysis.py** (25 lines): Pydantic models for analysis status tracking
  - `AnalysisStatus`: Literal type for status values (pending, extracting, analyzing, annotating, completed, failed)
  - `AnalysisState`: Full state model with video_id, status, progress, error, timestamps, paths
  - `AnalysisResponse`: API response model

- **api/services/analysis_service.py** (200+ lines): Core analysis service
  - `run_analysis()`: Synchronous wrapper for coach.py and tennis_annotate.py
  - `run_analysis_async()`: Async wrapper for BackgroundTasks
  - `get_analysis_status()`: Read status from JSON file
  - `start_analysis()`: Validate and initialize analysis
  - `_find_video_path()`: Locate uploaded video by video_id

- **api/routers/analysis.py** (95 lines): FastAPI router with 3 endpoints
  - `POST /api/analyze/{video_id}`: Start async analysis
  - `GET /api/status/{video_id}`: Query current status
  - `POST /api/retry/{video_id}`: Retry failed analysis

## Architecture

The analysis service follows this flow:
1. Frontend calls `POST /api/analyze/{video_id}` with analysis_type
2. Router validates video exists, adds `run_analysis` to BackgroundTasks
3. Background task executes:
   - Extract frames from video (src/video.py)
   - Analyze with GPT-4o Vision (src/analyzer.py)
   - Generate coach report (src/report.py)
   - Annotate frames with body parts/arrows (tennis_annotate.py)
   - Generate tennis report
4. Status updates written to `output/analysis/{video_id}/status.json`
5. Frontend polls `GET /api/status/{video_id}` for progress

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

All imports verified successful:
- Models: AnalysisState, AnalysisResponse, AnalysisStatus
- Service: run_analysis, get_analysis_status, start_analysis
- Router endpoints: `/analyze/{video_id}`, `/status/{video_id}`, `/retry/{video_id}`

## Self-Check: PASSED

- [x] api/services/analysis_service.py exists with run_analysis function
- [x] api/routers/analysis.py exists with start_analysis and get_status endpoints
- [x] api/main.py includes analysis router
- [x] Commit b93b31f: feat(02-01): create analysis service models and async runner
- [x] Commit feb0407: feat(02-01): create analysis API router endpoints