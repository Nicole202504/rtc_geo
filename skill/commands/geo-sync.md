---
name: geo-sync
description: Step 6 — 一键将文章 + 封面同步到 GEO 运营面板，自动管理 Campaign
user_invocable: true
argument: scope
---

# /geo-sync — 同步到运营面板

将本地生成的文章和封面图一键同步到在线运营面板（geo-ops-panel），
供团队在线审核和发布。**无需手动建 Campaign，全自动管理。**

## 参数

- 无参数：批量同步所有 `done` 状态的文章
- `--id P0-01`：只同步指定一篇
- `--new-campaign`：强制新建 Campaign（用于新一轮内容批次）
- `--panel-url <url>`：临时指定面板地址（优先级高于 .env）

示例：
- `/geo-sync` — 批量同步全部完成文章
- `/geo-sync --id P0-01` — 只同步 P0-01
- `/geo-sync --new-campaign` — 开始新一批内容，新建 Campaign

## 前置要求

- `output/content-prd.json` 存在且有 `done` 状态的文章
- 面板服务正在运行（本地或 Vercel）

## 首次运行自动配置

**运营同学什么都不用手动配置。** `/geo-sync` 在执行前会自动检测环境：

```
检测到 .env 不存在 / GEO_PANEL_URL 未设置
   ↓
询问用户：面板是本地还是线上？
   ├─ 本地  → 自动写入 GEO_PANEL_URL=http://localhost:3001
   └─ 线上  → 自动写入 GEO_PANEL_URL=https://geo-ops-panel.vercel.app
   ↓
.env 文件自动创建完成，继续同步
```

执行逻辑：

1. 检查项目根目录是否存在 `.env` 且包含 `GEO_PANEL_URL`
2. 如果不存在，询问用户：「面板跑在本地还是线上 Vercel？」
   - 回答「本地」→ 写入 `GEO_PANEL_URL=http://localhost:3001`
   - 回答「线上」→ 写入 `GEO_PANEL_URL=https://geo-ops-panel.vercel.app`
3. 写入 `.env` 后继续执行同步

> `GEO_CAMPAIGN_ID` **不需要手动填写**，脚本会自动管理。

## 自动 Campaign 管理逻辑

```
运行 /geo-sync
   ↓
读取 content-prd.json 中的项目名称
   ↓
检查 .env 是否已有 GEO_CAMPAIGN_ID
   ├─ 有 → 直接用（跳过查询）
   └─ 没有 → 去面板查找同名 Campaign
              ├─ 找到 → 复用，ID 写入 .env
              └─ 没找到 → 自动新建，ID 写入 .env
   ↓
同步文章 + 封面到该 Campaign
```

## 执行步骤

### Step 1：检查并自动配置 .env

```python
# 伪代码：Claude 执行的逻辑
env_path = os.path.join(PLUGIN_ROOT, ".env")
if not os.path.isfile(env_path) or "GEO_PANEL_URL" not in open(env_path).read():
    # 询问用户
    ask: "面板跑在哪里？"
    options:
      - "本地（http://localhost:3001）"
      - "线上 Vercel（https://geo-ops-panel.vercel.app）"
    # 根据回答写入 .env
    write GEO_PANEL_URL=<选择的地址> to .env
```

实际执行：**在运行脚本之前，Claude 先检查 `.env`，如果缺少 `GEO_PANEL_URL`，主动询问用户面板地址（本地 / 线上），然后用 Write 工具写入 `.env`。**

### Step 2：批量同步

```bash
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --batch
```

### Step 3（单篇）：

```bash
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --id {article_id}
```

### Step 4（新一轮内容强制建新 Campaign）：

```bash
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --batch --new-campaign
```

## 同步内容

每篇文章同步以下字段到面板：

| 字段 | 来源 |
|------|------|
| 标题 | `content-prd.json` → `title` |
| 正文 Markdown | `output/articles/{id}-{slug}.md` |
| 关键词列表 | `context_package.target_prompts` |
| 封面图 | `output/covers/{id}-{slug}-cover.png` → 上传到 Supabase Storage |
| 优先级序号 | `priority` 字段 |

文章同步后状态自动设为 `reviewing`，可在面板审核台审阅。

## 完成后输出

```
🚀 GEO 面板同步
   面板地址：https://geo-ops-panel.vercel.app
   🆕 未找到同名 Campaign，自动新建「TRTC GEO 2026」...
   ✅ Campaign 已创建：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Campaign：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

🔄 批量同步 20 篇文章
────────────────────────────────────────
  📄 P0-01  ✅  Best Chat SDKs for Mobile Apps in 2026
  📄 P0-02  ✅  In-App Chat APIs & SDKs Reviewed
  ...
────────────────────────────────────────
📤 发送 20 篇到面板...

✅ 同步完成！20 篇已上传

🌐 前往面板审核：https://geo-ops-panel.vercel.app
```

## 下一步

同步完成后，通知团队在面板审核：
- 面板地址：`GEO_PANEL_URL` 中配置的地址
- 审核台：点击文章 → 预览 → 通过 / 驳回 / 备注
