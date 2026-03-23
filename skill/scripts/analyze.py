#!/usr/bin/env python3
"""
TRTC GEO Planner — CSV Data Analyzer

Reads three Peec AI export CSVs (prompts, source-domains, source-urls)
and produces a structured JSON analysis for the GEO content strategy report.

Usage:
    python3 analyze.py \
        --prompts <prompts.csv> \
        --domains <domains.csv> \
        --urls <urls.csv> \
        --brand trtc.io \
        --output geo-analysis.json
"""

import argparse
import csv
import json
import sys
import os
from collections import defaultdict
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Community / UGC domains we care about
# ---------------------------------------------------------------------------
COMMUNITY_DOMAINS = {
    "reddit.com", "dev.to", "medium.com", "github.com",
    "stackoverflow.com", "quora.com", "hackernoon.com",
    "news.ycombinator.com", "hashnode.dev",
}

# Platform reach scores (for community opportunity scoring)
PLATFORM_REACH = {
    "reddit.com": 100,
    "dev.to": 85,
    "medium.com": 75,
    "github.com": 80,
    "stackoverflow.com": 90,
    "hackernoon.com": 60,
    "quora.com": 55,
    "news.ycombinator.com": 70,
    "hashnode.dev": 40,
}

# Content types we target for blog opportunities
BLOG_CONTENT_TYPES = {
    "Listicle", "Comparison", "How-To Guide", "Article",
    "Alternative", "Review",
}

# Feasibility scores by content type
CONTENT_FEASIBILITY = {
    "Listicle": 90,
    "Comparison": 90,
    "Alternative": 85,
    "How-To Guide": 80,
    "Article": 70,
    "Review": 65,
    "Discussion": 50,
    "Product Page": 40,
    "Other": 30,
}


def parse_pct(val: str) -> float:
    """Parse '72.8%' -> 0.728"""
    val = val.strip().rstrip("%")
    try:
        return float(val) / 100
    except (ValueError, TypeError):
        return 0.0


def parse_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val.strip())
    except (ValueError, TypeError):
        return default


def parse_int(val: str, default: int = 0) -> int:
    try:
        return int(val.strip())
    except (ValueError, TypeError):
        return default


def domain_of(url: str) -> str:
    """Extract domain from URL, stripping www."""
    try:
        d = urlparse(url).netloc.lower()
        if d.startswith("www."):
            d = d[4:]
        return d
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# CSV readers
# ---------------------------------------------------------------------------

def read_prompts(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "id": r.get("id", "").strip(),
                "prompt": r.get("prompt", "").strip(),
                "position": r.get("position", "-").strip(),
                "sentiment": parse_float(r.get("sentiment", ""), -1),
                "visibility": parse_float(r.get("visibility", "0")),
                "volume": parse_int(r.get("volume", "0")),
                "top": r.get("top", "").strip(),
                "tags": r.get("tags", "").strip(),
                "location": r.get("location", "").strip(),
            })
    return rows


def read_domains(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "domain": r.get("Domain", "").strip(),
                "type": r.get("Type", "").strip(),
                "used_pct": parse_pct(r.get("Used", "0%")),
                "avg_citations": parse_float(r.get("Avg. Citations", "0")),
            })
    return rows


def read_urls(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "url": r.get("URL", "").strip(),
                "title": r.get("Title", "").strip(),
                "type": r.get("Type", "").strip(),
                "mentioned": r.get("Mentioned", "").strip(),
                "mentions": r.get("Mentions", "").strip(),
                "used_total": parse_int(r.get("Used total", "0")),
                "avg_citations": parse_float(r.get("Avg. Citations", "0")),
                "domain": domain_of(r.get("URL", "")),
            })
    return rows


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def analyze_prompts(prompts: list[dict], brand: str) -> dict:
    """Analyze prompt-level visibility."""
    total = len(prompts)
    present = [p for p in prompts if p["position"] != "-"]
    absent = [p for p in prompts if p["position"] == "-"]
    transactional = [p for p in prompts if "transactional" in p["tags"].lower()]
    informational = [p for p in prompts if "informational" in p["tags"].lower()]

    avg_visibility = sum(p["visibility"] for p in prompts) / total if total else 0

    return {
        "total_prompts": total,
        "present_count": len(present),
        "absent_count": len(absent),
        "present_pct": round(len(present) / total * 100, 1) if total else 0,
        "absent_pct": round(len(absent) / total * 100, 1) if total else 0,
        "avg_visibility": round(avg_visibility, 3),
        "transactional_count": len(transactional),
        "informational_count": len(informational),
        "present_prompts": sorted(present, key=lambda x: x["visibility"], reverse=True),
        "absent_prompts": absent,
    }


