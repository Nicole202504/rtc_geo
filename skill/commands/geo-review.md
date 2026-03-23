---
name: geo-review
description: Step 5 — 启动本地运营审核平台，支持逐篇审阅、标注和 CMS 导入
user_invocable: true
argument: none
---

# /geo-review — 运营审核平台

启动本地 Web 审核平台，供运营人员逐篇审阅文章、标注审核状态、一键检查产品合规，并将审核通过的文章导入 CMS。

## 执行步骤

### 1. 启动审核后端服务（端口 8766）

```bash
python3 "PLUGIN_DIR/review-ui/audit.py" --serve --port 8766 &
```

若端口已占用，跳过此步。

### 2. 启动静态文件服务（端口 8765）

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory "<project-root>"
```

`project-root` = `plugin.json` 所在目录。

若端口已占用，跳过此步。

### 3. 打开浏览器

```bash
open http://localhost:8765/review-ui/index.html      # macOS
xdg-open http://localhost:8765/review-ui/index.html  # Linux
```

### 4. 告知用户

```
✅ 审核平台已启动！

🌐 http://localhost:8765/review-ui/index.html

使用方式：
📋 列表 Tab — 逐篇审阅文章，左侧点击选择，右侧审核操作
  - 「通过发布 ✓」→ 解锁 CMS 导入功能
  - 「需修改 ✎」→ 填写修改意见并保存
  - 「一键检查参数 & 内链」→ 触发产品合规审核

📊 总览 Tab — 查看整体进度、KPI、词数统计

📈 策略报告 Tab — 查看 GEO 分析、竞品域名排行、Prompt 覆盖矩阵
```

## 审核平台功能说明

### 文章列表（左侧边栏）
- 按状态筛选：全部 / 待审核 / 通过 / 需修改 / 拒绝
- 显示每篇文章的优先级评分、词数、GEO 分数
- 状态用彩色徽章标注

### 文章详情（中间主区域）
- 完整 Markdown 渲染
- 滚动阅读

### 审核面板（右侧）
- **状态操作**：通过发布 / 需修改 / 拒绝
- **审核备注**：填写修改意见
- **一键检查参数 & 内链**：调用 audit.py 服务，结果实时展示
  - 红色高亮显示错误行
  - 「↩ 标记为需修改」按钮自动填入错误摘要
- **导入 CMS**（仅审核通过后解锁）：
  - 自动填充 route_name（从文件名生成 slug）
  - 高级配置：language / category / author / SEO title / SEO desc / labels / 发布时间
  - 点击「🚀 导入到 CMS」通过代理转发到 CMS API

### 总览 Tab
- KPI 卡片：总词数、平均分、通过率、需修改数
- 状态分布饼图
- 文章词数排行

### 策略报告 Tab
- 数据总览（来自 geo-analysis.json）
- 竞品域名引用排行
- Prompt 覆盖矩阵
- 策略报告全文（来自 geo-strategy-report.md）
- 写作日志（来自 progress.txt）

## 审核状态说明

| 状态 | 说明 | 下一步 |
|------|------|--------|
| `pending` | 待审核 | 阅读文章后操作 |
| `approved` | 通过发布 | 可导入 CMS |
| `revision` | 需修改 | 修改后重新审核 |
| `rejected` | 拒绝 | 归档或重写 |

审核状态保存在浏览器 `localStorage`，刷新页面不丢失。

## 一键启动脚本

也可以直接运行：

```bash
bash "PLUGIN_DIR/review-ui/start.sh"
```
