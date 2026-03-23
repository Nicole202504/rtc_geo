---
name: geo-cover
description: Step 3.5 — 为所有文章批量生成博客封面图（380×200，左侧标题+右侧场景图）
user_invocable: true
argument: target
---

# /geo-cover — 博客封面生成

基于固定底图模板，自动为每篇文章生成封面图。3 倍超采样渲染，文字清晰锐利。

## 参数

- 无参数：批量生成所有文章的封面（读 `content-prd.json`）
- `--id P0-01`：只生成指定文章的封面
- `--bg <path>`：指定底图路径（默认 `assets/cover-bg.png`）
- `--out-dir <path>`：指定输出目录（默认 `output/covers/`）

示例：
- `/geo-cover` — 批量生成全部封面
- `/geo-cover --id P0-01` — 只生成 P0-01 的封面
- `/geo-cover --bg assets/cover-bg-v2.png` — 换底图重新批量生成

## 前置要求

- `assets/cover-bg.png` 存在（默认底图）
- `output/content-prd.json` 存在（批量模式）
- 已安装 Pillow：`pip3 install Pillow`

## 执行命令

**批量模式（全部文章）：**

```bash
python3 "PLUGIN_DIR/scripts/generate-cover.py" \
  --batch \
  --prd "output/content-prd.json" \
  --out-dir "output/covers"
```

**单篇模式：**

```bash
python3 "PLUGIN_DIR/scripts/generate-cover.py" \
  --title "<文章标题>" \
  --bg "PLUGIN_DIR/assets/cover-bg.png" \
  --output "output/covers/<id>-cover.png"
```

单篇模式时，从 `content-prd.json` 中读取对应 id 的 `title` 字段作为标题。

## 封面规格

| 参数 | 值 |
|------|----|
| 输出尺寸 | 380 × 200 px |
| 渲染方式 | 3 倍超采样后缩回（清晰度高） |
| 左侧区域 | 深蓝渐变 + 弧形右边缘 |
| 文字 | 白色粗体，左上区域，自动换行 |
| 右侧区域 | 底图场景图（保持原样） |

## 输出

- 封面图保存到 `output/covers/{id}-{slug}-cover.png`
- 封面路径自动写回 `content-prd.json` 的 `cover_file` 字段

## 替换底图

只需替换 `assets/cover-bg.png`，重跑 `/geo-cover` 即可批量更新全部封面。
底图要求：380×200 px，PNG 格式，RGBA 模式。

## 完成后输出

```
🖼️  批量生成封面（共 20 篇）
────────────────────────────
  ✅ P0-01  →  P0-01-best-chat-sdks-2026-cover.png
  ✅ P0-02  →  P0-02-in-app-chat-apis-sdks-reviewed-cover.png
  ...
────────────────────────────
✅ 完成：20 张成功，0 张失败
📁 输出目录：output/covers/
   cover_file 路径已写入 content-prd.json

下一步：/geo-audit 或 /geo-review
```

## 同步到运营面板

封面生成完毕后，若需同步文章 + 封面到在线运营面板：

```bash
# 批量同步（文章 + 封面一起上传）
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --batch

# 单篇同步
python3 "PLUGIN_DIR/scripts/sync-to-panel.py" --id P0-01
```

前置条件：
- 已在 `.env` 或环境变量中设置 `GEO_PANEL_URL` 和 `GEO_CAMPAIGN_ID`
- 面板已在 Vercel 部署（或本地 `npm run dev` 运行）
- Supabase Storage 中已创建 `article-covers` bucket（设为 public）

同步后，封面自动上传到 Supabase Storage，URL 写入文章记录的 `cover_image_url` 字段，审核台可直接预览封面图。
