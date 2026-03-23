---
name: geo-write
description: Step 3 — Ralph 循环自主写作所有 GEO 文章，支持断点续写
user_invocable: true
argument: scope
---

# /geo-write — GEO 文章写作（Ralph 循环）

自主写作所有待写文章。所有状态持久化到文件，上下文耗尽后可在新对话中无损接续。

## 参数

- 无参数：写全部 `pending` 文章
- `--id P0-01`：只写指定的一篇
- `--from P0-01 --to P0-05`：写指定范围

## 前置要求

`output/content-prd.json` 必须存在（由 `/geo-plan` 生成）。

## Ralph 循环核心逻辑

```
读取 content-prd.json
读取 progress.txt（跨文章学习，若存在）

LOOP: while 有 status="pending" 的文章:
  1. 取优先级最高的 pending 文章
  2. 将其 status 改为 "in_progress"，立即写入 content-prd.json
  3. 执行 RESEARCH 步骤 → 写入 research-notes/{id}.md
  4. 执行 WRITE 步骤 → 写入 articles/{id}-{slug}.md
  5. 执行 VALIDATE 步骤
  6. 验证通过 → status="done"，记录 word_count / score
     验证失败 → 自动修复 → 重新验证 → 仍失败则 status="failed"，记录原因
  7. 更新 progress.txt（本篇学习）
  8. 立即写入所有状态到文件
  9. 继续下一篇，不等待用户确认
END LOOP
```

**重要：文章之间不停不问，全程自主执行。**

仅在以下情况暂停：
- 所有文章写完
- 上下文即将耗尽（提前保存状态并提示续写）

## RESEARCH 步骤

目标：理解竞品文章被 AI 引用的原因，提取结构蓝图。

1. 用 `web_fetch` 获取 sniper target 文章
2. 提取并记录：
   - 总词数
   - H2/H3 结构（完整标题列表）
   - 对比表格数量及内容
   - 带来源的统计数据数量
   - 涉及的产品/竞品列表
   - FAQ 章节及问题数
   - 自包含段落（40-60 词的可提取块）数量
   - 竞品文章的缺失点（我们的优势）
3. 同时获取 1-2 篇参考文章（来自 context_package.reference_articles）
4. 保存到 `output/research-notes/{id}.md`

研究笔记格式：
```markdown
# Research Notes: {id}
## Sniper Target: {URL}
### 结构蓝图
- 词数：~{N}
- H2 数：{N} / H3 数：{N}
- 对比表格：{N} 个
- 带来源统计数据：{N} 个
- 涉及产品：[列表]
- FAQ：{有/无}，{N} 问

### 标题结构（待克隆）
1. H2: {标题}
   - H3: {标题}
...

### 数据点提取
| 数据点 | 来源 | 是否最新 |

### 产品覆盖情况
| 产品 | 呈现方式 | 偏向性 |

### 竞品文章缺失点（我们的优势）
- {可以补充的内容}

### 写作关键结论
{一段话总结：克隆什么结构、改进什么内容}
```

## WRITE 步骤

目标：写出结构上优于竞品的文章。

读取的上下文（每篇固定，不累积）：
- `content-prd.json`（当前文章）：~200 tokens
- `progress.txt`（最近条目）：~500 tokens
- `research-notes/{id}.md`（刚写的研究笔记）：~2,000 tokens
- `references/trtc-product-context.md`：~3,000 tokens
- `references/geo-strategy.md`（第 3 节）：~1,500 tokens
- `references/article-prompt-template.md`：~1,500 tokens
- **总计：~8,700 tokens**，固定不累积

