# AI Sports Coach Analyzer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool that takes a local sports video + background description, calls GPT-4o Vision, and outputs a professional coach analysis as a Markdown report with key frames and reference images.

**Architecture:** Single-script CLI (`coach.py`) orchestrates four focused modules: frame extraction via ffmpeg, GPT-4o Vision analysis, DuckDuckGo reference image search, and Markdown report assembly. Each module is independently testable with clear inputs/outputs.

**Tech Stack:** Python 3.10+, `openai`, `duckduckgo-search`, `requests`, `python-dotenv`, `ffmpeg` + `ffprobe` (system — both bundled in the ffmpeg package)

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `requirements.txt` | Create | Pin all Python dependencies |
| `.env.example` | Create | Document required env vars |
| `.gitignore` | Create | Exclude `.env`, `output/` |
| `src/__init__.py` | Create | Make src a package |
| `src/video.py` | Create | Extract 12 frames from video via ffmpeg |
| `src/analyzer.py` | Create | Call GPT-4o Vision, return structured JSON |
| `src/search.py` | Create | Search and download reference images |
| `src/report.py` | Create | Assemble and save Markdown report |
| `coach.py` | Create | CLI entry point, orchestrate pipeline |
| `tests/test_video.py` | Create | Unit tests for frame extraction |
| `tests/test_analyzer.py` | Create | Unit tests for analyzer (mocked API) |
| `tests/test_search.py` | Create | Unit tests for search (mocked HTTP) |
| `tests/test_report.py` | Create | Unit tests for report assembly |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `requirements.txt`**

```
openai>=1.30.0
duckduckgo-search>=6.1.0
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-mock>=3.12.0
```

- [ ] **Step 2: Create `.env.example`**

```
OPENAI_API_KEY=sk-...
```

- [ ] **Step 3: Create `.gitignore`**

```
.env
output/
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 4: Create empty `src/__init__.py` and `tests/__init__.py`**

Both files are empty — they just mark the directories as Python packages.

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install without errors.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example .gitignore src/__init__.py tests/__init__.py
git commit -m "chore: project scaffolding and dependencies"
```

---

## Task 2: Frame Extraction (`src/video.py`)

**Files:**
- Create: `src/video.py`
- Create: `tests/test_video.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_video.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.video import extract_frames, FrameExtractionError


def test_raises_if_video_not_found(tmp_path):
    with pytest.raises(FrameExtractionError, match="not found"):
        extract_frames(Path("/nonexistent/video.mp4"), tmp_path)


def test_raises_if_ffmpeg_not_installed(tmp_path, mocker):
    mocker.patch("shutil.which", return_value=None)
    with pytest.raises(FrameExtractionError, match="ffmpeg"):
        extract_frames(Path("video.mp4"), tmp_path)


def test_returns_12_frame_paths(tmp_path, mocker):
    mocker.patch("shutil.which", return_value="/usr/bin/ffmpeg")
    # Use a real path that exists (tmp_path itself) as the video to bypass the existence check
    fake_video = tmp_path / "video.mp4"
    fake_video.touch()
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(returncode=0, stdout="10.0\n")
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    # Simulate ffmpeg creating 12 frame files
    for i in range(1, 13):
        (frames_dir / f"frame_{i:03d}.jpg").touch()

    frames = extract_frames(fake_video, frames_dir)
    assert len(frames) == 12
    assert all(f.suffix == ".jpg" for f in frames)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_video.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` — `src.video` does not exist yet.

- [ ] **Step 3: Implement `src/video.py`**

