# AI Sports Coach Analyzer — Design Spec

**Date:** 2026-03-17
**Status:** Approved

---

## Overview

A CLI tool that accepts a local sports video and a background description, calls OpenAI GPT-4o Vision API to produce professional coach-level analysis, and saves the result as a Markdown report with extracted key frames and standard reference images.

---

## Architecture

```
ai-sports-coach/
├── coach.py              # CLI entry point
├── src/
│   ├── video.py          # Frame extraction via ffmpeg
│   ├── analyzer.py       # GPT-4o Vision API call + structured analysis
│   ├── search.py         # DuckDuckGo image search for reference images
│   └── report.py         # Markdown report assembly
├── output/               # Generated reports and images (gitignored)
├── requirements.txt
├── .env                  # Local secrets (gitignored)
├── .env.example          # Template committed to git
└── .gitignore            # Excludes .env and output/
```

---

## Components

### `coach.py` — CLI Entry Point

- Accepts `--video <path>` (required), `--context <string>` (optional), `--context-file <path>` (optional)
- If neither `--context` nor `--context-file` is provided, prompts user interactively
- Orchestrates the pipeline: video → frames → analysis → search → report
- Exits with clear error messages on misconfiguration

### `src/video.py` — Frame Extraction

- Uses `ffmpeg` (via `subprocess`) to uniformly sample **12 frames** from the video
- Saves frames as JPG to a temporary directory
- Raises a descriptive error if `ffmpeg` is not installed or the file does not exist

### `src/analyzer.py` — GPT-4o Vision Analysis

- Encodes each frame as base64
- Builds a structured prompt including:
  - Background description (athlete level, sport type, goals)
  - All 12 frame images
  - Instruction to respond as a professional coach with JSON output
- Expected JSON response fields:
  - `sport`: detected sport type (used for reference image search)
  - `score`: overall technique score (0–10)
  - `strengths`: list of observed positives
  - `issues`: list of technique problems with frame references
  - `suggestions`: prioritized improvement recommendations
  - `summary`: narrative paragraph for the report
- Uses `OPENAI_API_KEY` from environment

### `src/search.py` — Reference Image Search

- Searches DuckDuckGo Images using the `duckduckgo-search` library
- Query: `"{sport} standard technique professional"` (sport from analyzer output)
- Downloads 2–3 reference images to the output directory
- Degrades gracefully: if search or download fails, logs a warning and returns an empty list (report skips reference section)

### `src/report.py` — Markdown Report Assembly

Report structure:

```markdown
# Coach Analysis: {sport} — {date}

## Background
{background description}

## Key Frames
![Frame 1](frames/frame_001.jpg) ... (12 frames in grid)

## Analysis

### Overall Score: {score}/10

### Strengths
- ...

### Issues Found
- ...

### Improvement Suggestions
1. ...

### Coach Summary
{narrative paragraph}

## Standard Reference
![Reference 1](references/ref_001.jpg)
![Reference 2](references/ref_002.jpg)
```

- Saves report to `output/report_{timestamp}.md`
- Frame images and reference images are saved relative to the report

---

## Data Flow

```
coach.py
  → video.py       → output/frames/frame_001..012.jpg
  → analyzer.py    → structured JSON (sport, score, issues, suggestions)
  → search.py      → output/references/ref_001..003.jpg
  → report.py      → output/report_{timestamp}.md
```

---

## Configuration

`.env.example`:
```
OPENAI_API_KEY=sk-...
```

---

## Error Handling

| Scenario | Behavior |
|---|---|
| Video file not found | Exit with clear path error |
| `ffmpeg` not installed | Exit with installation instructions |
| `OPENAI_API_KEY` missing | Exit with `.env` configuration hint |
| API call fails | Exit with API error details |
| Image search fails | Log warning, skip reference section in report |
| Reference image download fails | Skip that image, continue with rest |

---

## Dependencies

- `openai` — GPT-4o API client
- `duckduckgo-search` — reference image search
- `requests` — image download
- `python-dotenv` — `.env` loading
- `ffmpeg` — system dependency for frame extraction

---

## Out of Scope

- Web UI or server mode
- Support for video URLs (local files only)
- Real-time analysis or streaming output
- Local ML models for motion detection
