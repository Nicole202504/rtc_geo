#!/usr/bin/env python3
"""
TRTC GEO Planner — Content PRD Generator

Reads the GEO strategy report (Markdown) and extracts action items
into a Ralph-style content-prd.json for tracking article production.

Usage:
    python3 generate-content-prd.py \
        --report <path-to-strategy-report.md> \
        --output <output-path>/content-prd.json

The script parses the report's Part A (blog) and Part B (community)
sections, extracting each action item's metadata into a structured JSON.
"""

import argparse
import json
import re
import sys
import os
from datetime import datetime


def slugify(title: str) -> str:
    """Convert title to a file-friendly slug."""
    slug = title.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug[:60].rstrip('-')


def extract_json_block(text: str) -> dict | None:
    """Extract the first JSON code block from a text section."""
    match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def extract_blog_items(report_text: str) -> list[dict]:
    """Extract blog action items from Part A of the report."""
    items = []

    # Find all P0-XX and P1-XX sections
    pattern = r'### \[(P[01]-\d+)\]\s*"?([^"\n]+)"?\s*\n(.*?)(?=\n### \[P[01]-\d+\]|\n## Part [BC]|\n### Additional Blog|\Z)'
    matches = re.finditer(pattern, report_text, re.DOTALL)

    for match in matches:
        item_id = match.group(1)
        title = match.group(2).strip().strip('"')
        body = match.group(3)

        # Extract priority score
        priority_match = re.search(r'\*\*Priority Score:\*\*\s*(\d+(?:\.\d+)?)/100', body)
        priority_score = float(priority_match.group(1)) if priority_match else 50.0

        # Extract effort
        effort_match = re.search(r'\*\*Effort:\*\*\s*(\S+)', body)
        effort = effort_match.group(1) if effort_match else "Medium"

        # Extract reference articles (the sniper target is the one with most citations)
        sniper_target = ""
        sniper_citations = 0
        ref_table_pattern = r'\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*\*?\*?(\d+)\*?\*?\s*\|'
        for ref_match in re.finditer(ref_table_pattern, body):
            url = ref_match.group(2)
            citations = int(ref_match.group(4))
            if citations > sniper_citations:
                sniper_target = url
                sniper_citations = citations

        # Extract context package JSON
        context_package = extract_json_block(body)

        # Extract target word count from context package or body
        target_length = "2000-3000"
        if context_package and "target_length" in context_package:
            target_length = context_package["target_length"]
        else:
            length_match = re.search(r'Target Word Count:\*\*\s*(\S+)', body)
            if length_match:
                target_length = length_match.group(1)

        # Determine priority order from the item ID
        priority_num = int(re.search(r'\d+', item_id.split('-')[1]).group())
        is_p0 = item_id.startswith("P0")

        slug = slugify(title)

        items.append({
            "id": item_id,
            "title": title,
            "type": "blog",
            "priority": priority_num if is_p0 else priority_num + 100,
            "priority_score": priority_score,
            "effort": effort,
            "status": "pending",
            "sniper_target": sniper_target,
            "target_citations": sniper_citations,
            "target_length": target_length,
            "context_package": context_package,
            "output_file": f"articles/{item_id}-{slug}.md",
            "research_file": f"research-notes/{item_id}.md",
            "validation": None,
            "word_count": None,
        })

    return items