```python
import shutil
import subprocess
from pathlib import Path


class FrameExtractionError(Exception):
    pass


def extract_frames(video_path: Path, output_dir: Path, num_frames: int = 12) -> list[Path]:
    """Extract num_frames evenly spaced frames from video_path into output_dir."""
    if shutil.which("ffmpeg") is None:
        raise FrameExtractionError(
            "ffmpeg is not installed. Install it with: brew install ffmpeg (macOS) "
            "or apt install ffmpeg (Linux)"
        )

    if not video_path.exists():
        raise FrameExtractionError(f"Video file not found: {video_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_pattern = str(output_dir / "frame_%03d.jpg")

    # Use fps filter to extract evenly spaced frames
    # Get video duration first, then compute fps to yield num_frames
    probe = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(video_path),
        ],
        capture_output=True, text=True,
    )
    duration = float(probe.stdout.strip()) if probe.returncode == 0 and probe.stdout.strip() else None

    if duration:
        fps = num_frames / duration
        vf_filter = f"fps={fps:.6f}"
    else:
        # Fallback: extract every Nth frame
        vf_filter = f"select='not(mod(n\\,10))',setpts=N/FRAME_RATE/TB"

    result = subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-vf", vf_filter,
         "-frames:v", str(num_frames), "-q:v", "2", output_pattern, "-y"],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        raise FrameExtractionError(f"ffmpeg failed:\n{result.stderr}")

    frames = sorted(output_dir.glob("frame_*.jpg"))
    return frames
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_video.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/video.py tests/test_video.py
git commit -m "feat: frame extraction via ffmpeg"
```

---

## Task 3: GPT-4o Vision Analyzer (`src/analyzer.py`)

**Files:**
- Create: `src/analyzer.py`
- Create: `tests/test_analyzer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_analyzer.py
import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.analyzer import analyze_frames, AnalysisResult, AnalyzerError


MOCK_RESPONSE = {
    "sport": "tennis",
    "score": 7,
    "strengths": ["Good stance", "Consistent toss"],
    "issues": ["Elbow too low on backswing (frame 3)", "Weight not transferring (frame 8)"],
    "suggestions": ["Keep elbow at shoulder height during backswing", "Step into the ball"],
    "summary": "Overall solid technique with room to improve power generation."
}


def test_raises_if_no_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AnalyzerError, match="OPENAI_API_KEY"):
        analyze_frames([], "context", api_key=None)


def test_returns_analysis_result(tmp_path, mocker):
    # Create a tiny 1x1 JPEG for testing
    frame = tmp_path / "frame_001.jpg"
    frame.write_bytes(
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
        b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
        b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\x1e\xc0'
        b'\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00'
        b'\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01'
        b'\x01\x00\x00?\x00\xf5\x0f\xff\xd9'
    )

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=json.dumps(MOCK_RESPONSE)))]
    )
    mocker.patch("src.analyzer.openai.OpenAI", return_value=mock_client)

    result = analyze_frames([frame], "I am a beginner tennis player", api_key="sk-test")

    assert isinstance(result, AnalysisResult)
    assert result.sport == "tennis"
    assert result.score == 7
    assert len(result.strengths) == 2
    assert len(result.issues) == 2
    assert len(result.suggestions) == 2
    assert result.summary != ""


def test_raises_on_invalid_json_response(tmp_path, mocker):
    frame = tmp_path / "frame_001.jpg"
    frame.write_bytes(b'\xff\xd8\xff\xd9')  # minimal JPEG

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="not json at all"))]
    )
    mocker.patch("src.analyzer.openai.OpenAI", return_value=mock_client)

    with pytest.raises(AnalyzerError, match="Failed to parse"):
        analyze_frames([frame], "context", api_key="sk-test")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_analyzer.py -v
```

Expected: `ImportError` — `src.analyzer` does not exist yet.

- [ ] **Step 3: Implement `src/analyzer.py`**