def analyze_domains(domains: list[dict]) -> dict:
    """Analyze domain-level competition."""
    competitors = [d for d in domains if d["type"] == "Competitor"]
    ugc = [d for d in domains if d["type"] == "UGC"
           or d["domain"] in COMMUNITY_DOMAINS]
    corporate = [d for d in domains if d["type"] == "Corporate"]
    brand_self = [d for d in domains if d["type"] == "You"]

    return {
        "total_domains": len(domains),
        "top_competitors": sorted(competitors, key=lambda x: x["used_pct"], reverse=True)[:10],
        "top_ugc": sorted(ugc, key=lambda x: x["used_pct"], reverse=True)[:10],
        "top_corporate": sorted(corporate, key=lambda x: x["used_pct"], reverse=True)[:10],
        "brand_data": brand_self,
    }


def find_blog_opportunities(urls: list[dict], prompts: list[dict], brand: str) -> list[dict]:
    """
    Identify blog article opportunities.
    Returns ranked list of content to create.
    """
    # Max used_total for normalization
    max_used = max((u["used_total"] for u in urls), default=1)

    # Build prompt lookup by keywords for rough matching
    absent_prompt_texts = [
        p["prompt"] for p in prompts if p["position"] == "-"
    ]
    low_vis_prompts = [
        p["prompt"] for p in prompts
        if p["position"] != "-" and p["visibility"] < 0.3
    ]

    opportunities = []
    seen_titles = set()

    for u in urls:
        # Only blog-type content
        if u["type"] not in BLOG_CONTENT_TYPES:
            continue
        # Skip our own content
        if brand.lower() in u["domain"].lower():
            continue
        # Deduplicate by title (normalized)
        title_key = u["title"].lower().strip()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        # Calculate score components
        citation_strength = min(100, (u["used_total"] / max_used) * 100)

        # Gap severity: if "Mentioned" is "No", we're absent from this content
        if u["mentioned"].lower() == "no":
            gap_severity = 100
        elif u["mentioned"].lower() == "unknown":
            gap_severity = 60
        else:
            gap_severity = 20  # We're mentioned but might need improvement

        # Intent value: try to match with prompts
        # Simple heuristic: check if any absent transactional prompt keywords overlap
        intent_value = 60  # Default informational
        title_lower = u["title"].lower()
        mentions_lower = u["mentions"].lower()
        for p in prompts:
            if "transactional" in p["tags"].lower():
                # Rough keyword overlap check
                prompt_words = set(p["prompt"].lower().split())
                title_words = set(title_lower.split())
                if len(prompt_words & title_words) >= 3:
                    intent_value = 100
                    break

        feasibility = CONTENT_FEASIBILITY.get(u["type"], 50)

        score = (
            citation_strength * 0.4
            + gap_severity * 0.3
            + intent_value * 0.2
            + feasibility * 0.1
        )

        # Find related prompts
        related_prompts = []
        title_words = set(title_lower.split())
        for p in prompts:
            prompt_words = set(p["prompt"].lower().split())
            overlap = len(prompt_words & title_words)
            if overlap >= 2:
                related_prompts.append({
                    "prompt": p["prompt"],
                    "position": p["position"],
                    "visibility": p["visibility"],
                    "tags": p["tags"],
                })

        opportunities.append({
            "score": round(score, 1),
            "reference_url": u["url"],
            "reference_title": u["title"],
            "content_type": u["type"],
            "used_total": u["used_total"],
            "avg_citations": u["avg_citations"],
            "mentioned": u["mentioned"],
            "competitors_mentioned": u["mentions"],
            "domain": u["domain"],
            "related_prompts": related_prompts[:5],
            "scoring_breakdown": {
                "citation_strength": round(citation_strength, 1),
                "gap_severity": round(gap_severity, 1),
                "intent_value": round(intent_value, 1),
                "feasibility": round(feasibility, 1),
            },
        })

    # Sort by score descending
    opportunities.sort(key=lambda x: x["score"], reverse=True)
    return opportunities


