#!/usr/bin/env python3
"""
generate-cover.py — TRTC GEO 博客封面生成器

用法：
  单篇：
    python3 scripts/generate-cover.py --title "10 Best Chat SDKs in 2026" --output output/covers/P0-01.png

  批量（读 content-prd.json，给所有 done 文章生成封面）：
    python3 scripts/generate-cover.py --batch

  指定底图：
    python3 scripts/generate-cover.py --title "..." --bg assets/bg.png --output out.png
"""

import argparse
import json
import math
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("❌ 缺少 Pillow，请先安装：pip3 install Pillow")
    sys.exit(1)

# ── 默认路径 ──────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT  = os.path.dirname(SCRIPT_DIR)
DEFAULT_BG   = os.path.join(PLUGIN_ROOT, "assets", "cover-bg.png")
DEFAULT_PRD  = os.path.join(PLUGIN_ROOT, "output", "content-prd.json")
DEFAULT_OUT  = os.path.join(PLUGIN_ROOT, "output", "covers")

# ── 渲染参数 ──────────────────────────────────────────────
SCALE       = 3       # 超采样倍数（渲染后缩回，保证清晰度）
OUT_W       = 380     # 最终输出宽
OUT_H       = 200     # 最终输出高
COVER_X     = 148     # 左侧深色区域基准宽度（原始像素）
ARC_BULGE   = 18      # 弧形右边缘向右凸出幅度（原始像素）
ARC_BLUR    = 1.5     # 弧形边缘模糊半径（原始像素）
FONT_SIZE   = 16      # 字体大小（原始像素）
TEXT_X      = 12      # 文字左边距（原始像素）
TEXT_MAX_W  = 118     # 文字区域最大宽度（原始像素）
LINE_H      = 22      # 行高（原始像素）
TEXT_OFFSET = -5      # 文字块垂直居中微调（原始像素）

# 渐变色：顶部 → 底部
GRAD_TOP    = (4,  6,  20)
GRAD_BOTTOM = (19, 26, 75)

# 字体候选（按优先级）
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",   # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


# ══════════════════════════════════════════════════════════
# 核心生成函数
# ══════════════════════════════════════════════════════════
def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            pass
    print("⚠️  未找到粗体字体，使用默认字体（清晰度较低）")
    return ImageFont.load_default()


def wrap_by_pixel(text: str, font, max_w: int) -> list[str]:
    """按像素宽度精确换行"""
    words  = text.split()
    lines  = []
    cur    = ""
    for word in words:
        test = (cur + " " + word).strip()
        if font.getbbox(test)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def generate_cover(title: str, bg_path: str, output_path: str) -> bool:
    """
    生成一张封面图。
    返回 True 表示成功，False 表示失败。
    """
    # 1. 加载底图
    if not os.path.isfile(bg_path):
        print(f"❌ 底图不存在：{bg_path}")
        return False

    try:
        img = Image.open(bg_path).convert("RGBA")
    except Exception as e:
        print(f"❌ 无法读取底图：{e}")
        return False

    W0, H0 = OUT_W, OUT_H
    S = SCALE

    # 2. 超采样：放大到 S 倍
    W, H = W0 * S, H0 * S
    img = img.resize((W, H), Image.LANCZOS)

    # 3. 弧形遮罩（左侧深色区域）
    cx  = COVER_X  * S
    ab  = ARC_BULGE * S
    blr = ARC_BLUR  * S

    mask = Image.new("L", (W, H), 0)
    md   = ImageDraw.Draw(mask)
    pts  = [(0, 0)]
    for y in range(H + 1):
        t   = y / H
        arc = ab * math.sin(math.pi * t)
        pts.append((cx + arc, y))
    pts += [(0, H)]
    md.polygon(pts, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blr))

    # 4. 渐变色块
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / H
        r = int(GRAD_TOP[0] + t * (GRAD_BOTTOM[0] - GRAD_TOP[0]))
        g = int(GRAD_TOP[1] + t * (GRAD_BOTTOM[1] - GRAD_TOP[1]))
        b = int(GRAD_TOP[2] + t * (GRAD_BOTTOM[2] - GRAD_TOP[2]))
        gd.line([(0, y), (W, y)], fill=(r, g, b, 255))
    grad.putalpha(mask)
    img.paste(grad, (0, 0), grad)

    # 5. 文字
    draw     = ImageDraw.Draw(img)
    font     = load_font(FONT_SIZE * S)
    max_w    = TEXT_MAX_W * S
    line_h   = LINE_H * S
    text_x   = TEXT_X * S

    lines    = wrap_by_pixel(title, font, max_w)
    total_h  = len(lines) * line_h
    start_y  = (H - total_h) // 2 + TEXT_OFFSET * S

    for i, line in enumerate(lines):
        y = start_y + i * line_h
        # 阴影（增加对比度）
        draw.text((text_x + S, y + S), line, font=font, fill=(0, 0, 0, 120))
        # 白色正文
        draw.text((text_x, y), line, font=font, fill=(255, 255, 255, 255))

    # 6. 缩回原始尺寸（LANCZOS 高质量）
    img = img.resize((W0, H0), Image.LANCZOS)

    # 7. 保存
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, dpi=(144, 144))
    return True


