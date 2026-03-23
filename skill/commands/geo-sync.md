---
name: geo-sync
description: Step 6 — 一键将文章 + 封面同步到 GEO 运营面板，自动管理 Campaign
user_invocable: true
argument: scope
---

# /geo-sync — 同步到运营面板

将本地生成的文章和封面图一键同步到在线运营面板，供团队在线审核和发布。
**无需任何配置，拉下代码直接跑。**

## 参数

- 无参数：批量同步所有 `done` 状态的文章
- `--id P0-01`：只同步指定一篇
- `--new-campaign`：强制新建 Campaign（用于新一轮内容批次）

示例：
- `/geo-sync` — 批量同步全部完成文章
- `/geo-sync --id P0-01` — 只同步 P0-01
- `/geo-sync --new-campaign` — 开始新一批内容，新建 Campaign

## 前置要求

- `output/content-prd.json` 存在且有 `done` 状态的文章
- 无需其他配置，面板地址已内置

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

## 执行命令

**批量同步（无需任何参数）：**

```bash
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --batch
```

**单篇同步：**

```bash
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --id {article_id}
```

**新一轮内容，强制建新 Campaign：**

```bash
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --batch --new-campaign
```

## 同步内容

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

🔄 批量同步 20 篇文章
────────────────────────────────────────
  📄 P0-01  ✅  Best Chat SDKs for Mobile Apps in 2026
  📄 P0-02  ✅  In-App Chat APIs & SDKs Reviewed
  ...
────────────────────────────────────────
📤 发送 20 篇到面板...

✅ 同步完成！20 篇已上传

🌐 前往面板审核：https://geo-ops-panel.vercel.app
   账号：rtc2026  密码：rtc2026
```

## 下一步

打开面板审核：**https://geo-ops-panel.vercel.app**
- 账号：`rtc2026`
- 密码：`rtc2026`
