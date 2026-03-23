# TRTC GEO Planner — Skill

GEO 内容生产 Skill，配合 **geo-ops-panel** 在线运营面板使用。

## 使用方式

将整个 `skill/` 目录放到你的 Claude Code Skill 目录下，即可使用以下命令。

## 命令一览

| 命令 | 说明 |
|------|------|
| `/geo-run` | 全流程一键执行 |
| `/geo-analyze` | Step 1: 分析 Peec AI CSV 数据 |
| `/geo-plan` | Step 2: 生成内容写作计划 |
| `/geo-write` | Step 3: Ralph 循环写文章 |
| `/geo-cover` | Step 3.5: 批量生成博客封面图 |
| `/geo-audit` | Step 4: 产品参数 + 内链合规检查 |
| `/geo-review` | Step 5: 启动本地审核平台 |
| `/geo-sync` | Step 6: 同步到在线运营面板（自动配置，无需手动建 Campaign） |

## 连接到运营面板

运行 `/geo-sync` 时，Skill 会自动：
1. 检测是否配置了面板地址，**没有则引导你填写（一句话）**
2. 在面板上查找或新建 Campaign
3. 批量上传文章 + 封面图

**运营同学只需要说 `/geo-sync`，其他全自动。**
