---
name: indoor-climbing-coach
description: 室内攀岩视频教练分析 skill。当用户提供或指定一段攀岩视频（抱石/运动攀岩/线路攀登）并希望获得技术分析、动作点评或改进建议时立即使用。触发词包括：攀岩、抱石、boulder、climbing、路线、手法、脚法、重心、侧翻、overgrip 等。
---

# 室内攀岩视频教练分析

## 分析模式选择

| 模式 | 触发场景 | 工具 |
|------|---------|------|
| **综合教练分析** | 整体技术点评、路线解析 | `coach.py` |
| **身体部位标注** | 手脚点位精准标注、姿态问题定位 | `climbing_annotate.py` |
| **输出 PPT** | 用户要求幻灯片 | `gen_climbing_ppt.js`（按需生成） |
| **输出 PDF** | 用户要求 PDF 报告 | `gen_climbing_pdf.py`（按需生成） |

---

## 攀岩教练分析框架

复盘时从以下维度分析，也是构建 context 的参考结构：

### 个人技术层面

**脚法**
- 踩点精准度：趾尖是否压在岩点中心，有无滑脚
- 踩点方式：内刃 / 外刃 / 摩擦 / 勾脚 / 下勾
- 用脚承重：是否充分利用脚点减轻手臂负担
- 静音脚：换脚时是否平稳，有无踢踏声

**手法**
- 握持方式：开手 / 半开手 / 扣指 / 捏型 / 抓型
- 锁扣时机：锁扣前重心是否已到位
- 推拉配合：推型（推岩点向外）与拉型配合是否合理
- 过度抓握（Overgrip）：手臂是否提前泵掉

**身体姿态**
- 髋部位置：髋部是否贴近岩壁，有无下沉（Hip Drop）
- 侧翻失衡（Barn Door）：身体是否绕单侧手旋转脱离岩壁
- 旗帜步：是否用旗帜步平衡身体对抗侧翻
- 髋部转动：侧拉 / Layback 动作中髋是否转向岩壁
- 手臂：休息位手臂是否伸直（Lock off 时弯曲正确）

**路线阅读与体能**
- 攀前路线预判：动作序列是否规划合理
- 休息位利用：是否识别并使用无手休息位 / 抖手位
- 体能分配：是否在泵手前提前降级难度或调整动作

### 关键帧问题溯源

对每个问题注明：
- 出现帧号
- 问题部位（左手 / 右脚 / 身体重心等）
- 问题类型（见下表）
- 修正动作

| 问题类型 | 英文标签 | 说明 |
|---------|---------|------|
| 脚法不精准 | `POOR FOOT` | 趾尖偏离岩点，滑脚 |
| 手臂僵直 | `STRAIGHT ARM` | 移动时肘关节锁死 |
| 髋部下沉 | `HIP DROP` | 髋离墙超 30cm，加重手臂负担 |
| 侧翻失衡 | `BARN DOOR` | 身体绕单点旋转脱墙 |
| 过度抓握 | `OVERGRIP` | 握力过大，浪费前臂体能 |
| 髋部不转 | `STIFF HIP` | 侧拉动作中髋未转向岩壁 |
| 路线误判 | `WRONG SEQ` | 选择了非最优动作序列 |
| 漏掉休息位 | `MISSED REST` | 经过休息位未利用 |
| 姿态正确 | `GOOD POS` | 正面标注，绿色圈 |
| 脚法优秀 | `GOOD FOOT` | 静音精准，正面标注 |

---

## 模式一：综合教练分析（coach.py）

### 第一步：收集信息

依次确认：

**1. 视频路径**（未提供时询问）

**2. 分析重点**（展示菜单）：
1. 脚法技术 — 踩点精准度、踩点方式、静音脚
2. 手法技术 — 握持类型、锁扣时机、过度抓握
3. 身体姿态 — 髋部位置、侧翻、旗帜步、手臂
4. 路线阅读 — 动作序列、休息位识别
5. 体能管理 — 泵手节奏、力量分配
6. 综合评估 — 以上全部

