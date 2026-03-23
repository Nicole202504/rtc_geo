---
name: geo-plan
description: Step 2 — 基于分析数据生成 GEO 策略报告和文章写作计划 content-prd.json
user_invocable: true
argument: none
---

# /geo-plan — GEO 策略规划

读取 `output/geo-analysis.json`，生成完整的 GEO 策略报告和 Ralph-style 文章写作计划。

## 前置要求

`output/geo-analysis.json` 必须存在（由 `/geo-analyze` 生成）。

## 执行步骤

### 1. 生成策略报告

输出 Markdown 策略报告，保存到 `output/geo-strategy-report.md`，包含：

**Part A：博客文章行动清单（按优先级排列）**

每条格式如下：

```markdown
### [P0-01] 建议文章标题

**优先级评分：** XX/100
**Sniper Target：** [竞品文章 URL]
**目标被引次数：** XX 次

#### 为什么 AI 引用这篇竞品文章
- 结构分析：H2/H3 层级、章节数
- 数据密度：统计数据数量、表格数量
- 可提取性：自包含段落数量
- 覆盖广度：涉及产品数量
- 时效性信号：标题含年份、"Updated XXXX"

#### 目标 Prompts
| Prompt | 当前排名 | 当前可见性 | 意图 |

#### 内容蓝图
- 内容类型：[Listicle / Comparison / How-To 等]
- 目标词数：2000-3000
- 建议标题：[SEO + GEO 优化的标题]
- 需要覆盖的竞品：[列表]
- trtc.io 差异化亮点：[具体数据点]

#### GEO 优化要求
- [ ] 至少 5 条带来源的统计数据
- [ ] 对比表格（不少于竞品数量）
- [ ] FAQ 章节（≥3 问）
- [ ] 自包含答案段落（40-60 词）
- [ ] 包含 "Last updated: [日期]"

#### 写作上下文包（Context Package）
\`\`\`json
{
  "id": "P0-01",
  "task": "写一篇 GEO 优化的博客文章",
  "sniper_target": "竞品 URL",
  "target_prompts": [...],
  "content_type": "Listicle",
  "competitors_to_cover": [...],
  "trtc_advantages": [...],
  "target_length": "2000-3000 词"
}
\`\`\`
```

**Part B：社区内容行动清单**（同上格式，平台为 Reddit/dev.to/Medium 等）

**Part C：快速见效项**（<1 天可完成的操作）

### 2. 生成 content-prd.json

运行脚本：

```bash
python3 "PLUGIN_DIR/scripts/generate-content-prd.py" \
  --report "output/geo-strategy-report.md" \
  --output "output/content-prd.json"
```

若脚本失败，手动从策略报告的 P0-xx / P1-xx 行动清单提取，生成格式：

```json
{
  "project": "trtc-geo-content",
  "created": "2026-03-17",
  "stories": [
    {
      "id": "P0-01",
      "title": "文章标题",
      "priority": 1,
      "status": "pending",
      "sniper_target": "https://...",
      "target_citations": 107,
      "output_file": "articles/P0-01-slug.md",
      "research_file": "research-notes/P0-01.md",
      "context_package": { ... }
    }
  ]
}
```

status 初始值全部为 `"pending"`。

### 3. 输出摘要

```
✅ 策略规划完成

📋 写作计划：
- P0 优先级文章：10 篇
- P1 优先级文章：10 篇
- 社区内容：5 篇
- 快速见效项：X 个

📁 输出文件：
- output/geo-strategy-report.md
- output/content-prd.json

下一步：/geo-write（开始写文章）
```
