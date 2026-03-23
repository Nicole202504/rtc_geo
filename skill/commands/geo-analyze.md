---
name: geo-analyze
description: Step 1 — 分析 Peec AI 导出的 3 个 CSV，生成 geo-analysis.json
user_invocable: true
argument: csv_paths
---

# /geo-analyze — Peec AI 数据分析

读取用户提供的 3 个 Peec AI CSV 文件，运行分析脚本，输出结构化的 AI 可见性报告。

## 前置要求

用户必须提供 **3 个 CSV 文件**（Peec AI 导出）：

| 文件 | 必填列 | 说明 |
|------|--------|------|
| **Prompts CSV** | `prompt`, `position`, `visibility`, `volume`, `tags` | AI 搜索词追踪数据 |
| **Source Domains CSV** | `Domain`, `Type`, `Used`, `Avg. Citations` | 被 AI 引用的域名 |
| **Source URLs CSV** | `URL`, `Title`, `Type`, `Mentioned`, `Used total`, `Avg. Citations` | 被 AI 引用的具体 URL |

**如果缺少任意一个文件，立即停止，告知用户缺少哪个，并说明该文件的格式要求。**

每次运行必须使用最新导出的 CSV。如果用户说"用上次的"，提醒：
> "Peec AI 数据变化很快，请提供最新导出的 3 个 CSV 文件，这样分析结果才准确。"

## 执行步骤

### 1. 确认文件路径

用户提供文件路径后，验证 3 个文件都存在且可读。

### 2. 运行分析脚本

```bash
python3 "PLUGIN_DIR/scripts/analyze.py" \
  --prompts "<path-to-prompts-csv>" \
  --domains "<path-to-domains-csv>" \
  --urls "<path-to-urls-csv>" \
  --brand "trtc.io" \
  --output "output/geo-analysis.json"
```

`PLUGIN_DIR` = plugin 根目录（`plugin.json` 所在目录）。

### 3. 脚本失败时手动分析

若脚本报错，手动执行以下分析逻辑：

**Prompt 分析：**
- 分为两组：trtc.io 有排名 vs. 排名为 "-"（缺席）
- 缺席的 prompt = 可见性缺口，最高优先级
- 有排名但 visibility 低 = 提升机会
- 从 `tags` 列判断 intent（informational / transactional）
- transactional prompt 优先级权重 ×1.5

**博客机会识别：**
- 从 source-urls CSV 筛选 `Type` in [Listicle, Comparison, How-To Guide, Article, Alternative]
- 按 `Used total` 降序排列
- 交叉比对 `Mentioned` 列：若 trtc.io 未被提及 = 缺口
- 机会评分 = `Used total × Avg.Citations × intent_weight`

**社区机会识别：**
- 从 source-domains CSV 筛选 `Type` = UGC（reddit, dev.to, medium, github, stackoverflow 等）
- 找到引用频次最高的社区 URL
- 识别来源社区/版块

### 4. 输出

保存到 `output/geo-analysis.json`，结构：
```json
{
  "summary": {
    "presence_rate": "48%",
    "absent_prompts": 13,
    "blog_opportunities": 241
  },
  "prompt_analysis": [...],
  "blog_opportunities": [...],
  "community_opportunities": [...],
  "quick_wins": [...]
}
```

分析完成后输出摘要，并提示下一步：
```
✅ 数据分析完成

📊 摘要：
- 当前 AI 可见率：48%（13 个 prompt 完全缺席）
- 识别博客机会：241 个
- 社区机会：XX 个

下一步：/geo-plan（生成内容策略报告）
```