def find_community_opportunities(urls: list[dict], domains: list[dict], prompts: list[dict]) -> list[dict]:
    """
    Identify community posting opportunities.
    """
    # Filter URLs to community domains
    community_urls = [
        u for u in urls
        if any(cd in u["domain"] for cd in COMMUNITY_DOMAINS)
    ]

    max_used = max((u["used_total"] for u in community_urls), default=1) if community_urls else 1

    opportunities = []
    for u in community_urls:
        # Determine which community domain
        matched_domain = None
        for cd in COMMUNITY_DOMAINS:
            if cd in u["domain"]:
                matched_domain = cd
                break
        if not matched_domain:
            continue

        citation_freq = min(100, (u["used_total"] / max_used) * 100)
        platform_reach_score = PLATFORM_REACH.get(matched_domain, 30)

        # Count related prompts
        title_lower = u["title"].lower()
        title_words = set(title_lower.split())
        related_count = 0
        related_prompts = []
        for p in prompts:
            prompt_words = set(p["prompt"].lower().split())
            if len(prompt_words & title_words) >= 2:
                related_count += 1
                related_prompts.append(p["prompt"])

        prompt_coverage = min(100, related_count * 20)

        score = (
            citation_freq * 0.5
            + (platform_reach_score / 100 * 100) * 0.3
            + prompt_coverage * 0.2
        )

        # Determine content angle
        if "vs" in title_lower or "compar" in title_lower:
            angle = "technical comparison"
        elif "recommend" in title_lower or "best" in title_lower or "suggest" in title_lower:
            angle = "recommendation discussion"
        elif "how" in title_lower or "tutorial" in title_lower or "guide" in title_lower:
            angle = "tutorial / how-to"
        elif "review" in title_lower or "experience" in title_lower:
            angle = "experience sharing"
        else:
            angle = "general discussion"

        # Extract subreddit if reddit
        channel = ""
        if "reddit.com" in u["url"]:
            parts = u["url"].split("/")
            for i, part in enumerate(parts):
                if part == "r" and i + 1 < len(parts):
                    channel = f"r/{parts[i+1]}"
                    break

        opportunities.append({
            "score": round(score, 1),
            "platform": matched_domain,
            "channel": channel,
            "reference_url": u["url"],
            "reference_title": u["title"],
            "used_total": u["used_total"],
            "avg_citations": u["avg_citations"],
            "content_angle": angle,
            "related_prompts": related_prompts[:5],
            "scoring_breakdown": {
                "citation_frequency": round(citation_freq, 1),
                "platform_reach": platform_reach_score,
                "prompt_coverage": round(prompt_coverage, 1),
            },
        })

    opportunities.sort(key=lambda x: x["score"], reverse=True)
    return opportunities


def identify_quick_wins(blog_opps: list[dict], community_opps: list[dict]) -> list[dict]:
    """Top 5 highest-impact actions combining both tracks."""
    wins = []

    # Top blog opportunities where we're not mentioned and content type is easy
    for b in blog_opps[:3]:
        wins.append({
            "action": f"Write a GEO-optimized {b['content_type']} to compete with: \"{b['reference_title']}\"",
            "type": "Blog",
            "reference": b["reference_url"],
            "estimated_impact": "High" if b["score"] > 70 else "Medium",
            "effort": "Medium",
            "prompts_affected": len(b["related_prompts"]),
            "score": b["score"],
        })

    # Top community opportunities
    for c in community_opps[:2]:
        wins.append({
            "action": f"Post {c['content_angle']} content on {c['platform']}" + (f" ({c['channel']})" if c['channel'] else ""),
            "type": "Community",
            "reference": c["reference_url"],
            "estimated_impact": "Medium",
            "effort": "Low",
            "prompts_affected": len(c["related_prompts"]),
            "score": c["score"],
        })

    wins.sort(key=lambda x: x["score"], reverse=True)
    return wins[:5]