# ══════════════════════════════════════════════════════════
# 批量模式
# ══════════════════════════════════════════════════════════
def batch_generate(prd_path: str, bg_path: str, out_dir: str):
    if not os.path.isfile(prd_path):
        print(f"❌ 找不到 content-prd.json：{prd_path}")
        sys.exit(1)

    with open(prd_path, encoding="utf-8") as f:
        prd = json.load(f)

    stories = prd.get("stories", [])
    targets = [s for s in stories if s.get("status") in ("done", "pending", "in_progress")]

    if not targets:
        print("⚠️  content-prd.json 中没有可处理的文章")
        return

    os.makedirs(out_dir, exist_ok=True)
    ok, fail = 0, 0

    print(f"\n🖼️  批量生成封面（共 {len(targets)} 篇）\n{'─'*40}")

    for story in targets:
        sid   = story.get("id", "unknown")
        title = story.get("title", sid)

        # 从 output_file 推导 slug，生成输出文件名
        out_file = story.get("output_file", "")
        slug     = os.path.basename(out_file).replace(".md", "") if out_file else sid
        out_path = os.path.join(out_dir, f"{slug}-cover.png")

        success = generate_cover(title, bg_path, out_path)
        if success:
            # 把封面路径写回 content-prd.json
            story["cover_file"] = out_path
            print(f"  ✅ {sid}  →  {os.path.basename(out_path)}")
            ok += 1
        else:
            print(f"  ❌ {sid}  生成失败")
            fail += 1

    # 写回 content-prd.json
    with open(prd_path, "w", encoding="utf-8") as f:
        json.dump(prd, f, ensure_ascii=False, indent=2)

    print(f"\n{'─'*40}")
    print(f"✅ 完成：{ok} 张成功，{fail} 张失败")
    print(f"📁 输出目录：{out_dir}")
    if ok:
        print(f"   cover_file 路径已写入 content-prd.json")


# ══════════════════════════════════════════════════════════
# CLI 入口
# ══════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="TRTC GEO 博客封面生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  单篇：
    python3 scripts/generate-cover.py \\
      --title "10 Best Chat SDKs in 2026" \\
      --output output/covers/P0-01-cover.png

  批量（读 content-prd.json）：
    python3 scripts/generate-cover.py --batch

  指定底图：
    python3 scripts/generate-cover.py \\
      --title "Best Chat APIs" \\
      --bg assets/cover-bg.png \\
      --output output/covers/test.png
        """
    )
    parser.add_argument("--title",  help="文章标题（单篇模式）")
    parser.add_argument("--bg",     default=DEFAULT_BG,  help=f"底图路径（默认：{DEFAULT_BG}）")
    parser.add_argument("--output", help="输出图片路径（单篇模式）")
    parser.add_argument("--batch",  action="store_true", help="批量模式：读 content-prd.json 生成全部封面")
    parser.add_argument("--prd",    default=DEFAULT_PRD, help=f"content-prd.json 路径（批量模式，默认：{DEFAULT_PRD}）")
    parser.add_argument("--out-dir",default=DEFAULT_OUT, help=f"封面输出目录（批量模式，默认：{DEFAULT_OUT}）")
    args = parser.parse_args()

    if args.batch:
        batch_generate(args.prd, args.bg, args.out_dir)

    elif args.title:
        out = args.output or os.path.join(DEFAULT_OUT, "cover-preview.png")
        print(f"🖼️  生成封面：{args.title[:50]}...")
        ok = generate_cover(args.title, args.bg, out)
        if ok:
            print(f"✅ 已保存：{out}")
        else:
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
