# TRTC GEO Planner — Skill

GEO 内容生产 Skill，配合 **geo-ops-panel** 在线运营面板使用。

## 安装（只做一次）

**1. 拉代码**

```bash
git clone git@github.com:Nicole202504/rtc_skill.git
cd rtc_skill
```

**2. 把命令注册到 Claude Code**

```bash
# 创建软链接，让 Claude Code 能识别 /geo-* 命令
ln -sf "$(pwd)/commands/geo-"*.md ~/.claude/commands/
```

**3. 重新开一个新对话**

Claude Code 重新加载后，`/geo-run` 等命令即可使用。

---

## 使用

准备好 3 个 Peec AI CSV 文件后，直接说：

```
/geo-run
```

全程自动执行，写完每篇文章实时同步到面板。

---

## 命令一览

| 命令 | 说明 |
|------|------|
| `/geo-run` | 全流程一键执行 |
| `/geo-analyze` | Step 1: 分析 Peec AI CSV 数据 |
| `/geo-plan` | Step 2: 生成写作计划 + 面板自动建 Campaign |
| `/geo-write` | Step 3: 写文章，每篇完成自动同步到面板 |
| `/geo-cover` | Step 4: 批量生成封面图，自动更新到面板 |
| `/geo-audit` | Step 5: 产品参数 + 内链合规检查 |
| `/geo-sync` | Step 6: 手动补同步（查漏补缺） |
| `/geo-review` | Step 7: 启动本地审核平台 |

---

## 在线审核面板

写作过程中可实时在面板查看进度：

🌐 **https://geo-ops-panel.vercel.app**
- 账号：`rtc2026`
- 密码：`rtc2026`