**3. 攀登背景**（选填）：
- 难度等级（V0-V10 / 5.8-5.15）
- 经验水平（初学 / 进阶 / 竞技）
- 攀岩类型（抱石 / 运动攀岩 / 传统攀登）
- 目标（备赛 / 突破级别 / 改善弱点）

### 第二步：调用 coach.py

```bash
cd /Users/oopslink/works/codes/oopslink/ai-sports-coach
python3 coach.py --video "<视频路径>" --context "<中文 context>"
```

context 模板：
```
这是一段室内攀岩训练视频（抱石/运动攀岩）。请全程用中文进行专业攀岩教练分析。
重点分析方向：[用户选择]。
攀登者情况：[背景信息]。
请从以下维度给出详细点评：
- 脚法：踩点精准度、方式选择、承重比例
- 手法：握持类型、锁扣时机、过度抓握迹象
- 身体姿态：髋部位置、侧翻预防、手臂使用
- 每个问题注明出现在哪一帧，给出具体修正建议。
```

输出：`output/report_YYYYMMDD_HHMMSS.md`

---

## 模式二：身体部位标注（climbing_annotate.py）

```bash
cd /Users/oopslink/works/codes/oopslink/ai-sports-coach
python3 climbing_annotate.py
```

需先用 `coach.py` 提取帧（`output/frames/` 存在）。

**标注图例：**
- 🔵 蓝圈 + `C1` — 攀岩者身体重心
- 🟢 绿圈 + `L.Hand / R.Hand` — 左/右手接触点
- 🟠 橙圈 + `L.Foot / R.Foot` — 左/右脚接触点
- 🔴 红色警告外圈 — 该部位存在技术问题
- 🟢 绿色外圈 — 该部位动作正确（正面标注）
- 黑底黄字说明文字 — 英文问题描述

输出：`output/climbing_annotated/frame_*.jpg` + `output/climbing_report_*.md`

---

## 模式三/四：PPT / PDF

PPT 按需生成（参考 flag-football-coach 的 `gen_defense_ppt.js` 模式）：

```bash
# pptxgenjs 必须用全局绝对路径
node output/gen_climbing_ppt.js

# PDF 用 reportlab
python3 output/gen_climbing_pdf.py
```

PPT 推荐结构（10-12 页）：
封面 → 攀岩者评分总览 → 脚法专项分析 → 手法专项分析 → 身体姿态分析 → 逐帧标注（每页 2 帧）→ 个人问题汇总 → 训练计划 → 总结

---

## ⚠️ GPT-4o 调用注意事项

与 flag-football 相同的限制：
- **英文 system prompt**（中文会触发拒绝）
- **不能说"识别人物"**，用 "biomechanics analysis"、"body part positions as spatial coordinates"
- **detail=low**（12 帧 detail=high 易被过滤）
- System prompt 开头声明："indoor rock climbing training footage for technique improvement"

---

## 错误处理

| 错误 | 解决方案 |
|------|---------|
| `Video file not found` | 确认路径 |
| `ffmpeg is not installed` | `brew install ffmpeg` |
| `OPENAI_API_KEY is not set` | 项目目录创建 `.env` |
| GPT-4o 拒绝分析图片 | 检查 system prompt 是英文且无"识别人物"字样 |
| PIL 中文乱码 | 标注文字统一用英文 |
| `Cannot find module 'pptxgenjs'` | `require("/opt/homebrew/lib/node_modules/pptxgenjs")` |

---

## 注意事项

- 攀岩视频建议拍摄角度：正面或 45° 侧面，能看到全身和岩点
- 视频时长建议 15-90 秒，单条路线完整攀登效果最佳
- 多条路线请分别运行 coach.py，每条独立分析
- `climbing_annotate.py` 依赖已有的 `output/frames/`
- 抱石分析重视脚法和身体姿态；运动攀岩额外关注体能管理和休息位