def extract_community_items(report_text: str) -> list[dict]:
    """Extract community action items from Part B of the report."""
    items = []

    pattern = r'### \[(P0-C\d+)\]\s*([^\n]+)\n(.*?)(?=\n### \[P0-C\d+\]|\n### Additional Community|\n## Part C|\Z)'
    matches = re.finditer(pattern, report_text, re.DOTALL)

    for match in matches:
        item_id = match.group(1)
        title = match.group(2).strip()
        body = match.group(3)

        # Extract priority score
        priority_match = re.search(r'\*\*Priority Score:\*\*\s*(\d+(?:\.\d+)?)/100', body)
        priority_score = float(priority_match.group(1)) if priority_match else 50.0

        # Extract effort
        effort_match = re.search(r'\*\*Effort:\*\*\s*(\S+)', body)
        effort = effort_match.group(1) if effort_match else "Low"

        # Extract platform
        platform_match = re.search(r'\*\*Platform:\*\*\s*(\S+)', body)
        platform = platform_match.group(1) if platform_match else "unknown"

        # Extract channel
        channel_match = re.search(r'\*\*Specific Channel:\*\*\s*(.+)', body)
        channel = channel_match.group(1).strip() if channel_match else ""

        # Extract reference URL
        ref_match = re.search(r'\*\*Reference[^:]*:\*\*\s*\[([^\]]+)\]\(([^)]+)\)', body)
        sniper_target = ref_match.group(2) if ref_match else ""

        # Extract citation count from reference
        cite_match = re.search(r'cited\s*\*?\*?(\d+)\s*times?\*?\*?', body)
        sniper_citations = int(cite_match.group(1)) if cite_match else 0

        # Extract context package
        context_package = extract_json_block(body)

        priority_num = int(re.search(r'\d+', item_id.split('C')[1]).group())
        slug = slugify(title)

        items.append({
            "id": item_id,
            "title": title,
            "type": "community",
            "priority": priority_num + 50,  # Community items after blog P0s
            "priority_score": priority_score,
            "effort": effort,
            "platform": platform,
            "channel": channel,
            "status": "pending",
            "sniper_target": sniper_target,
            "target_citations": sniper_citations,
            "context_package": context_package,
            "output_file": f"articles/{item_id}-{slug}.md",
            "research_file": f"research-notes/{item_id}.md",
            "validation": None,
            "word_count": None,
        })

    return items


def extract_p1_blog_items(report_text: str) -> list[dict]:
    """Extract P1 blog items from the Additional Blog Topics table."""
    items = []

    # Look for the P1 table
    table_pattern = r'\|\s*(P1-\d+)\s*\|\s*"?([^"|]+)"?\s*\|\s*(\d+)\s*\|\s*(\S+)\s*\|'
    for match in re.finditer(table_pattern, report_text):
        item_id = match.group(1)
        title = match.group(2).strip().strip('"')
        prompt_count = int(match.group(3))
        effort = match.group(4)

        priority_num = int(re.search(r'\d+', item_id.split('-')[1]).group())
        slug = slugify(title)

        items.append({
            "id": item_id,
            "title": title,
            "type": "blog",
            "priority": priority_num + 100,
            "priority_score": 50.0,
            "effort": effort,
            "status": "pending",
            "sniper_target": "",
            "target_citations": 0,
            "target_length": "1500-2500",
            "context_package": None,
            "output_file": f"articles/{item_id}-{slug}.md",
            "research_file": f"research-notes/{item_id}.md",
            "validation": None,
            "word_count": None,
        })

    return items


def main():
    parser = argparse.ArgumentParser(description="TRTC GEO Planner - Content PRD Generator")
    parser.add_argument("--report", required=True, help="Path to GEO strategy report (Markdown)")
    parser.add_argument("--output", default="content-prd.json", help="Output JSON path")
    args = parser.parse_args()

    if not os.path.isfile(args.report):
        print(f"ERROR: Report file not found: {args.report}", file=sys.stderr)
        sys.exit(1)

    with open(args.report, "r", encoding="utf-8") as f:
        report_text = f.read()

    # Extract all items
    blog_items = extract_blog_items(report_text)
    community_items = extract_community_items(report_text)
    p1_items = extract_p1_blog_items(report_text)

    # Merge (avoid duplicates from P1 items already in blog_items)
    existing_ids = {item["id"] for item in blog_items}
    for item in p1_items:
        if item["id"] not in existing_ids:
            blog_items.append(item)

    all_stories = blog_items + community_items
    all_stories.sort(key=lambda x: x["priority"])

    prd = {
        "project": "trtc-geo-content",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "total_stories": len(all_stories),
        "blog_count": len([s for s in all_stories if s["type"] == "blog"]),
        "community_count": len([s for s in all_stories if s["type"] == "community"]),
        "done_count": 0,
        "stories": all_stories,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(prd, f, indent=2, ensure_ascii=False)

    print(f"Content PRD generated: {args.output}")
    print(f"  - Blog articles: {prd['blog_count']}")
    print(f"  - Community posts: {prd['community_count']}")
    print(f"  - Total stories: {prd['total_stories']}")

    # Print priority list
    print("\nPriority order:")
    for s in all_stories[:15]:
        print(f"  [{s['id']}] ({s['priority_score']}/100) {s['title'][:60]}...")


if __name__ == "__main__":
    main()
