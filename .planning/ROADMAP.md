# Roadmap: AI 网球教练 Web 版

**Project:** AI Tennis Coach Web Extension  
**Created:** 2026-04-21  
**Phases:** 7  
**Estimated Duration:** 6-8 weeks

---

## Milestone v1.0: Complete Web Experience

**Goal:** 功能完整的 Web 版网球教练，用户可以上传视频、查看丰富的可视化分析报告、与职业选手对比。

**Success Criteria:**
- 流畅的上传 → 分析 → 报告 完整流程
- 所有 38 个 v1 需求完成
- 本地可运行，单用户友好

---

## Phase Overview

| Phase | Name | Focus | Requirements | Est. Duration |
|-------|------|-------|--------------|---------------|
| 1 | Project Setup | Vue 项目 + API 基础 | UPLD-01~04 | 3-5 days |
| 2 | Analysis Pipeline | 异步分析后端 + 状态管理 | PIPE-01~04 | 5-7 days |
| 3 | Video Player | 标注视频播放器 + 帧查看器 | PLAY-01~05, FRAME-01~04 | 7-10 days |
| 4 | Charts | 数据可视化 | CHART-01~04 | 5-7 days |
| 5 | Comparison | 职业选手对比 | COMP-01~04 | 5-7 days |
| 6 | Report | 结构化报告页 | RPT-01~06 | 5-7 days |
| 7 | History | 历史记录管理 | HIST-01~04 | 3-5 days |

---

## Phase 1: Project Setup

**Goal:** 初始化 Vue 项目，搭建开发环境，完成视频上传界面

**Requirements:** UPLD-01, UPLD-02, UPLD-03, UPLD-04

**Key Deliverables:**
- Vue 3 + TypeScript + Vite 项目结构
- 前端路由和基础布局
- 视频上传组件（拖拽 + 选择）
- 后端 Flask/FastAPI API 框架
- 上传接口（接收视频并保存）

**Technical Notes:**
- 前端：Vue 3 Composition API + TypeScript
- 样式：Tailwind CSS 或 UnoCSS
- 后端：FastAPI（轻量，异步支持好）
- 视频存储：本地文件系统 output/uploads/

**Dependencies:**
- Phase 1 is independent

---

## Phase 2: Analysis Pipeline

**Goal:** 连接现有 Python 分析引擎，实现异步分析流程

**Requirements:** PIPE-01, PIPE-02, PIPE-03, PIPE-04

**Key Deliverables:**
- 异步任务队列（Celery 或 Python asyncio + FastAPI BackgroundTasks）
- 调用现有 coach.py 分析视频
- 状态管理 API（查询分析进度）
- 前端分析状态显示（等待中/分析中/完成/失败）
- 分析完成通知和自动跳转

**Technical Notes:**
- 复用 coach.py 和 tennis_annotate.py 的调用逻辑
- 分析输出目录规范化（output/analysis/{id}/）
- 状态持久化：JSON 文件或 SQLite

**Dependencies:**
- Depends on Phase 1（需要上传功能）

---

## Phase 3: Video Player

**Goal:** 实现标注视频播放器和交互式帧查看器

**Requirements:** PLAY-01~05, FRAME-01~04

**Key Deliverables:**
- HTML5 Video 播放器组件
- Canvas 叠加层（绘制身体部位圆圈和问题标签）
- 时间轴自定义（标记问题帧）
- 问题帧缩略图列表组件
- 点击帧缩略图跳转到对应时间
- 问题类型筛选器

**Technical Notes:**
- 使用 Canvas 2D 在视频上绘制标注
- 同步视频时间和标注数据显示
- 从后端获取标注数据（坐标 + 标签）

**Dependencies:**
- Depends on Phase 2（需要分析结果）

---

## Phase 4: Charts

**Goal:** 实现数据可视化图表

**Requirements:** CHART-01, CHART-02, CHART-03, CHART-04

**Key Deliverables:**
- 发球高度趋势折线图
- 击球点分布热力图（Court Heatmap）
- 动作一致性雷达图（6 维度）
- 问题类型统计图

**Technical Notes:**
- 图表库：ECharts（功能丰富，支持热力图）
- 从 coach_*.md 和 annotate_*.md 解析数据
- 可能需要扩展后端 API 返回结构化数据

**Dependencies:**
- Depends on Phase 2（需要分析结果）
- Can be developed in parallel with Phase 3

---

## Phase 5: Comparison

**Goal:** 实现职业选手对比功能

**Requirements:** COMP-01, COMP-02, COMP-03, COMP-04

**Key Deliverables:**
- 职业选手视频库（内置样本）
- 分屏对比播放器组件
- 同步播放控制（播放/暂停/进度同步）
- 关键帧对齐标记功能

**Technical Notes:**
- 职业选手视频存储在 static/pros/ 目录
- 同步播放需要考虑视频时长差异
- 关键帧对齐：用户手动标记对比点

**Dependencies:**
- Depends on Phase 3（复用播放器组件）

---

## Phase 6: Report

**Goal:** 实现结构化教练报告页面

**Requirements:** RPT-01~06

**Key Deliverables:**
- 综合评分卡片（总分 + 6 维度）
- 亮点展示区域
- 问题深度分析（分页/滚动展示）
- 问题汇总表
- 专项训练计划
- 教练总结

**Technical Notes:**
- 解析 coach_*.md 报告内容
- 设计清晰的信息层次
- 可打印/导出 PDF 格式

**Dependencies:**
- Depends on Phase 2（需要分析结果）
- Can be developed in parallel with Phases 3-5

---

## Phase 7: History

**Goal:** 实现分析历史管理

**Requirements:** HIST-01, HIST-02, HIST-03, HIST-04

**Key Deliverables:**
- 历史列表页面
- 搜索和筛选功能
- 删除确认对话框
- 重新打开历史报告

**Technical Notes:**
- 分析元数据存储（ID、日期、视频名、评分、状态）
- 本地文件管理（清理已删除的分析文件）

**Dependencies:**
- Depends on Phase 2（需要分析任务管理）

---

## Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Pipeline)
    ↓
    ├── Phase 3 (Player) ──→ Phase 5 (Comparison)
    ├── Phase 4 (Charts)
    └── Phase 6 (Report)
    ↓
Phase 7 (History)
```

---

## Execution Order Recommendation

**Sequential（推荐）：**
1. Phase 1 → Phase 2 → Phase 3 → Phase 5 → Phase 6 → Phase 4 → Phase 7

**Rationale:**
- Phase 1-2 是基础必须先做
- Phase 3 是核心体验，完成后可以直观感受产品
- Phase 5 依赖 Phase 3 的播放器组件
- Phase 6 可以并行但建议在看板后完成以调整报告设计
- Phase 4 图表可以稍晚（锦上添花）
- Phase 7 是收尾功能

---

## Next Steps

1. Run `/gsd-plan-phase 1` to start detailed planning for Phase 1
2. Review requirements and provide feedback if needed
3. Proceed with Phase 1 execution

---
*Roadmap created: 2026-04-21*
