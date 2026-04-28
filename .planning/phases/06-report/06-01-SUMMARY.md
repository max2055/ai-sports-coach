---
phase: 06-report
plan: 01
status: complete
completed_at: "2026-04-28T18:00:00Z"
---

# Plan 06-01: Backend Report Parsing API - Execution Summary

## Objective

创建后端报告解析服务，从 coach_*.md 中提取结构化数据供前端报告页面使用。

## Completed Tasks

### Task 1: Create Report Data Models ✓

Created `api/models/report.py`:
- Strength, Issue, ImprovementSuggestion models
- IssueSummaryRow for frame-level issue table
- RadarScores (6 dimensions with defaults of 5)
- CoachReport (complete structured report)

### Task 2: Create Report Service ✓

Created `api/services/report_service.py`:
- `parse_coach_report(markdown_path)` - parses coach_*.md using regex:
  - Overall Score extraction
  - Strengths list with frame refs
  - Issues list with severity calculation
  - Improvement suggestions with numbering
  - Coach summary paragraph
- `extract_issue_summary(frames_json_path)` - extracts issue rows from frames.json
- `calculate_radar_scores(summary_path)` - reads scores from summary.json
- `generate_training_plan(issues, radar_scores)` - generates training recommendations based on issues
- `get_report_for_video(video_id)` - orchestrates all above, searches report/tennis/ and output/analysis/

### Task 3: Create Report Router ✓

Created `api/routers/report.py`:
- GET /api/report/{video_id} → CoachReport

Updated `api/main.py`:
- Added report router import and include_router

## Verification Results

- ✓ api/models/report.py has CoachReport, RadarScores
- ✓ api/services/report_service.py has parse_coach_report, get_report_for_video
- ✓ api/routers/report.py has get_report endpoint
- ✓ api/main.py includes report router

## Files Modified

| File | Action | Lines |
|------|--------|-------|
| api/models/report.py | Created | 50 |
| api/services/report_service.py | Created | 200 |
| api/routers/report.py | Created | 15 |
| api/main.py | Modified | +2 |

## Success Criteria

- ✓ 后端可以返回结构化报告数据
- ✓ 包含评分、亮点、问题、训练计划、教练总结
- ✓ API 返回 JSON 格式
