---
name: geo-audit
description: Step 4 — 对文章进行产品参数准确性 + trtc.io 内链有效性检查
user_invocable: true
argument: target
---

# /geo-audit — 产品合规审核

检查文章中的产品参数是否准确、trtc.io 内链是否存在且有效。基于 `review-ui/audit-config.json` 中的审核标准。

## 参数

- 无参数：对所有 `status="done"` 的文章批量检查
- `--id P0-01`：只检查指定文章
- `--all`：强制检查所有文章（包括已审核的）

## 前置要求

- `output/articles/*.md` 存在
- `review-ui/audit-config.json` 存在（审核标准配置）
- `review-ui/audit.py` 服务运行中（端口 8766）

## 审核内容

### 1. 产品参数准确性

从 `review-ui/audit-config.json` 中读取审核规则，检查以下关键参数：

| 参数 | 正确值 | 严重级别 |
|------|--------|----------|
| 消息送达率 | >99.99% | error |
| 服务 MAU 规模 | 1 Billion+ | error |
| 日峰值消息量 | 550 Billion+ | error |
| 丢包容忍率 | 60% | error |
| 免费 Plan MAU | 1,000 MAU | error |
| MAU 超出单价 | $0.05/MAU | error |
| Starter Plan 价格 | $69.9/mo（首月） | error |
| UIKit 集成时间 | 10 分钟 | warning |
| 合规认证数量 | 13 个 | warning |
| Standard Plan | $399/mo | warning |
| Pro Plan | $699/mo | warning |

检查逻辑：逐行扫描文章，若发现 `wrong_patterns` 中的值，且同行不含 `correct_values`，则报错。

### 2. trtc.io 内链有效性

- 提取文章中所有 trtc.io 链接（Markdown 格式 + 裸 URL）
- 对每条链接发送 HTTP 请求验证可访问性（timeout: 8s）
- 检查必填链接是否覆盖：
  - `https://trtc.io/products/chat`（必填）
  - `https://trtc.io/pricing/chat`（必填）

### 3. 内链密度

- 最少 2 条 trtc.io 内链（不足则报 error）

## 执行方式

调用本地审核服务：

```
GET http://127.0.0.1:8766/audit?article=output/articles/{slug}.md
```

若审核服务未运行，先启动：

```bash
python3 "PLUGIN_DIR/review-ui/audit.py" --serve --port 8766 &
```

## 输出格式

每篇文章输出审核结果：

```
📄 P0-01-best-chat-sdks-2026.md

  ✅ 产品参数：无错误
  ✅ 内链：3 条，全部有效，必填链接已覆盖

  状态：通过 ✅
```

或：

```
📄 P0-05-best-chat-sdks-free-tier.md

  ❌ 产品参数错误（2 项）：
    - 第 47 行：检测到 "99.9%"，应为 ">99.99%"（消息送达率）
    - 第 112 行：检测到 "$49/mo"，应为 "$69.9/mo"（Starter Plan）

  ⚠️ 产品参数警告（1 项）：
    - 第 88 行：检测到 "5 minutes"，应为 "10 minutes"（UIKit 集成时间）

  ❌ 内链问题（1 项）：
    - 缺少必填内链 "定价页"：https://trtc.io/pricing/chat

  状态：不通过 ❌ → 建议执行 /geo-review 手动标记为「需修改」
```

## 批量检查完成后

```
✅ 审核完成

📊 结果：
- 通过：17 篇
- 有警告：2 篇（可通过）
- 不通过：1 篇（需修改）

下一步：/geo-review — 在审核平台查看详情并处理
```

## 审核配置更新

若产品参数（价格、指标等）发生变化，只需更新 `review-ui/audit-config.json`，无需改代码。
