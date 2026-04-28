---
phase: 04-charts
plan: 01
subsystem: backend
tags: [api, charts, echarts, visualization]
requires: [analysis-output]
provides: [chart-data-api]
affects: [frontend-charts]
tech-stack:
  added: [pydantic-models, fastapi-router]
  patterns: [service-layer, rest-api]
key-files:
  created:
    - api/models/chart.py
    - api/services/chart_service.py
    - api/routers/charts.py
  modified:
    - api/main.py
decisions:
  - Serve frames identified by BAD TOSS issue or first 3 frames
  - Frame time assumes 30fps
  - Issue severity: high (>3), medium (2-3), low (1)
metrics:
  duration_minutes: 10
  completed: "2026-04-28"
---

# Phase 4 Plan 01: Backend Chart Data API Summary

**Status:** Complete
**One-liner:** Four chart data extraction APIs serving ECharts-formatted JSON from analysis results.

## What Was Built

### Chart Data Models (`api/models/chart.py`)
- `ServeHeightData` - Time series of body.y_pct for serve frames
- `HitPointHeatmap` - Scatter plot positions with issue markers
- `ConsistencyRadar` - 6-dimension radar chart with overall score
- `IssueStatistics` - Issue counts with severity classification

### Chart Service (`api/services/chart_service.py`)
- `get_serve_height_data()` - Extracts body position for serve motion
- `get_hit_point_heatmap()` - Extracts hand_l racket positions
- `get_consistency_radar()` - Maps summary scores to 6 dimensions
- `get_issue_statistics()` - Counts issue_type occurrences

### Chart Router (`api/routers/charts.py`)
- `GET /api/charts/{video_id}/serve-height`
- `GET /api/charts/{video_id}/hit-points`
- `GET /api/charts/{video_id}/radar`
- `GET /api/charts/{video_id}/issues`

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Commit | Message |
|--------|---------|
| f9ccb32 | feat(04-01): add chart data models for ECharts visualization |
| ca73256 | feat(04-01): add chart data extraction service |
| d895408 | feat(04-01): add chart API endpoints and register router |

## Requirements Satisfied

- CHART-01: Serve height line chart data
- CHART-02: Hit point scatter/heatmap data
- CHART-03: 6-dimension consistency radar data
- CHART-04: Issue statistics bar chart data