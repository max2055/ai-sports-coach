# Requirements: AI 网球教练 Web 版

**Defined:** 2026-04-21
**Core Value:** 提供丰富、直观、可交互的技术分析反馈，让业余网球爱好者能够像有专业教练在场一样改进动作

## v1 Requirements

### Authentication

(None — 本地单用户，无需认证)

### Upload

- [ ] **UPLD-01**: 用户可以拖拽或选择上传视频文件（mp4/mov/avi/mkv）
- [ ] **UPLD-02**: 上传过程显示进度条
- [ ] **UPLD-03**: 上传完成后显示视频元信息（时长、分辨率、大小）
- [ ] **UPLD-04**: 支持选择分析类型（正手、反手、发球、截击、全场综合）

### Analysis Pipeline

- [ ] **PIPE-01**: 后端接收视频后启动异步分析任务
- [x] **PIPE-02
**: 前端轮询或 WebSocket 接收分析状态（等待中/分析中/完成/失败）
- [x] **PIPE-03
**: 分析完成后通知用户并自动跳转到报告页
- [x] **PIPE-04
**: 分析失败时显示错误信息和重试选项

### Video Player (Annotated)

- [ ] **PLAY-01**: 播放原始视频，画面流畅
- [ ] **PLAY-02**: 在视频上叠加标注层（身体部位圆圈 + 问题标签）
- [ ] **PLAY-03**: 标注层可开关（显示/隐藏）
- [ ] **PLAY-04**: 时间轴标记问题帧位置
- [ ] **PLAY-05**: 点击时间轴跳转到对应时间点

### Interactive Frame Viewer

- [ ] **FRAME-01**: 显示问题帧缩略图列表
- [ ] **FRAME-02**: 点击缩略图跳转到视频对应时间点
- [ ] **FRAME-03**: 显示帧的问题标签和描述
- [ ] **FRAME-04**: 支持按问题类型筛选帧

### Charts & Visualization

- [ ] **CHART-01**: 发球高度趋势图（针对发球分析）
- [ ] **CHART-02**: 击球点分布热力图
- [ ] **CHART-03**: 动作一致性雷达图（各维度评分）
- [ ] **CHART-04**: 问题类型统计饼图/柱状图

### Pro Player Comparison

- [ ] **COMP-01**: 内置职业选手视频库（正手、反手、发球各 2-3 个样本）
- [ ] **COMP-02**: 分屏对比用户视频和职业选手视频
- [ ] **COMP-03**: 同步播放控制（同时播放/暂停）
- [ ] **COMP-04**: 关键帧对齐（手动标记对比位置）

### Report View

- [ ] **RPT-01**: 显示综合评分（总分 + 6 维度分）
- [ ] **RPT-02**: 显示亮点列表（2-3 个）
- [ ] **RPT-03**: 显示问题深度分析（每个问题一页）
- [ ] **RPT-04**: 显示问题汇总表（帧/类型/部位/描述/优先级）
- [ ] **RPT-05**: 显示专项训练计划
- [ ] **RPT-06**: 显示教练总结

### History Management

- [ ] **HIST-01**: 显示历史分析列表（日期、视频名、评分）
- [ ] **HIST-02**: 支持搜索/筛选历史记录
- [ ] **HIST-03**: 支持删除历史记录
- [ ] **HIST-04**: 支持重新查看历史报告

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Multi-Sport

- **MULTI-01**: 支持切换其他运动（羽毛球、乒乓球、篮球等）

### Advanced Features

- **ADV-01**: 用户上传自己的"标准动作"作为对比基准
- **ADV-02**: 视频剪辑功能（导出问题片段）
- **ADV-03**: PPT 导出功能（复用现有 node 脚本）
- **ADV-04**: 训练计划跟踪（记录完成状态）

## Out of Scope

| Feature | Reason |
|---------|--------|
| 实时分析 | 用户明确不需要，现有流程为异步 |
| 移动端 App | v1 聚焦 Web，响应式布局适配移动端浏览器即可 |
| 社交/分享功能 | 非核心，个人训练工具 |
| 多租户/云端部署 | 本地运行，单用户使用 |
| 自动摄像头捕获 | 用户明确不需要实时 |
| AI 语音讲解 | 文本报告已足够，增加复杂度 |
| 用户账户系统 | 本地单用户，无需认证 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| UPLD-01 | Phase 1 | Pending |
| UPLD-02 | Phase 1 | Pending |
| UPLD-03 | Phase 1 | Pending |
| UPLD-04 | Phase 1 | Pending |
| PIPE-01 | Phase 2 | Pending |
| PIPE-02 | Phase 2 | Pending |
| PIPE-03 | Phase 2 | Pending |
| PIPE-04 | Phase 2 | Pending |
| PLAY-01 | Phase 3 | Pending |
| PLAY-02 | Phase 3 | Pending |
| PLAY-03 | Phase 3 | Pending |
| PLAY-04 | Phase 3 | Pending |
| PLAY-05 | Phase 3 | Pending |
| FRAME-01 | Phase 3 | Pending |
| FRAME-02 | Phase 3 | Pending |
| FRAME-03 | Phase 3 | Pending |
| FRAME-04 | Phase 3 | Pending |
| CHART-01 | Phase 4 | Pending |
| CHART-02 | Phase 4 | Pending |
| CHART-03 | Phase 4 | Pending |
| CHART-04 | Phase 4 | Pending |
| COMP-01 | Phase 5 | Pending |
| COMP-02 | Phase 5 | Pending |
| COMP-03 | Phase 5 | Pending |
| COMP-04 | Phase 5 | Pending |
| RPT-01 | Phase 6 | Pending |
| RPT-02 | Phase 6 | Pending |
| RPT-03 | Phase 6 | Pending |
| RPT-04 | Phase 6 | Pending |
| RPT-05 | Phase 6 | Pending |
| RPT-06 | Phase 6 | Pending |
| HIST-01 | Phase 7 | Pending |
| HIST-02 | Phase 7 | Pending |
| HIST-03 | Phase 7 | Pending |
| HIST-04 | Phase 7 | Pending |

**Coverage:**
- v1 requirements: 38 total
- Mapped to phases: 38
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-21*
*Last updated: 2026-04-21 after initial definition*