def compute_content_type_distribution(urls: list[dict]) -> dict:
    """Count content types across all cited URLs."""
    dist = defaultdict(int)
    for u in urls:
        dist[u["type"]] += 1
    total = sum(dist.values())
    result = []
    for ctype, count in sorted(dist.items(), key=lambda x: x[1], reverse=True):
        result.append({
            "type": ctype,
            "count": count,
            "pct": round(count / total * 100, 1) if total else 0,
        })
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="TRTC GEO Planner - CSV Analyzer")
    parser.add_argument("--prompts", required=True, help="Path to prompts CSV")
    parser.add_argument("--domains", required=True, help="Path to source-domains CSV")
    parser.add_argument("--urls", required=True, help="Path to source-urls CSV")
    parser.add_argument("--brand", default="trtc.io", help="Brand domain (default: trtc.io)")
    parser.add_argument("--output", default="geo-analysis.json", help="Output JSON path")
    args = parser.parse_args()

    # Validate inputs
    for label, path in [("prompts", args.prompts), ("domains", args.domains), ("urls", args.urls)]:
        if not os.path.isfile(path):
            print(f"ERROR: {label} CSV not found: {path}", file=sys.stderr)
            sys.exit(1)

    # Read data
    prompts = read_prompts(args.prompts)
    domains = read_domains(args.domains)
    urls = read_urls(args.urls)

    print(f"Loaded: {len(prompts)} prompts, {len(domains)} domains, {len(urls)} URLs")

    # Analyze
    prompt_analysis = analyze_prompts(prompts, args.brand)
    domain_analysis = analyze_domains(domains)
    blog_opps = find_blog_opportunities(urls, prompts, args.brand)
    community_opps = find_community_opportunities(urls, domains, prompts)
    quick_wins = identify_quick_wins(blog_opps, community_opps)
    content_type_dist = compute_content_type_distribution(urls)

    # Determine how many blog articles needed for full prompt coverage
    # We need enough articles that each absent/low-vis prompt is covered by at least one
    absent_prompts = prompt_analysis["absent_prompts"]
    low_vis = [p for p in prompt_analysis["present_prompts"] if p["visibility"] < 0.3]
    all_gap_prompts = absent_prompts + low_vis

    # Estimate: each blog article covers ~3-5 related prompts
    estimated_blog_count = max(len(blog_opps[:20]), len(all_gap_prompts) // 3 + 1)
    # But cap at reasonable number and let the report include all that matter
    estimated_blog_count = min(estimated_blog_count, len(blog_opps))

    # Build output
    output = {
        "summary": {
            "brand": args.brand,
            "total_prompts_tracked": prompt_analysis["total_prompts"],
            "prompts_with_presence": prompt_analysis["present_count"],
            "prompts_absent": prompt_analysis["absent_count"],
            "presence_rate_pct": prompt_analysis["present_pct"],
            "avg_visibility": prompt_analysis["avg_visibility"],
            "total_blog_opportunities": len(blog_opps),
            "total_community_opportunities": len(community_opps),
            "estimated_blog_articles_needed": estimated_blog_count,
            "gap_prompts_count": len(all_gap_prompts),
        },
        "prompt_analysis": {
            "present_prompts": prompt_analysis["present_prompts"],
            "absent_prompts": prompt_analysis["absent_prompts"],
            "transactional_count": prompt_analysis["transactional_count"],
            "informational_count": prompt_analysis["informational_count"],
        },
        "domain_analysis": domain_analysis,
        "blog_opportunities": blog_opps[:30],  # Top 30
        "community_opportunities": community_opps[:20],  # Top 20
        "quick_wins": quick_wins,
        "content_type_distribution": content_type_dist,
    }

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nAnalysis complete! Output written to: {args.output}")
    print(f"\nSummary:")
    print(f"  - Tracked prompts: {prompt_analysis['total_prompts']}")
    print(f"  - Presence rate: {prompt_analysis['present_pct']}%")
    print(f"  - Absent from: {prompt_analysis['absent_count']} prompts")
    print(f"  - Blog opportunities identified: {len(blog_opps)}")
    print(f"  - Community opportunities identified: {len(community_opps)}")
    print(f"  - Estimated blog articles for full coverage: {estimated_blog_count}")
    print(f"  - Top 5 quick wins generated")


if __name__ == "__main__":
    main()
