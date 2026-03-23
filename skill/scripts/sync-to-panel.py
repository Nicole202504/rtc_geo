#!/usr/bin/env python3
"""
sync-to-panel.py — 将本地生成的文章同步到 GEO 运营面板（Supabase）

核心能力：
  - 自动从 content-prd.json 读取项目名，在面板上匹配或新建 Campaign
  - Campaign ID 自动写回 .env，下次无需重复操作
  - 同步文章 Markdown + 封面图（base64 → Supabase Storage）

用法：
  python3 scripts/sync-to-panel.py --batch           # 批量同步所有 done 文章
  python3 scripts/sync-to-panel.py --id P0-01        # 同步单篇
  python3 scripts/sync-to-panel.py --batch --new-campaign  # 强制新建 Campaign

环境变量（项目根目录 .env 或直接 export）：
  GEO_PANEL_URL   面板地址，如 https://geo-ops-panel.vercel.app
                  （GEO_CAMPAIGN_ID 会自动管理，无需手动设置）
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(SCRIPT_DIR)
PRD_PATH    = os.path.join(PLUGIN_ROOT, "output", "content-prd.json")
COVERS_DIR  = os.path.join(PLUGIN_ROOT, "output", "covers")
ENV_PATH    = os.path.join(PLUGIN_ROOT, ".env")


# ──────────────────────────────────────────────
# 环境变量 / .env 读写
# ──────────────────────────────────────────────

def load_env():
    """读取 .env 文件（如果存在）"""
    if os.path.isfile(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def save_env_key(key: str, value: str):
    """将 key=value 写入 .env（已有则更新，没有则追加）"""
    lines = []
    found = False
    if os.path.isfile(ENV_PATH):
        with open(ENV_PATH) as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if re.match(rf"^{key}\s*=", line):
                lines[i] = f"{key}={value}\n"
                found = True
                break
    if not found:
        lines.append(f"{key}={value}\n")
    with open(ENV_PATH, "w") as f:
        f.writelines(lines)


def get_panel_url():
    url = os.environ.get("GEO_PANEL_URL", "").rstrip("/")
    if not url:
        print("❌ 未设置 GEO_PANEL_URL")
        print("   在项目根目录创建 .env 文件，写入：")
        print("   GEO_PANEL_URL=https://geo-ops-panel.vercel.app")
        print("   （本地调试用 http://localhost:3001）")
        sys.exit(1)
    return url


# ──────────────────────────────────────────────
# HTTP 工具
# ──────────────────────────────────────────────

def http_get(url: str) -> dict | None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "geo-skill-sync/1.0"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ❌ GET {url} 失败: {e}")
        return None


def http_post(url: str, payload: dict) -> dict | None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent":   "geo-skill-sync/1.0",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ❌ HTTP {e.code}: {body[:300]}")
        return None
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return None


# ──────────────────────────────────────────────
# Campaign 自动管理
# ──────────────────────────────────────────────

def get_or_create_campaign(panel_url: str, prd: dict, force_new: bool = False) -> str:
    """
    自动管理 Campaign：
    1. 优先从 .env 读取已保存的 GEO_CAMPAIGN_ID
    2. 没有则去面板查找同名 Campaign
    3. 找不到则自动新建
    4. 最终将 ID 写回 .env

    返回 campaign_id（str）
    """
    # 从 prd 提取项目名称，用于 Campaign name
    project_name = prd.get("project", {}).get("name", "") \
                   or prd.get("title", "") \
                   or "TRTC GEO Campaign"
    topic = prd.get("project", {}).get("target_topic", "") \
            or prd.get("topic", "") \
            or ""

    # 1. 已有保存的 ID 且不强制新建 → 直接用
    saved_id = os.environ.get("GEO_CAMPAIGN_ID", "").strip()
    if saved_id and not force_new:
        print(f"  📌 使用已保存的 Campaign ID：{saved_id}")
        return saved_id

    print(f"  🔍 在面板查找 Campaign：「{project_name}」...")

    # 2. 拉取面板所有 Campaign，按名字匹配
    result = http_get(f"{panel_url}/api/campaigns")
    if result and result.get("data"):
        for c in result["data"]:
            if c.get("name", "").strip() == project_name.strip():
                cid = c["id"]
                print(f"  ✅ 找到已有 Campaign：{cid}")
                save_env_key("GEO_CAMPAIGN_ID", cid)
                os.environ["GEO_CAMPAIGN_ID"] = cid
                return cid

    # 3. 没找到 → 新建
    print(f"  🆕 未找到同名 Campaign，自动新建「{project_name}」...")
    stories = prd.get("stories", [])
    create_result = http_post(f"{panel_url}/api/campaigns", {
        "name":         project_name,
        "description":  f"GEO 内容批次，来自本地 Skill 自动同步",
        "target_topic": topic,
        "target_count": len([s for s in stories if s.get("type") == "blog"]),
        "language":     "English",
        "status":       "draft",
    })
    if not create_result or not create_result.get("data"):
        print("  ❌ 新建 Campaign 失败")
        sys.exit(1)

    cid = create_result["data"]["id"]
    print(f"  ✅ Campaign 已创建：{cid}")
    save_env_key("GEO_CAMPAIGN_ID", cid)
    os.environ["GEO_CAMPAIGN_ID"] = cid
    return cid


# ──────────────────────────────────────────────
# 文章 / 封面读取
# ──────────────────────────────────────────────

def read_article_md(story: dict) -> str | None:
    """读取文章 Markdown 内容"""
    out_file = story.get("output_file", "")
    if not out_file:
        return None
    path = os.path.join(PLUGIN_ROOT, "output", os.path.basename(out_file))
    if not os.path.isfile(path):
        path = os.path.join(PLUGIN_ROOT, out_file)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


def read_cover_base64(story: dict) -> str | None:
    """读取封面图，转为 base64 data URI"""
    cover_file = story.get("cover_file", "")
    if cover_file and os.path.isfile(cover_file):
        with open(cover_file, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()

    out_file = story.get("output_file", "")
    if out_file:
        slug = os.path.basename(out_file).replace(".md", "")
        cover_path = os.path.join(COVERS_DIR, f"{slug}-cover.png")
        if os.path.isfile(cover_path):
            with open(cover_path, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return None


def build_article_payload(story: dict) -> dict | None:
    """把一个 story 转成 webhook 请求体中的文章对象"""
    content_md = read_article_md(story)
    if not content_md:
        print(f"  ⚠️  {story['id']} 找不到文章文件，跳过")
        return None

    cover_b64 = read_cover_base64(story)
    ctx       = story.get("context_package", {})
    keywords  = ctx.get("target_prompts", [])

    return {
        "seq_no":          story.get("priority", 0),
        "article_id":      story.get("id"),
        "title":           story.get("title", ""),
        "content_md":      content_md,
        "keywords":        keywords,
        "cover_image_b64": cover_b64,
    }


# ──────────────────────────────────────────────
# 同步逻辑
# ──────────────────────────────────────────────

def sync_single(story_id: str, panel_url: str, campaign_id: str):
    """同步单篇文章"""
    with open(PRD_PATH, encoding="utf-8") as f:
        prd = json.load(f)

    story = next((s for s in prd["stories"] if s["id"] == story_id), None)
    if not story:
        print(f"❌ 找不到文章 {story_id}")
        sys.exit(1)

    print(f"🔄 同步文章：{story_id} — {story.get('title', '')}")
    payload = build_article_payload(story)
    if not payload:
        sys.exit(1)

    result = http_post(f"{panel_url}/api/webhook/article-ready", {
        "campaign_id": campaign_id,
        "articles":    [payload],
    })
    if result and result.get("ok"):
        print(f"  ✅ 已同步到面板 Campaign {campaign_id}")
    else:
        print(f"  ❌ 同步失败")
        sys.exit(1)


def sync_batch(panel_url: str, campaign_id: str, status_filter: list = None):
    """批量同步所有指定状态的文章"""
    if status_filter is None:
        status_filter = ["done"]

    with open(PRD_PATH, encoding="utf-8") as f:
        prd = json.load(f)

    targets = [
        s for s in prd["stories"]
        if s.get("status") in status_filter and s.get("type") == "blog"
    ]
    if not targets:
        print(f"⚠️  没有符合条件的文章（status in {status_filter}）")
        return

    print(f"\n🔄 批量同步 {len(targets)} 篇文章\n{'─'*40}")

    articles = []
    skipped  = 0
    for story in targets:
        payload = build_article_payload(story)
        if payload:
            articles.append(payload)
            has_cover = "✅" if payload.get("cover_image_b64") else "⚠️ 无封面"
            print(f"  📄 {story['id']}  {has_cover}  {story.get('title', '')[:50]}")
        else:
            skipped += 1

    if not articles:
        print("❌ 没有可同步的文章（文件缺失）")
        return

    print(f"\n{'─'*40}")
    print(f"📤 发送 {len(articles)} 篇到面板...")

    result = http_post(f"{panel_url}/api/webhook/article-ready", {
        "campaign_id": campaign_id,
        "articles":    articles,
    })
    if result and result.get("ok"):
        print(f"\n✅ 同步完成！{len(articles)} 篇已上传")
        if skipped:
            print(f"⚠️  {skipped} 篇因文件缺失跳过")
        print(f"\n🌐 前往面板审核：{panel_url}")
    else:
        print("❌ 同步失败，请检查面板服务是否正常")
        sys.exit(1)


# ──────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────

def main():
    load_env()
    parser = argparse.ArgumentParser(description="同步 GEO 文章到运营面板（自动管理 Campaign）")
    parser.add_argument("--id",           help="同步单篇文章，如 P0-01")
    parser.add_argument("--batch",        action="store_true", help="批量同步所有 done 文章")
    parser.add_argument("--new-campaign", action="store_true", help="强制新建 Campaign（忽略已保存的 ID）")
    parser.add_argument("--panel-url",    help="面板地址（也可通过 GEO_PANEL_URL 环境变量设置）")
    parser.add_argument("--status",       default="done", help="同步哪些状态的文章（默认 done）")
    args = parser.parse_args()

    if args.panel_url:
        os.environ["GEO_PANEL_URL"] = args.panel_url

    panel_url = get_panel_url()

    # 读取 PRD，自动获取或创建 Campaign
    with open(PRD_PATH, encoding="utf-8") as f:
        prd = json.load(f)

    print(f"\n🚀 GEO 面板同步")
    print(f"   面板地址：{panel_url}")
    campaign_id = get_or_create_campaign(panel_url, prd, force_new=args.new_campaign)
    print(f"   Campaign：{campaign_id}\n")

    if args.id:
        sync_single(args.id, panel_url, campaign_id)
    elif args.batch:
        sync_batch(panel_url, campaign_id, status_filter=args.status.split(","))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