```python
import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path

import openai


class AnalyzerError(Exception):
    pass


@dataclass
class AnalysisResult:
    sport: str
    score: int
    strengths: list[str]
    issues: list[str]
    suggestions: list[str]
    summary: str


SYSTEM_PROMPT = """You are a professional sports coach with decades of experience analyzing athlete technique.
Analyze the provided video frames and background context, then respond ONLY with a JSON object using this exact schema:
{
  "sport": "<detected sport>",
  "score": <integer 0-10>,
  "strengths": ["<observed strength>", ...],
  "issues": ["<technique problem with frame reference>", ...],
  "suggestions": ["<prioritized improvement>", ...],
  "summary": "<narrative paragraph>"
}
Be specific, reference frame numbers where relevant, and give actionable coaching advice."""


def _encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def analyze_frames(frames: list[Path], context: str, api_key: str | None = None) -> AnalysisResult:
    """Send frames to GPT-4o Vision and return structured analysis."""
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise AnalyzerError(
            "OPENAI_API_KEY is not set. Add it to your .env file:\n  OPENAI_API_KEY=sk-..."
        )

    client = openai.OpenAI(api_key=key)

    content: list[dict] = [
        {"type": "text", "text": f"Athlete background: {context}\n\nAnalyze the following {len(frames)} frames:"}
    ]
    for i, frame in enumerate(frames, 1):
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{_encode_image(frame)}",
                "detail": "low",
            },
        })
        content.append({"type": "text", "text": f"[Frame {i}]"})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            max_tokens=1500,
        )
    except openai.OpenAIError as e:
        raise AnalyzerError(f"OpenAI API error: {e}") from e

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON block if wrapped in markdown
        import re
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
        else:
            raise AnalyzerError(f"Failed to parse API response as JSON:\n{raw}")

    return AnalysisResult(
        sport=data.get("sport", "unknown"),
        score=int(data.get("score", 0)),
        strengths=data.get("strengths", []),
        issues=data.get("issues", []),
        suggestions=data.get("suggestions", []),
        summary=data.get("summary", ""),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_analyzer.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/analyzer.py tests/test_analyzer.py
git commit -m "feat: GPT-4o Vision analyzer with structured output"
```

---

## Task 4: Reference Image Search (`src/search.py`)

**Files:**
- Create: `src/search.py`
- Create: `tests/test_search.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_search.py
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.search import fetch_reference_images


def test_returns_empty_list_on_search_failure(tmp_path, mocker):
    mocker.patch("src.search.DDGS", side_effect=Exception("network error"))
    result = fetch_reference_images("tennis", tmp_path)
    assert result == []


def test_returns_empty_list_on_download_failure(tmp_path, mocker):
    mock_ddgs = MagicMock()
    mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
    mock_ddgs.__exit__ = MagicMock(return_value=False)
    mock_ddgs.images.return_value = [
        {"image": "http://example.com/img1.jpg"},
    ]
    mocker.patch("src.search.DDGS", return_value=mock_ddgs)
    mocker.patch("requests.get", side_effect=Exception("timeout"))

    result = fetch_reference_images("tennis", tmp_path)
    assert result == []


def test_downloads_up_to_3_images(tmp_path, mocker):
    mock_ddgs = MagicMock()
    mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
    mock_ddgs.__exit__ = MagicMock(return_value=False)
    mock_ddgs.images.return_value = [
        {"image": f"http://example.com/img{i}.jpg"} for i in range(5)
    ]
    mocker.patch("src.search.DDGS", return_value=mock_ddgs)

    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock()
    fake_response.content = b'\xff\xd8\xff\xd9'  # minimal JPEG bytes
    mocker.patch("requests.get", return_value=fake_response)

    result = fetch_reference_images("tennis", tmp_path)
    assert len(result) == 3
    assert all(p.suffix == ".jpg" for p in result)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_search.py -v
```

Expected: `ImportError` — `src.search` does not exist yet.

- [ ] **Step 3: Implement `src/search.py`**

```python
import logging
from pathlib import Path

import requests
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


def fetch_reference_images(sport: str, output_dir: Path, max_images: int = 3) -> list[Path]:
    """Search DuckDuckGo for standard technique images and download them."""
    output_dir.mkdir(parents=True, exist_ok=True)
    query = f"{sport} standard technique professional athlete"
    downloaded: list[Path] = []

    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=max_images * 2))
    except Exception as e:
        logger.warning(f"Reference image search failed: {e}")
        return []

    for i, result in enumerate(results):
        if len(downloaded) >= max_images:
            break
        url = result.get("image", "")
        if not url:
            continue
        dest = output_dir / f"ref_{i + 1:03d}.jpg"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            downloaded.append(dest)
        except Exception as e:
            logger.warning(f"Failed to download reference image {url}: {e}")
            continue

    return downloaded
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_search.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/search.py tests/test_search.py
git commit -m "feat: DuckDuckGo reference image search with graceful degradation"
```

---

## Task 5: Markdown Report Assembly (`src/report.py`)

