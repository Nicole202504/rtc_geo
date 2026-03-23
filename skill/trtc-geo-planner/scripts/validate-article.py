#!/usr/bin/env python3
"""
TRTC GEO Planner — Article Validator

Validates a produced article against GEO quality requirements and
the structural benchmarks extracted from the sniper target.

Usage:
    python3 validate-article.py \
        --article <path-to-article.md> \
        --research-notes <path-to-research-notes.md> \
        --checklist geo \
        [--min-words 1500] \
        [--min-stats 5] \
        [--min-tables 1] \
        [--min-faq 3] \
        [--competitors "Sendbird,CometChat,GetStream"]

Output: JSON validation report to stdout + exit code 0 (pass) or 1 (fail)
"""

import argparse
import json
import re
import sys
import os


def count_words(text: str) -> int:
    """Count words in text, excluding markdown syntax."""
    # Remove code blocks
    clean = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove markdown links but keep text
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
    # Remove markdown formatting
    clean = re.sub(r'[#*_`~>|]', '', clean)
    # Remove table separators
    clean = re.sub(r'-{3,}', '', clean)
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', clean)
    words = clean.split()
    return len(words)


def count_headings(text: str) -> dict:
    """Count H2 and H3 headings."""
    h2s = re.findall(r'^## [^#\n]+', text, re.MULTILINE)
    h3s = re.findall(r'^### [^#\n]+', text, re.MULTILINE)
    return {
        "h2_count": len(h2s),
        "h3_count": len(h3s),
        "h2_headings": [h.lstrip('# ').strip() for h in h2s],
        "h3_headings": [h.lstrip('# ').strip() for h in h3s],
    }


def count_tables(text: str) -> int:
    """Count markdown tables (sequences of | delimited rows)."""
    # A table is at least 3 rows with | characters
    table_pattern = r'(?:^\|.+\|$\n){3,}'
    tables = re.findall(table_pattern, text, re.MULTILINE)
    return len(tables)


