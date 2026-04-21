# AI 网球教练 Web 版 (AI Tennis Coach Web)

## What This Is

基于现有的 AI Sports Coach 命令行工具，扩展为一个完整的 Vue Web 应用。用户上传网球训练视频，系统通过 GPT-4o 进行技术分析，生成带有身体部位标注的视频回放、交互式帧查看器、数据图表和结构化教练报告。内置职业选手视频库用于动作对比。

这是一个**brownfield 项目** — 已有可用的 Python 分析引擎（coach.py + tennis_annotate.py），当前工作聚焦于 Web 层封装和可视化增强。

## Core Value

**提供丰富、直观、可交互的技术分析反馈，让业余网球爱好者能够像有专业教练在场一样改进动作。**

所有其他功能（对比库、图表、报告）都服务于这一核心：让用户清楚地看到自己哪里做得不对，以及如何改进。

## Requirements

### Validated

- ✓ 视频帧提取和分析（coach.py）— 现有
- ✓ GPT-4o 视觉分析和教练点评 — 现有
- ✓ 身体部位标注（21 种问题类型识别）— 现有
- ✓ Markdown 结构化报告生成 — 现有
- ✓ 标注图片生成 — 现有

### Active

- [ ] Web 视频上传界面（拖拽 + 进度显示）
- [ ] 异步分析任务队列（上传 → 分析中 → 完成）
- [ ] 标注视频播放器（播放原始视频 + 叠加标注层）
- [ ] 交互式帧查看器（时间轴 + 问题帧列表 + 点击跳转）
- [ ] 数据图表（发球高度趋势、击球点分布热力图、动作一致性雷达图）
- [ ] 职业选手对比（分屏对比、同步播放、关键帧对齐）
- [ ] 结构化报告页面（评分、问题列表、训练计划）
- [ ] 分析历史管理（列表、搜索、删除）

### Out of Scope

| Feature | Reason |
|---------|--------|
| 实时分析 | 用户明确不需要，现有流程为异步 |
| 移动端 App | v1 聚焦 Web，响应式布局适配移动端浏览器即可 |
| 社交/分享功能 | 非核心，个人训练工具 |
| 多租户/云端部署 | 本地运行，单用户使用 |
| 自动摄像头捕获 | 用户明确不需要实时 |
| AI 语音讲解 | 文本报告已足够，增加复杂度 |

## Context

### 现有代码结构

```
├── coach.py              # 视频分析入口：提取帧 → GPT-4o 分析 → 生成教练报告
├── tennis_annotate.py    # 帧标注：身体部位圆圈 + 问题标签 → 标注图片
├── src/                  # 共享工具模块
├── .claude/skills/       # Claude Code skills（各运动项目）
├── output/               # 分析输出目录
│   └── tennis/
│       ├── frames/          # 原始视频帧
│       ├── annotated/       # 标注后的帧
│       ├── coach_*.md       # 教练分析报告
│       └── annotate_*.md    # 逐帧标注报告
```

### 技术环境

- **后端**: Python 3.11+, OpenAI GPT-4o, ffmpeg
- **前端**: Vue 3 + TypeScript
- **部署**: 本地运行（localhost）

### 关键依赖

- 视频处理：ffmpeg 提取帧
- AI 分析：OpenAI API（GPT-4o vision）
- 标注绘制：PIL（后端生成标注图）
- 图表库：ECharts 或 Chart.js（前端）
- 视频播放：原生 HTML5 video + Canvas 叠加层

## Constraints

- **Tech Stack**: Vue 3 + TypeScript 前端，保持现有 Python 后端
- **Runtime**: 本地部署，单用户，无需认证系统
- **Browser**: 现代浏览器（Chrome/Firefox/Safari/Edge）
- **Video Format**: 支持 mp4/mov/avi/mkv（ffmpeg 支持的格式）
- **Data Storage**: 本地文件系统（output/ 目录），无需数据库
- **AI Limits**: GPT-4o API 调用成本和延迟是主要瓶颈

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Vue 3 + TypeScript | 用户指定，现代前端栈 | — Pending |
| 保持 Python 后端不变 | 现有分析引擎已成熟，复用 | — Pending |
| 本地文件存储 | 本地运行，简化部署 | — Pending |
| 异步分析队列 | 视频分析耗时（GPT-4o），不能阻塞 UI | — Pending |
| Canvas 叠加标注 | 比预生成标注图更灵活，支持交互 | — Pending |
| 内嵌职业选手视频 | 本地存储，避免版权问题 | — Pending |

---

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-21 after initialization*