**Files:**
- Create: `src/report.py`
- Create: `tests/test_report.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_report.py
import pytest
from pathlib import Path
from datetime import date
from src.analyzer import AnalysisResult
from src.report import generate_report


MOCK_RESULT = AnalysisResult(
    sport="tennis",
    score=7,
    strengths=["Good stance", "Consistent toss"],
    issues=["Elbow too low on backswing (frame 3)"],
    suggestions=["Keep elbow at shoulder height"],
    summary="Overall solid technique with room to improve power generation.",
)


def test_report_file_is_created(tmp_path):
    frames = [tmp_path / f"frame_{i:03d}.jpg" for i in range(1, 4)]
    for f in frames:
        f.touch()
    references = [tmp_path / "ref_001.jpg"]
    references[0].touch()

    report_path = generate_report(
        result=MOCK_RESULT,
        context="I am a beginner",
        frames=frames,
        references=references,
        output_dir=tmp_path,
    )

    assert report_path.exists()
    assert report_path.suffix == ".md"


def test_report_contains_key_sections(tmp_path):
    frames = [tmp_path / f"frame_{i:03d}.jpg" for i in range(1, 4)]
    for f in frames:
        f.touch()

    report_path = generate_report(
        result=MOCK_RESULT,
        context="I am a beginner",
        frames=frames,
        references=[],
        output_dir=tmp_path,
    )

    content = report_path.read_text()
    assert "# Coach Analysis: tennis" in content
    assert "## Background" in content
    assert "## Key Frames" in content
    assert "Overall Score: 7/10" in content
    assert "## Strengths" in content
    assert "## Issues Found" in content
    assert "## Improvement Suggestions" in content
    assert "## Coach Summary" in content
    assert "Good stance" in content
    assert "Keep elbow at shoulder height" in content


def test_report_skips_reference_section_when_empty(tmp_path):
    frames = [tmp_path / "frame_001.jpg"]
    frames[0].touch()

    report_path = generate_report(
        result=MOCK_RESULT,
        context="context",
        frames=frames,
        references=[],
        output_dir=tmp_path,
    )

    content = report_path.read_text()
    assert "## Standard Reference" not in content


def test_report_includes_reference_section_when_present(tmp_path):
    frames = [tmp_path / "frame_001.jpg"]
    frames[0].touch()
    ref = tmp_path / "ref_001.jpg"
    ref.touch()

    report_path = generate_report(
        result=MOCK_RESULT,
        context="context",
        frames=frames,
        references=[ref],
        output_dir=tmp_path,
    )

    content = report_path.read_text()
    assert "## Standard Reference" in content
    assert "ref_001.jpg" in content
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_report.py -v
```

Expected: `ImportError` — `src.report` does not exist yet.

- [ ] **Step 3: Implement `src/report.py`**

```python
from datetime import datetime
from pathlib import Path

from src.analyzer import AnalysisResult


def generate_report(
    result: AnalysisResult,
    context: str,
    frames: list[Path],
    references: list[Path],
    output_dir: Path,
) -> Path:
    """Assemble and save a Markdown coach analysis report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"report_{timestamp}.md"

    lines: list[str] = []

    # Header
    date_str = datetime.now().strftime("%Y-%m-%d")
    lines += [
        f"# Coach Analysis: {result.sport.title()} — {date_str}",
        "",
        "## Background",
        "",
        context,
        "",
    ]

    # Key Frames
    lines += ["## Key Frames", ""]
    for frame in frames:
        rel = frame.relative_to(output_dir) if frame.is_relative_to(output_dir) else frame
        lines.append(f"![{frame.stem}]({rel})")
    lines.append("")

    # Analysis
    lines += [
        "## Analysis",
        "",
        f"### Overall Score: {result.score}/10",
        "",
        "## Strengths",
        "",
    ]
    for s in result.strengths:
        lines.append(f"- {s}")
    lines.append("")

    lines += ["## Issues Found", ""]
    for issue in result.issues:
        lines.append(f"- {issue}")
    lines.append("")

    lines += ["## Improvement Suggestions", ""]
    for i, suggestion in enumerate(result.suggestions, 1):
        lines.append(f"{i}. {suggestion}")
    lines.append("")

    lines += ["## Coach Summary", "", result.summary, ""]

    # Reference images (optional)
    if references:
        lines += ["## Standard Reference", ""]
        for ref in references:
            rel = ref.relative_to(output_dir) if ref.is_relative_to(output_dir) else ref
            lines.append(f"![Reference: {ref.stem}]({rel})")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_report.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/report.py tests/test_report.py
git commit -m "feat: Markdown report assembly"
```

