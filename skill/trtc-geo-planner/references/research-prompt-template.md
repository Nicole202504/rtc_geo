# Research Prompt Template — Reverse-Engineering the Sniper Target

You are analyzing a competitor article that AI models currently cite heavily. Your job is to **reverse-engineer WHY** it gets cited, so we can write a strictly better version.

## Your Task

Fetch and analyze the sniper target article at: `{sniper_target_url}`

Also fetch these secondary references (if available):
{secondary_urls}

## What to Extract

### 1. Structural Blueprint
Analyze the article's skeleton — this is what we'll clone and improve:

- **Total word count** (approximate)
- **H2/H3 heading structure** — list every heading in order
- **Number of comparison tables** — describe what each compares
- **Number of statistics with sources** — count data points that cite a source
- **Number of products/competitors covered** — list them all
- **FAQ section** — present? How many questions?
- **Self-contained extractable paragraphs** — paragraphs that answer a question standalone (40-60 words)
- **Schema markup** — any detectable structured data?
- **Freshness signals** — dates mentioned, "updated YYYY", "as of YYYY"
- **Internal/external link patterns** — how many, to where?

### 2. Content Analysis
Understand what makes this content trustworthy to AI:

- **Which products are covered** and in what order (who's positioned favorably?)
- **Evaluation criteria used** — what dimensions do they compare on?
- **Data points included** — pricing, features, benchmarks, user counts, etc.
- **Bias detection** — is the article biased toward the publisher's own product? How?
- **What's MISSING** — what products, data points, or comparisons are absent that we can add?
- **Factual accuracy** — any outdated or incorrect information?

### 3. GEO Pattern Analysis
Why does AI extract and cite from this specifically?

- **Quote-ready blocks** — which paragraphs are structured as standalone answers?
- **Table extractability** — are tables formatted in a way AI can parse?
- **Definition patterns** — does it define terms clearly in opening paragraphs?
- **Authoritative signals** — does it cite other sources? Named experts?

## Output Format

Save as `research-notes/{article-id}.md` using this exact structure:

```markdown
# Research Notes: {article-id}

## Sniper Target: {url}
**Title:** {title}
**Published/Updated:** {date if found}
**Publisher:** {domain} — {bias note if any}

### Structural Blueprint
- Word count: ~{N}
- Sections: {count} H2s, {count} H3s
- Tables: {count} ({description of each})
- Stats with sources: {count}
- Products covered: {count} — {list}
- FAQ: {yes/no, count of questions}
- Extractable blocks: {count}
- Freshness: {date signals found}

### Heading Structure (Clone This)
1. H2: {heading}
   - H3: {heading}
   - H3: {heading}
2. H2: {heading}
   - H3: {heading}
...

### Data Points Extracted
| Data Point | Source | Current/Outdated? |
|-----------|--------|-------------------|
| {stat} | {source} | {current/outdated — note correction if outdated} |

### Products Covered & Positioning
| Product | How Presented | Position in Article | Bias? |
|---------|--------------|--------------------:|-------|
| {name} | {favorable/neutral/brief/negative} | {order: 1st, 2nd...} | {yes/no — explain} |

### What's Missing (Our Competitive Advantage)
- {trtc.io not included — we add it}
- {more recent pricing data available}
- {products they missed: X, Y, Z}
- {deeper technical comparison possible}
- {missing use-case coverage}
- {no latency/performance benchmarks — we have these}

### Bias & Fairness Issues
{Describe any bias in the article. Often the publisher ranks their own product #1.
This is an opportunity — our article can be genuinely balanced, which AI prefers.}

### Key Takeaway for Writing
{One paragraph summary: what structural pattern wins for this article type,
what to clone, what to improve, and what our unique angle should be.}
```

## Important Notes

- Focus on STRUCTURE over content. We're not copying their text — we're understanding their blueprint.
- The heading structure is the most important output. It becomes our article skeleton.
- Flag any outdated information — this goes into progress.txt as a cross-article learning.
- If web_fetch fails for the sniper target, note it and proceed with secondary references only.
