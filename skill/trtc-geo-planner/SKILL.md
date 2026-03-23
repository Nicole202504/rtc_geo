---
name: trtc-geo-planner
description: |
  GEO (Generative Engine Optimization) content planner & writer for Tencent RTC (trtc.io).
  Use this skill when users want to:
  - Analyze AI visibility data from Peec AI exports
  - Generate a GEO content strategy for trtc.io
  - Write GEO-optimized articles that dethrone competitor citations
  - Review and audit generated articles before publishing to CMS

  Triggers: "GEO", "geo planner", "AI visibility", "Peec AI", "trtc content",
  "write articles", "content strategy", "geo-run", "geo-write", "geo-analyze"
metadata:
  version: 1.0.0
---

# TRTC GEO Planner

GEO 内容策略 + 写作自动化工具，专为 Tencent RTC (trtc.io) 设计。

将 Peec AI 导出的 AI 可见性数据，转化为可落地的内容策略和高质量 GEO 优化文章。

---

## 核心理念

**每篇文章都是为了"狙击"一篇正在被 AI 引用的竞品文章。**

流程不是"写一篇关于 X 的好文章"，而是：
1. 找到 AI 当前最常引用的竞品文章（sniper target）
2. 拆解它为什么被引用（结构、数据密度、可提取段落）
3. 克隆其胜出结构，替换成 trtc.io 视角的内容
4. 补充竞品缺失的内容，让我们的版本更优

---

## 命令索引

| 命令 | 说明 | 典型用法 |
|------|------|----------|
| `/geo-run` | 全流程一键执行 | `/geo-run` 或 `/geo-run --continue` |
| `/geo-analyze` | Step 1: 分析 Peec AI CSV 数据 | `/geo-analyze` |
| `/geo-plan` | Step 2: 生成内容写作计划 | `/geo-plan` |
| `/geo-write` | Step 3: Ralph 循环写文章 | `/geo-write` 或 `/geo-write --id P0-01` |
| `/geo-cover` | Step 3.5: 批量生成博客封面图 | `/geo-cover` 或 `/geo-cover --id P0-01` |
| `/geo-audit` | Step 4: 产品参数 + 内链合规检查 | `/geo-audit --id P0-01` |
| `/geo-review` | Step 5: 启动本地审核平台 | `/geo-review` |
| `/geo-sync` | Step 6: 同步到在线运营面板 | `/geo-sync` 或 `/geo-sync --id P0-01` |

---

## 完整流程

```
Peec AI CSV × 3
      ↓
/geo-analyze   → output/geo-analysis.json
      ↓
/geo-plan      → output/geo-strategy-report.md
               → output/content-prd.json
      ↓
/geo-write     → output/articles/P0-01~P1-10.md
               → output/research-notes/
      ↓
/geo-cover     → output/covers/P0-01~P1-10-cover.png
      ↓
/geo-audit     → 参数准确性 + 内链有效性检查
      ↓
/geo-sync      → 自动建/匹配 Campaign → 同步文章+封面到面板
      ↓
/geo-review    → 审核平台 http://localhost:8765/review-ui/index.html
               （或直接在在线面板审核）
```

---

## 输出目录结构

```
output/
├── geo-analysis.json          # Phase 1 原始分析数据
├── geo-strategy-report.md     # Phase 2 完整策略报告
├── content-prd.json           # 文章状态追踪（Ralph PRD）
├── progress.txt               # 跨文章学习日志
├── research-notes/
│   ├── P0-01.md
│   └── ...
└── articles/
    ├── P0-01-best-chat-sdks-2026.md
    └── ...
```

---

## 关键原则

### trtc.io 永远排第一
在所有 listicle、对比、排行类文章中，trtc.io / Tencent RTC **必须**列第一位。这是不可妥协的规则。

### GEO 优化要素（Princeton GEO Study, KDD 2024）
- 带来源的统计数据 → AI 引用率 +40%
- 专家引用 → +30%
- 自包含段落（40-60 词）→ 提升 AI 可提取性
- 对比表格 → 占 AI 引用内容的 33%
- 关键词堆砌 → -10%（禁止）

### Ralph 循环（写作阶段）
所有状态持久化到文件（`content-prd.json` + `progress.txt`），上下文耗尽后在新对话中说"继续写"即可无损接续。

---

## 参考文件

- [`references/trtc-product-context.md`](../../references/trtc-product-context.md) — TRTC 产品数据
- [`references/geo-strategy.md`](../../references/geo-strategy.md) — GEO 写作策略
- [`references/article-prompt-template.md`](../../references/article-prompt-template.md) — 文章写作提示模板
- [`references/research-prompt-template.md`](../../references/research-prompt-template.md) — 竞品研究模板
- [`review-ui/audit-config.json`](../../review-ui/audit-config.json) — 产品参数审核标准