---

## Task 6: CLI Entry Point (`coach.py`)

**Files:**
- Create: `coach.py`

No unit tests for the CLI orchestrator — it is thin glue code. Integration is verified by a manual smoke test in the next step.

- [ ] **Step 1: Implement `coach.py`**

```python
#!/usr/bin/env python3
"""AI Sports Coach Analyzer — CLI entry point."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.video import extract_frames, FrameExtractionError
from src.analyzer import analyze_frames, AnalyzerError
from src.search import fetch_reference_images
from src.report import generate_report

load_dotenv()


def get_context(args: argparse.Namespace) -> str:
    if args.context:
        return args.context
    if args.context_file:
        p = Path(args.context_file)
        if not p.exists():
            print(f"Error: context file not found: {p}", file=sys.stderr)
            sys.exit(1)
        return p.read_text(encoding="utf-8").strip()
    # Interactive fallback
    print("No background context provided.")
    print("Please describe the athlete (sport, level, goals):")
    return input("> ").strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Sports Coach: analyze a sports video with GPT-4o Vision"
    )
    parser.add_argument("--video", required=True, help="Path to the local video file")
    parser.add_argument("--context", help="Background description (inline string)")
    parser.add_argument("--context-file", help="Path to a text file with background description")
    parser.add_argument(
        "--output-dir", default="output", help="Directory to save report and images (default: output/)"
    )
    args = parser.parse_args()

    video_path = Path(args.video)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    context = get_context(args)

    frames_dir = output_dir / "frames"
    print(f"Extracting frames from {video_path}...")
    try:
        frames = extract_frames(video_path, frames_dir)
    except FrameExtractionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"  → {len(frames)} frames extracted to {frames_dir}")

    api_key = os.getenv("OPENAI_API_KEY")
    print("Analyzing with GPT-4o Vision...")
    try:
        result = analyze_frames(frames, context, api_key=api_key)
    except AnalyzerError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"  → Sport detected: {result.sport}, Score: {result.score}/10")

    refs_dir = output_dir / "references"
    print(f"Searching for '{result.sport}' reference images...")
    references = fetch_reference_images(result.sport, refs_dir)
    print(f"  → {len(references)} reference image(s) downloaded")

    print("Generating Markdown report...")
    report_path = generate_report(
        result=result,
        context=context,
        frames=frames,
        references=references,
        output_dir=output_dir,
    )
    print(f"\nDone! Report saved to: {report_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify help output works**

```bash
python coach.py --help
```

Expected: Usage message printed with `--video`, `--context`, `--context-file`, `--output-dir` options.

- [ ] **Step 3: Commit**

```bash
git add coach.py
git commit -m "feat: CLI entry point and pipeline orchestration"
```

---

## Task 7: Final Wiring and Smoke Test

- [ ] **Step 1: Run all tests**

```bash
pytest -v
```

Expected: All tests PASS.

- [ ] **Step 2: Verify error cases manually**

```bash
# Missing video
python coach.py --video /nonexistent.mp4 --context "test"
# Expected: "Error: Video file not found: /nonexistent.mp4"

# Missing API key
OPENAI_API_KEY="" python coach.py --video /nonexistent.mp4 --context "test"
# Expected: "Error: OPENAI_API_KEY is not set..."
```

- [ ] **Step 3: (Optional) Smoke test with a real video if OPENAI_API_KEY is set**

```bash
# Download a short test video (5–10 seconds)
python coach.py --video path/to/test.mp4 --context "I am a beginner learning tennis forehand"
```

Expected: `output/report_YYYYMMDD_HHMMSS.md` created with analysis.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "test: verify all tests pass and CLI wiring is complete"
```