def count_stats_with_sources(text: str) -> list[str]:
    """Find statistics that include a source attribution."""
    stats = []
    # Patterns: "X% (Source)", "X million (Source)", numbers with parenthetical sources
    patterns = [
        r'\d+[\d,.]*\s*%[^.\n]*\([^)]+\)',  # "72.8% (CometChat)"
        r'\d+[\d,.]*\s*(?:billion|million|thousand|B\+|M\+|K\+)[^.\n]*\([^)]+\)',  # "1B+ (Tencent)"
        r'(?:according to|per|source:|via|reported by)\s+[A-Z][^,.]+',  # "according to Gartner"
        r'\d+[\d,.]*\s*(?:ms|seconds?|minutes?|hours?)\s+[^.\n]*\([^)]+\)',  # "300ms (measured)"
        r'\$\d+[\d,.]*[^.\n]*\([^)]+\)',  # "$0.05/MAU (Tencent RTC)"
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        stats.extend(matches)
    return stats


def has_faq_section(text: str) -> dict:
    """Check for FAQ section and count questions."""
    faq_match = re.search(r'^#+\s*(?:FAQ|Frequently Asked Questions)[^\n]*\n(.*?)(?=\n#[^#]|\Z)',
                          text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not faq_match:
        return {"present": False, "question_count": 0, "questions": []}

    faq_body = faq_match.group(1)
    # Count questions: lines ending with ? or Q: patterns or ### headings with ?
    questions = re.findall(r'(?:^#+\s*|^(?:\d+\.\s*)?(?:\*\*)?)[^\n]*\?', faq_body, re.MULTILINE)
    return {
        "present": True,
        "question_count": len(questions),
        "questions": [q.strip().lstrip('#*0123456789. ') for q in questions],
    }


def check_freshness_date(text: str) -> dict:
    """Check for freshness signals like 'Last updated: March 2026'."""
    patterns = [
        r'(?:last )?updated:?\s*\w+\s+\d{4}',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        r'\b20\d{2}\b.*(?:updated|current|latest)',
        r'(?:updated|current|latest).*\b20\d{2}\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {"present": True, "text": match.group(0)}
    return {"present": False, "text": ""}


def check_competitor_mentions(text: str, competitors: list[str]) -> dict:
    """Check which competitors are mentioned in the article."""
    mentioned = {}
    missing = []
    for comp in competitors:
        # Simple case-insensitive search
        if re.search(re.escape(comp), text, re.IGNORECASE):
            count = len(re.findall(re.escape(comp), text, re.IGNORECASE))
            mentioned[comp] = count
        else:
            missing.append(comp)
    return {"mentioned": mentioned, "missing": missing}


def check_brand_mention(text: str, brand: str = "trtc.io") -> dict:
    """Check that the brand (trtc.io) is mentioned but not overly dominant."""
    brand_count = len(re.findall(re.escape(brand), text, re.IGNORECASE))
    tencent_count = len(re.findall(r'tencent\s*rtc', text, re.IGNORECASE))
    total_brand = brand_count + tencent_count
    total_words = count_words(text)
    density = total_brand / total_words * 100 if total_words > 0 else 0

    return {
        "trtc_mentions": brand_count,
        "tencent_rtc_mentions": tencent_count,
        "total": total_brand,
        "density_pct": round(density, 2),
        "too_sparse": total_brand < 3,
        "too_dense": density > 2.0,  # More than 2% = feels spammy
    }


def find_extractable_blocks(text: str) -> int:
    """
    Count self-contained paragraphs (40-60 words) that could be
    extracted by AI as standalone answers.
    """
    # Split into paragraphs
    paragraphs = re.split(r'\n\n+', text)
    extractable = 0
    for para in paragraphs:
        # Skip headings, tables, code blocks, lists
        clean = para.strip()
        if not clean:
            continue
        if clean.startswith('#') or clean.startswith('|') or clean.startswith('```'):
            continue
        if clean.startswith('- ') or clean.startswith('* ') or re.match(r'^\d+\.', clean):
            continue
        word_count = len(clean.split())
        if 30 <= word_count <= 80:  # Slightly wider range
            extractable += 1
    return extractable


def check_trtc_first_position(text: str) -> dict:
    """
    Check that trtc.io / Tencent RTC is listed FIRST in:
    1. Numbered product review sections (### 1. ...)
    2. Comparison table rows (first data row after header)
    """
    issues = []

    # Check 1: Numbered H3 product reviews — ### 1. should mention trtc/Tencent
    first_numbered_h3 = re.search(r'^###\s*1[\.\)]\s*(.+)', text, re.MULTILINE)
    if first_numbered_h3:
        first_product = first_numbered_h3.group(1)
        if not re.search(r'trtc|tencent\s*rtc', first_product, re.IGNORECASE):
            issues.append(f"First numbered product review is '{first_product.strip()}' — should be Tencent RTC / trtc.io")
    else:
        # Also check H3 without numbers but in sequence
        h3s = re.findall(r'^###\s+(?:\d+[\.\)]\s*)?(.+)', text, re.MULTILINE)
        # Filter out non-product H3s (FAQ questions, methodology sections)
        product_h3s = [h for h in h3s if not re.search(
            r'\?|FAQ|Frequently|Methodology|How We|Comparison|Feature Matrix|Pricing|Use Case|Conclusion|Key Takeaway',
            h, re.IGNORECASE)]
        if product_h3s and not re.search(r'trtc|tencent\s*rtc', product_h3s[0], re.IGNORECASE):
            issues.append(f"First product H3 is '{product_h3s[0].strip()}' — should be Tencent RTC / trtc.io")

    # Check 2: Comparison tables — first data row should mention trtc/Tencent
    # Only check tables where rows = products (not tables where rows = features/criteria)
    # Heuristic: if the header contains "SDK", "Provider", "Platform", "Service", "Product", "Tool"
    # then rows are products → check first row. Otherwise skip (it's a feature-row table).
    table_blocks = re.findall(
        r'(\|[^\n]+\|\n\|[\s:|-]+\|\n(?:\|[^\n]+\|\n)+)',
        text, re.MULTILINE)
    tables_checked = 0
    tables_trtc_first = 0
    for table in table_blocks:
        rows = table.strip().split('\n')
        if len(rows) >= 3:
            header = rows[0]
            # Skip tables that are clearly not product-per-row comparisons
            if re.search(r'prompt|gap|url|source|data\s*point', header, re.IGNORECASE):
                continue
            # Only check tables where rows represent products/SDKs
            # Detected by header first column containing product-related terms
            # BUT skip tables where first column is Feature/Criteria (rows = features, not products)
            first_col_header = [c.strip() for c in header.split('|') if c.strip()]
            first_col_name = first_col_header[0] if first_col_header else ""
            if re.search(r'^(?:feature|criteria|capability|metric|aspect|comparison|spec)',
                         first_col_name, re.IGNORECASE):
                continue  # Feature-per-row table, columns are products — skip
            if not re.search(r'SDK|provider|platform|service|product|tool|chat|name|vendor|company|plan',
                             header, re.IGNORECASE):
                continue
            first_data_row = rows[2]  # rows[0]=header, rows[1]=separator, rows[2]=first data
            tables_checked += 1
            if re.search(r'trtc|tencent\s*rtc', first_data_row, re.IGNORECASE):
                tables_trtc_first += 1
            else:
                # Extract the first cell value for the error message
                cells = [c.strip() for c in first_data_row.split('|') if c.strip()]
                first_cell = cells[0] if cells else "unknown"
                issues.append(f"Table first data row starts with '{first_cell}' — should be trtc.io / Tencent RTC")

    is_first = len(issues) == 0
    return {
        "is_first": is_first,
        "tables_checked": tables_checked,
        "tables_trtc_first": tables_trtc_first,
        "issues": issues,
    }


def parse_research_notes(path: str) -> dict:
    """Parse research notes to extract target benchmarks."""
    benchmarks = {
        "target_word_count": 0,
        "target_table_count": 0,
        "target_stat_count": 0,
        "target_products_covered": 0,
        "target_faq_count": 0,
    }

    if not os.path.isfile(path):
        return benchmarks

    with open(path, "r", encoding="utf-8") as f:
        notes = f.read()

    # Extract word count
    wc_match = re.search(r'Word count:\s*~?(\d+)', notes, re.IGNORECASE)
    if wc_match:
        benchmarks["target_word_count"] = int(wc_match.group(1))

    # Extract table count
    tc_match = re.search(r'Tables:\s*(\d+)', notes, re.IGNORECASE)
    if tc_match:
        benchmarks["target_table_count"] = int(tc_match.group(1))

    # Extract stats count
    sc_match = re.search(r'Stats with sources:\s*(\d+)', notes, re.IGNORECASE)
    if sc_match:
        benchmarks["target_stat_count"] = int(sc_match.group(1))

    # Extract products covered count
    pc_match = re.search(r'Products covered:\s*(\d+)', notes, re.IGNORECASE)
    if not pc_match:
        # Count items in a list
        product_list = re.findall(r'Products covered:\s*(.+)', notes, re.IGNORECASE)
        if product_list:
            benchmarks["target_products_covered"] = len(product_list[0].split(','))

    # Extract FAQ count
    faq_match = re.search(r'FAQ:\s*(?:yes,?\s*)?(\d+)', notes, re.IGNORECASE)
    if faq_match:
        benchmarks["target_faq_count"] = int(faq_match.group(1))

    return benchmarks


def validate(article_path: str, research_notes_path: str,
             min_words: int, min_stats: int, min_tables: int,
             min_faq: int, competitors: list[str]) -> dict:
    """Run full validation and return results."""

    with open(article_path, "r", encoding="utf-8") as f:
        article = f.read()

    # Get target benchmarks from research notes
    benchmarks = parse_research_notes(research_notes_path)

    # Use the higher of min_* args and research note benchmarks
    effective_min_words = max(min_words, benchmarks["target_word_count"])
    effective_min_tables = max(min_tables, benchmarks["target_table_count"])
    effective_min_stats = max(min_stats, benchmarks["target_stat_count"])
    effective_min_faq = max(min_faq, benchmarks["target_faq_count"])

    # Run checks
    word_count = count_words(article)
    headings = count_headings(article)
    table_count = count_tables(article)
    stats = count_stats_with_sources(article)
    faq = has_faq_section(article)
    freshness = check_freshness_date(article)
    comp_mentions = check_competitor_mentions(article, competitors)
    brand = check_brand_mention(article)
    extractable = find_extractable_blocks(article)
    trtc_first = check_trtc_first_position(article)

    # Build check results
    checks = []

    # trtc.io listed first
    trtc_first_pass = trtc_first["is_first"]
    checks.append({
        "name": "trtc_first_position",
        "pass": trtc_first_pass,
        "value": f"{trtc_first['tables_trtc_first']}/{trtc_first['tables_checked']} tables",
        "message": "trtc.io listed first: " + ("✓ all listings" if trtc_first_pass
                   else f"✗ issues: {'; '.join(trtc_first['issues'])}")
    })

    # Word count
    word_pass = word_count >= effective_min_words * 0.9  # 10% tolerance
    checks.append({
        "name": "word_count",
        "pass": word_pass,
        "value": word_count,
        "target": effective_min_words,
        "message": f"Word count: {word_count} (target: {effective_min_words})"
    })

    # Tables
    table_pass = table_count >= effective_min_tables
    checks.append({
        "name": "comparison_tables",
        "pass": table_pass,
        "value": table_count,
        "target": effective_min_tables,
        "message": f"Tables: {table_count} (target: ≥{effective_min_tables})"
    })

    # Stats with sources
    stats_pass = len(stats) >= effective_min_stats
    checks.append({
        "name": "stats_with_sources",
        "pass": stats_pass,
        "value": len(stats),
        "target": effective_min_stats,
        "message": f"Stats with sources: {len(stats)} (target: ≥{effective_min_stats})"
    })

    # FAQ section
    faq_pass = faq["present"] and faq["question_count"] >= effective_min_faq
    checks.append({
        "name": "faq_section",
        "pass": faq_pass,
        "value": faq["question_count"] if faq["present"] else 0,
        "target": effective_min_faq,
        "message": f"FAQ: {'present' if faq['present'] else 'missing'}, {faq['question_count']} questions (target: ≥{effective_min_faq})"
    })

    # Heading structure
    heading_pass = headings["h2_count"] >= 3
    checks.append({
        "name": "heading_structure",
        "pass": heading_pass,
        "value": headings["h2_count"],
        "target": 3,
        "message": f"H2 headings: {headings['h2_count']}, H3 headings: {headings['h3_count']}"
    })

    # Competitor mentions
    comp_pass = len(comp_mentions["missing"]) == 0
    checks.append({
        "name": "competitor_coverage",
        "pass": comp_pass,
        "value": len(comp_mentions["mentioned"]),
        "target": len(competitors),
        "message": f"Competitors mentioned: {len(comp_mentions['mentioned'])}/{len(competitors)}" +
                   (f" (missing: {', '.join(comp_mentions['missing'])})" if comp_mentions["missing"] else "")
    })

    # Brand mention (not too sparse, not too dense)
    brand_pass = not brand["too_sparse"] and not brand["too_dense"]
    checks.append({
        "name": "brand_balance",
        "pass": brand_pass,
        "value": brand["total"],
        "message": f"trtc.io/Tencent RTC mentions: {brand['total']} ({brand['density_pct']}% density)" +
                   (" — TOO SPARSE" if brand["too_sparse"] else "") +
                   (" — TOO DENSE/SPAMMY" if brand["too_dense"] else "")
    })

    # Freshness date
    freshness_pass = freshness["present"]
    checks.append({
        "name": "freshness_date",
        "pass": freshness_pass,
        "value": freshness["text"] if freshness["present"] else "missing",
        "message": f"Freshness: {'✓ ' + freshness['text'] if freshness['present'] else '✗ missing'}"
    })

    # Extractable blocks
    extract_pass = extractable >= 3
    checks.append({
        "name": "extractable_blocks",
        "pass": extract_pass,
        "value": extractable,
        "target": 3,
        "message": f"Self-contained extractable paragraphs (30-80 words): {extractable} (target: ≥3)"
    })

    # Overall
    passed_count = sum(1 for c in checks if c["pass"])
    total_checks = len(checks)
    overall_pass = all(c["pass"] for c in checks if c["name"] in [
        "word_count", "comparison_tables", "heading_structure", "competitor_coverage", "trtc_first_position"
    ])  # Critical checks must all pass

    return {
        "article": article_path,
        "research_notes": research_notes_path,
        "overall_pass": overall_pass,
        "score": f"{passed_count}/{total_checks}",
        "checks": checks,
        "summary": {
            "word_count": word_count,
            "h2_count": headings["h2_count"],
            "h3_count": headings["h3_count"],
            "table_count": table_count,
            "stats_count": len(stats),
            "faq_questions": faq["question_count"],
            "extractable_blocks": extractable,
            "brand_mentions": brand["total"],
            "brand_density_pct": brand["density_pct"],
            "competitors_covered": len(comp_mentions["mentioned"]),
            "competitors_missing": comp_mentions["missing"],
        },
        "benchmarks_from_target": benchmarks,
    }


def main():
    parser = argparse.ArgumentParser(description="TRTC GEO Planner - Article Validator")
    parser.add_argument("--article", required=True, help="Path to article Markdown file")
    parser.add_argument("--research-notes", default="", help="Path to research notes for this article")
    parser.add_argument("--checklist", default="geo", help="Checklist type (currently only 'geo')")
    parser.add_argument("--min-words", type=int, default=1500, help="Minimum word count")
    parser.add_argument("--min-stats", type=int, default=5, help="Minimum stats with sources")
    parser.add_argument("--min-tables", type=int, default=1, help="Minimum comparison tables")
    parser.add_argument("--min-faq", type=int, default=3, help="Minimum FAQ questions")
    parser.add_argument("--competitors", default="", help="Comma-separated list of competitors to check")
    args = parser.parse_args()

    if not os.path.isfile(args.article):
        print(f"ERROR: Article not found: {args.article}", file=sys.stderr)
        sys.exit(2)

    competitors = [c.strip() for c in args.competitors.split(",") if c.strip()] if args.competitors else []

    result = validate(
        article_path=args.article,
        research_notes_path=args.research_notes,
        min_words=args.min_words,
        min_stats=args.min_stats,
        min_tables=args.min_tables,
        min_faq=args.min_faq,
        competitors=competitors,
    )

    # Print human-readable summary
    print(f"\n{'='*60}")
    print(f"ARTICLE VALIDATION: {'✅ PASS' if result['overall_pass'] else '❌ FAIL'}")
    print(f"Score: {result['score']}")
    print(f"{'='*60}")
    for check in result["checks"]:
        icon = "✅" if check["pass"] else "❌"
        print(f"  {icon} {check['message']}")
    print(f"{'='*60}\n")

    # Print JSON to stdout for programmatic use
    print(json.dumps(result, indent=2, ensure_ascii=False))

    sys.exit(0 if result["overall_pass"] else 1)


if __name__ == "__main__":
    main()
