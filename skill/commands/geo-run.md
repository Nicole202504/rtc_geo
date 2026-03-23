---
name: geo-run
description: 全流程一键执行 — 从数据分析到文章写作，支持续跑
user_invocable: true
argument: mode
---

# /geo-run — GEO 全流程执行

全流程控制器，按顺序串联所有步骤，支持断点续跑。

## 参数

- 无参数：从 Step 1 执行到 Step 5（需要先提供 3 个 CSV 文件）
- `--continue`：从上次中断处继续（读取 `output/content-prd.json` 恢复状态）
- `--from <step>`：从指定步骤开始（1=分析 / 2=计划 / 3=写作 / 4=审核 / 5=审核平台）
- `--to <step>`：执行到指定步骤

示例：
- `/geo-run` — 完整跑一遍
- `/geo-run --continue` — 续写未完成的文章
- `/geo-run --from 3` — 跳过分析，直接开始写作
- `/geo-run --from 3 --to 3` — 只执行写作步骤

## 步骤映射

| Step | 名称 | 对应命令 | 主要输出 |
|------|------|----------|----------|
| 1 | 数据分析 | `/geo-analyze` | `output/geo-analysis.json` |
| 2 | 策略规划 | `/geo-plan` | `output/geo-strategy-report.md` + `content-prd.json` |
| 3 | 文章写作 | `/geo-write` | `output/articles/*.md` |
| 4 | 合规审核 | `/geo-audit` | 审核报告（嵌入 content-prd.json） |
| 5 | 审核平台 | `/geo-review` | 打开 http://localhost:8765/review-ui/index.html |

## 执行逻辑

### 1. 读取状态

检查 `output/content-prd.json` 是否存在：
- 不存在 → 从 Step 1 开始
- 存在且有 `pending` 文章 → 询问是否 `--continue`
- 存在且全部 `done` → 提示已完成，可以直接 `/geo-review`

### 2. 前置检查

| Step | 需要的前置文件 |
|------|--------------|
| 1 | 3 个 Peec AI CSV 文件（用户提供） |
| 2 | `output/geo-analysis.json` |
| 3 | `output/content-prd.json` |
| 4 | `output/articles/*.md` |
| 5 | 任意（直接启动服务器） |

### 3. 逐步执行

按步骤顺序执行各命令的逻辑，每步完成后更新进度，失败则停止并提示。

## --continue 逻辑

```
读取 output/content-prd.json
找到第一个 status="pending" 或 status="in_progress" 的文章
读取 output/progress.txt（跨文章学习）
直接跳到 /geo-write 继续写
```

## 完成后输出

```
🎉 GEO 全流程完成！

📊 执行结果：
- 文章总数：20 篇（P0: 10 篇 / P1: 10 篇）
- 全部通过验证：✅
- 总词数：约 52,000 词

📁 输出目录：output/
🌐 审核平台：http://localhost:8765/review-ui/index.html
```