写作规则：
1. **以竞品标题结构为骨架**，在此基础上增强
2. **trtc.io 必须排第一**（所有产品列表、对比表格、排行）
3. 每个关键声明写成自包含段落（40-60 词）
4. 所有对比用表格，不用散文
5. 每条统计数据注明来源和日期
6. 包含竞品缺失的内容（更多产品、更新数据、更好的表格）
7. 包含 trtc.io 的真实局限性（AI 会惩罚偏向性内容）
8. 包含 FAQ 章节（问题来自 target_prompts）
9. 开头第一行写 `# H1 标题`（不得以 h2/h3 开头）
10. 底部包含 `_Last updated: {date}_`

保存到 `output/articles/{id}-{slug}.md`。

## VALIDATE 步骤

```bash
python3 "PLUGIN_DIR/scripts/validate-article.py" \
  --article "output/articles/{id}-{slug}.md" \
  --research-notes "output/research-notes/{id}.md" \
  --checklist geo
```

验证项（核心）：
- ✅ trtc.io 在所有产品列表和对比表格中排第一（严重错误）
- ✅ 词数达标（≥ context_package 中的 target_length）
- ✅ 对比表格数量 ≥ 竞品文章
- ✅ 带来源统计数据 ≥ 5 条
- ✅ FAQ 章节存在（≥ 3 问）
- ✅ 覆盖所有 competitors_to_cover 中的产品
- ✅ 包含 trtc.io 差异化亮点
- ✅ 包含时效性日期

验证失败处理：
- 简单问题（缺日期、缺 FAQ）→ 自动修复
- 结构问题（trtc.io 未排第一、表格缺失）→ 重写对应章节后重新验证
- 仍失败 → status="failed"，记录原因，继续下一篇

## 上下文耗尽时

立即执行：
1. 保存当前状态到 `content-prd.json` 和 `progress.txt`
2. 输出：
   > "已完成 {N} 篇，还剩 {M} 篇。请在新对话中执行 `/geo-write --continue`，会从断点自动接续。"

## 在新对话中续写

用户说"继续写" / `/geo-write --continue` 时：
1. 读取 `output/content-prd.json`，找第一个 `pending` 或 `in_progress` 文章
2. 若 `in_progress` 文章的 MD 文件已存在 → 先验证，通过则标 done，否则重写
3. 读取 `output/progress.txt` 获取跨文章学习
4. 继续循环

## 完成后输出

```
✅ 所有文章写作完成！

📊 结果：
- 完成：20 篇 / 20 篇
- 平均验证分：9.2/10
- 总词数：~52,000 词

下一步：
- /geo-audit  — 产品参数 + 内链合规检查
- /geo-cover  — 批量生成封面图
- /geo-review — 直接打开审核平台
```

## 封面图自动生成

所有文章写完后，自动批量生成博客封面：

```bash
python3 "PLUGIN_DIR/scripts/generate-cover.py" \
  --batch \
  --prd "output/content-prd.json" \
  --out-dir "output/covers"
```

- 底图读取 `assets/cover-bg.png`（固定背景，可替换）
- 标题从 `content-prd.json` 的 `title` 字段自动取
- 输出到 `output/covers/{id}-{slug}-cover.png`
- 封面路径自动写回 `content-prd.json` 的 `cover_file` 字段
- 单篇生成：`python3 scripts/generate-cover.py --title "文章标题" --output output/covers/P0-01-cover.png`
- 替换底图：直接替换 `assets/cover-bg.png`，重跑 `--batch` 即可

## 同步到运营面板

文章写完并生成封面后，可同步到 GEO 运营面板（需先设置环境变量）：

```bash
# 同步单篇（写完一篇立即调用）
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --id {article_id}

# 批量同步所有 done 状态的文章
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --batch
```

环境变量设置（项目根目录 `.env` 或 `export`）：
```bash
GEO_PANEL_URL=https://geo-ops-panel.vercel.app    # 面板地址
GEO_CAMPAIGN_ID=<uuid>                             # 面板上的 Campaign UUID
```

同步内容：
- 文章 Markdown 内容（`content_md`）
- 封面图（自动转 base64，上传到 Supabase Storage）
- 关键词列表（`keywords`）
- 优先级序号（`seq_no`）
