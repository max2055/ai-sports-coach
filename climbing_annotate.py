#!/usr/bin/env python3
"""
climbing_annotate.py — 室内攀岩教练标注工具
1. 把所有帧一次性发给 GPT-4o，返回攀岩者身体部位坐标 + 技术问题
2. 用 PIL 在每帧上标注：身体圆圈、手脚点位、问题区域（英文标签）
3. 生成含标注图片的逐体位分析 Markdown 报告
"""

import base64
import json
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path

import openai
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

# ── 路径配置 ──────────────────────────────────────────────────────────────────
FRAMES_DIR    = Path("output/frames")
ANNOTATED_DIR = Path("output/climbing_annotated")
REPORT_PATH   = Path(f"output/climbing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

# ── 颜色（PIL RGB）────────────────────────────────────────────────────────────
COLOR = {
    "body":         ( 30, 144, 255),   # 蓝 — 身体重心
    "hand_l":       ( 50, 200,  80),   # 绿 — 左手
    "hand_r":       ( 20, 160,  50),   # 深绿 — 右手
    "foot_l":       (255, 140,   0),   # 橙 — 左脚
    "foot_r":       (220, 100,   0),   # 深橙 — 右脚
    "issue_ring":   (255,  50,  50),   # 红 — 问题高亮外圈
    "good_ring":    ( 50, 220,  80),   # 绿 — 正确标注外圈
    "label_body":   ( 20, 100, 200),
    "label_hand":   ( 20, 130,  50),
    "label_foot":   (180,  90,   0),
    "label_fg":     (255, 255, 255),
    "issue_note_bg":(  0,   0,   0),
    "issue_note_fg":(255, 220,  80),
}

# ── 问题类型（英文标签）───────────────────────────────────────────────────────
ISSUE_LABELS = {
    "poor_footwork":  "POOR FOOT",
    "straight_arm":   "STRAIGHT ARM",
    "hip_drop":       "HIP DROP",
    "barn_door":      "BARN DOOR",
    "overgrip":       "OVERGRIP",
    "stiff_hip":      "STIFF HIP",
    "read_error":     "WRONG SEQ",
    "rest_missed":    "MISSED REST",
    "good_position":  "GOOD POS",
    "good_footwork":  "GOOD FOOT",
}

# ── GPT-4o System Prompt ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a professional indoor rock climbing coach analyzing training footage for technique improvement.
You will receive sequential video frames from the same climbing session.

Your task is sports biomechanics analysis — describe climber body part POSITIONS using spatial coordinates only.
Do NOT attempt to identify the person. Focus on posture, balance, and movement quality.

For each frame, locate the climber and their limbs:
- body: center of mass / torso center
- hand_l: left hand contact point
- hand_r: right hand contact point
- foot_l: left foot contact point
- foot_r: right foot contact point

All positions as fractions of image width (x_pct) and height (y_pct), range 0.0-1.0.
Radius (radius_pct) relative to image width: body ~0.06, limbs ~0.03.

Classify technique issues using ONLY these types:
- poor_footwork: foot placement imprecise, wrong edge, toe slipping off hold
- straight_arm: locked elbows when resting (should be straight only when hanging, bent when moving)
- hip_drop: hips sagging away from wall — increases arm load
- barn_door: body rotating away from wall, losing balance
- overgrip: over-gripping holds (wasted forearm energy)
- stiff_hip: hips not turned into wall on sidepull / layback moves
- read_error: wrong move sequence or route choice
- rest_missed: skipped a no-hands or shake-out rest position
- good_position: correct technique — highlight positively
- good_footwork: precise, quiet foot placement — highlight positively

issue_note and frame_summary MUST be in ENGLISH.
Climber analysis fields (strengths, issues detail, improvement) should be in Chinese.

Respond ONLY with valid JSON (no markdown):
{
  "frames": {
    "1": {
      "climbers": [
        {
          "id": "C1",
          "body":   {"x_pct": 0.50, "y_pct": 0.40, "radius_pct": 0.06},
          "hand_l": {"x_pct": 0.40, "y_pct": 0.28, "radius_pct": 0.03, "issue_type": "", "issue_note": ""},
          "hand_r": {"x_pct": 0.58, "y_pct": 0.25, "radius_pct": 0.03, "issue_type": "", "issue_note": ""},
          "foot_l": {"x_pct": 0.42, "y_pct": 0.60, "radius_pct": 0.03, "issue_type": "poor_footwork", "issue_note": "Toe not on hold center"},
          "foot_r": {"x_pct": 0.55, "y_pct": 0.58, "radius_pct": 0.03, "issue_type": "", "issue_note": ""},
          "body_issue_type": "hip_drop",
          "body_issue_note": "Hips 30cm from wall, overloading arms"
        }
      ],
      "frame_summary": "Climber on overhang section, hips sagging, left foot placement imprecise."
    }
  },
  "climber_analysis": {
    "C1": {
      "overall_rating": 6,
      "strengths": ["优点1（中文）", "优点2"],
      "issues": [
        {"frame": 3, "type": "hip_drop", "body_part": "body", "detail": "中文详细描述"}
      ],
      "improvement": "可操作训练建议（中文，分3条列出）"
    }
  },
  "route_summary": "路线整体攀爬质量评价（中文，3-5句）",
  "overall_score": 6
}"""


def encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def call_gpt4o(frames: list[Path]) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = openai.OpenAI(api_key=api_key)
    content: list[dict] = [
        {"type": "text", "text": f"Indoor rock climbing training footage — {len(frames)} sequential frames for biomechanics analysis:"}
    ]
    for i, frame in enumerate(frames, 1):
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encode_image(frame)}", "detail": "low"},
        })
        content.append({"type": "text", "text": f"[Frame {i}]"})

    print("  → 发送帧到 GPT-4o（攀岩技术分析）...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": content},
        ],
        max_tokens=4000,
    )

    raw = response.choices[0].message.content
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise RuntimeError(f"JSON 解析失败:\n{raw}")


# ── 绘制工具 ──────────────────────────────────────────────────────────────────

def get_font(size: int):
    for p in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_label(draw, text, cx, cy, bg, fg, font, padding=3):
    """在 (cx, cy) 上方绘制带背景标签。"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x0, y0 = cx - tw // 2 - padding, cy - th - padding * 2 - 4
    x1, y1 = cx + tw // 2 + padding, cy - 4
    draw.rectangle([x0, y0, x1, y1], fill=bg)
    draw.text((x0 + padding, y0 + padding), text, font=font, fill=fg)


def draw_issue_note(draw, note, cx, cy, img_w, font):
    """在 (cx, cy) 下方绘制问题说明（英文，自动换行）。"""
    lines = textwrap.wrap(note, 16)[:2]
    y = cy + 38
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        tx = max(4, min(cx - tw // 2, img_w - tw - 4))
        draw.rectangle([tx - 2, y - 1, tx + tw + 2, y + 15], fill=COLOR["issue_note_bg"] + (180,))
        draw.text((tx, y), line, font=font, fill=COLOR["issue_note_fg"])
        y += 16


def draw_part(draw, part_data, label, bg_color, img_w, img_h, font_label, font_note):
    """绘制单个身体部位（手/脚/身体）。"""
    if not part_data:
        return
    x_pct     = float(part_data.get("x_pct", 0))
    y_pct     = float(part_data.get("y_pct", 0))
    r_pct     = float(part_data.get("radius_pct", 0.03))
    issue_type = part_data.get("issue_type", "")
    issue_note = part_data.get("issue_note", "")

    cx = int(x_pct * img_w)
    cy = int(y_pct * img_h)
    r  = max(int(r_pct * img_w), 14)

    is_issue = issue_type and issue_type not in ("good_position", "good_footwork")
    is_good  = issue_type in ("good_position", "good_footwork")

    # 外圈
    if is_issue:
        draw.ellipse([cx-r-5, cy-r-5, cx+r+5, cy+r+5], outline=COLOR["issue_ring"]+(210,), width=3)
    elif is_good:
        draw.ellipse([cx-r-5, cy-r-5, cx+r+5, cy+r+5], outline=COLOR["good_ring"]+(210,), width=3)

    # 主圈
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=bg_color+(220,), width=2)

    # 标签
    tag = ISSUE_LABELS.get(issue_type, "")
    full_label = f"{label}" + (f" {tag}" if tag else "")
    draw_label(draw, full_label, cx, cy, bg=bg_color+(200,), fg=COLOR["label_fg"], font=font_label)

    # 问题说明
    if issue_note and is_issue:
        draw_issue_note(draw, issue_note, cx, cy, img_w, font_note)


def annotate_frame(frame_path: Path, climbers: list[dict], out_path: Path):
    img = Image.open(frame_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    W, H = img.size

    font_label = get_font(15)
    font_note  = get_font(12)

    for c in climbers:
        cid = c.get("id", "C1")

        # 身体（重心）
        body = c.get("body", {})
        body_issue = {"x_pct": body.get("x_pct", 0), "y_pct": body.get("y_pct", 0),
                      "radius_pct": body.get("radius_pct", 0.06),
                      "issue_type": c.get("body_issue_type", ""),
                      "issue_note": c.get("body_issue_note", "")}
        draw_part(draw, body_issue, cid, COLOR["body"], W, H, font_label, font_note)

        # 手脚
        parts = [
            (c.get("hand_l"), "L.Hand", COLOR["hand_l"]),
            (c.get("hand_r"), "R.Hand", COLOR["hand_r"]),
            (c.get("foot_l"), "L.Foot", COLOR["foot_l"]),
            (c.get("foot_r"), "R.Foot", COLOR["foot_r"]),
        ]
        for part_data, part_label, part_color in parts:
            if part_data:
                draw_part(draw, part_data, part_label, part_color, W, H, font_label, font_note)

    combined = Image.alpha_composite(img, overlay).convert("RGB")
    combined.save(out_path, "JPEG", quality=90)


# ── Markdown 报告 ─────────────────────────────────────────────────────────────

ISSUE_TYPE_CN = {
    "poor_footwork":  "脚法不精准",
    "straight_arm":   "手臂僵直",
    "hip_drop":       "髋部下沉",
    "barn_door":      "侧翻失衡",
    "overgrip":       "过度抓握",
    "stiff_hip":      "髋部不转",
    "read_error":     "路线误判",
    "rest_missed":    "漏掉休息位",
    "good_position":  "姿态正确",
    "good_footwork":  "脚法优秀",
}

PART_CN = {
    "body": "身体重心", "hand_l": "左手", "hand_r": "右手",
    "foot_l": "左脚", "foot_r": "右脚",
}


def generate_report(data: dict, annotated_frames: dict[str, Path]) -> str:
    lines = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    score = data.get("overall_score", "N/A")

    lines += [
        "# 室内攀岩 教练分析报告",
        "",
        f"> 分析时间：{ts}　｜　综合评分：**{score} / 10**",
        "",
    ]

    # 帧标注
    lines += ["## 关键帧标注", ""]
    frame_data = data.get("frames", {})
    for fn in sorted(annotated_frames.keys(), key=lambda x: int(x)):
        img_path = annotated_frames[fn]
        finfo = frame_data.get(fn, {})
        summary = finfo.get("frame_summary", "")
        lines += [f"### Frame {fn}", "", f"![Frame {fn}](climbing_annotated/{img_path.name})", ""]
        if summary:
            lines += [f"> {summary}", ""]

        # 本帧问题汇总
        issues = []
        for c in finfo.get("climbers", []):
            cid = c.get("id", "C1")
            body_issue = c.get("body_issue_type", "")
            body_note  = c.get("body_issue_note", "")
            if body_issue and body_issue not in ("good_position", "good_footwork"):
                issues.append(f"**{cid} 身体** — {ISSUE_TYPE_CN.get(body_issue, body_issue)}：{body_note}")
            for part_key, part_cn in PART_CN.items():
                if part_key == "body":
                    continue
                pd = c.get(part_key, {})
                if pd:
                    it = pd.get("issue_type", "")
                    note = pd.get("issue_note", "")
                    if it and it not in ("good_position", "good_footwork"):
                        issues.append(f"**{cid} {part_cn}** — {ISSUE_TYPE_CN.get(it, it)}：{note}")
        if issues:
            lines += ["**本帧问题：**", ""]
            for iss in issues:
                lines.append(f"- {iss}")
            lines += [""]

    # 逐人详细分析
    lines += ["---", "", "## 攀岩者个人分析", ""]
    for cid, ca in sorted(data.get("climber_analysis", {}).items()):
        rating  = ca.get("overall_rating", "N/A")
        strengths = ca.get("strengths", [])
        issues    = ca.get("issues", [])
        improve   = ca.get("improvement", "")

        lines += [f"### {cid}　评分：{rating} / 10", ""]
        if strengths:
            lines += ["**✅ 亮点**", ""]
            for s in strengths:
                lines.append(f"- {s}")
            lines += [""]
        if issues:
            lines += ["**❌ 问题记录**", "", "| 帧 | 问题类型 | 部位 | 描述 |", "|---|---|---|---|"]
            for iss in issues:
                fn   = iss.get("frame", "?")
                it   = ISSUE_TYPE_CN.get(iss.get("type", ""), iss.get("type", ""))
                part = PART_CN.get(iss.get("body_part", "body"), iss.get("body_part", ""))
                det  = iss.get("detail", "")
                lines.append(f"| Frame {fn} | {it} | {part} | {det} |")
            lines += [""]
        if improve:
            lines += ["**🎯 训练建议**", "", improve, ""]
        lines += ["---", ""]

    # 路线总结
    route_sum = data.get("route_summary", "")
    if route_sum:
        lines += ["## 路线总结", "", route_sum, ""]

    return "\n".join(lines)


# ── 主流程 ────────────────────────────────────────────────────────────────────
def main():
    frame_files = sorted(FRAMES_DIR.glob("frame_*.jpg"))
    if not frame_files:
        print("Error: output/frames/ 下没有帧文件，请先运行 coach.py 提取帧")
        return

    print(f"共找到 {len(frame_files)} 帧，开始攀岩技术分析...")
    data = call_gpt4o(frame_files)
    print("  → GPT-4o 分析完成")

    annotated_map: dict[str, Path] = {}
    print("生成标注图片...")
    for i, frame_path in enumerate(frame_files, 1):
        fn_key  = str(i)
        finfo   = data.get("frames", {}).get(fn_key, {})
        climbers = finfo.get("climbers", [])
        out_path = ANNOTATED_DIR / frame_path.name
        annotate_frame(frame_path, climbers, out_path)
        annotated_map[fn_key] = out_path
        print(f"  → Frame {i:02d} 标注完成")

    print("生成 Markdown 报告...")
    report_md = generate_report(data, annotated_map)
    REPORT_PATH.write_text(report_md, encoding="utf-8")

    print(f"\n✅ 完成！")
    print(f"   标注图片：{ANNOTATED_DIR}/")
    print(f"   分析报告：{REPORT_PATH}")


if __name__ == "__main__":
    main()
