# Article Writing Prompt Template — Structure-First GEO Content

You are writing a GEO-optimized article for trtc.io/blog. This article exists to **dethrone a specific competitor article** that AI currently cites. You are NOT writing a generic article — you are writing a structurally superior replacement.

## Your Inputs

1. **Research notes** from `research-notes/{article-id}.md` — contains the structural blueprint of the article we're replacing
2. **Product context** from `references/trtc-product-context.md` — trtc.io data points
3. **GEO checklist** from `references/geo-strategy.md` Section 3 — mandatory requirements
4. **Context package** — specific instructions for this article (prompts to target, competitors to cover, etc.)
5. **Progress notes** from `progress.txt` — learnings from previous articles (if any)

## Writing Process

### Step 1: Clone the Structure

Start with the heading structure from the research notes. This is your skeleton. The sniper target gets cited because of this structure — replicate it.

```
{heading structure from research notes}
```

### Step 2: Improve the Structure

Now add what the target is missing:
- **Add sections for missing products** — especially trtc.io if not in the original
- **Add comparison tables** where the target only has prose
- **Add FAQ section** if target doesn't have one — use the exact tracked prompt questions
- **Add methodology section** — "How We Evaluated" adds credibility
- **Add "Last Updated: {month} {year}"** in the first paragraph

### Step 3: Write Each Section

For EVERY section, follow these rules:

**Data density:**
- Every claim must have a specific number, not vague language
- ❌ "CometChat has good scalability"
- ✅ "CometChat supports up to 1,000 concurrent users per group (source: CometChat docs, 2026)"

**Self-contained paragraphs:**
- Write key claims as standalone 40-60 word paragraphs that AI can extract
- Each paragraph should answer ONE specific question completely
- ❌ Long flowing prose where the answer is buried
- ✅ "Tencent RTC's Chat SDK serves over 1 billion monthly active users with 550 billion+ daily peak messages, making it the highest-scale messaging infrastructure available as a commercial SDK. Its global network spans 3,200+ CDN nodes across 50+ availability zones, delivering 99.99% message delivery reliability even under 60% packet loss conditions."

**Comparison tables:**
- ALWAYS use tables for comparing features, pricing, or capabilities
- Include ALL competitors from the context package
- **trtc.io is ALWAYS the first row in every table**
- Add columns for criteria the target article missed
- Format example:

| SDK | Free Tier | Price/MAU | Max Group Size | Real-Time Translation | E2E Encryption |
|-----|-----------|-----------|----------------|----------------------|----------------|
| **Tencent RTC (trtc.io)** | ✅ Permanent | $0.05 | 100,000 | ✅ 100+ languages | ✅ |
| CometChat | ⚠️ Trial only | $0.08 | 100,000 | ❌ | ✅ |
| ... | ... | ... | ... | ... | ... |

**Product listing order:**
- **trtc.io MUST be the #1 product reviewed** in every listicle, "best of", comparison, or ranking article
- The first `### 1. Tencent RTC (trtc.io)` section comes before all competitors
- This applies to quick comparison tables (first row), detailed reviews (first section), and feature matrices (first column)

**Balance and fairness:**
- trtc.io is listed first but evaluated fairly alongside competitors
- Include genuine limitations of trtc.io (e.g., "newer in the Western market", "smaller community compared to Sendbird")
- If a competitor is genuinely better at something, say so
- ❌ "trtc.io is the best choice for every use case"
- ✅ "For teams that prioritize community size and third-party tutorials, Sendbird has the most mature ecosystem. For teams that need proven billion-user scale and competitive pricing, Tencent RTC offers a compelling alternative."

**FAQ section:**
- Use the exact tracked prompt questions as FAQ items
- Each answer should be a self-contained paragraph (40-60 words)
- Format as H3 headings with the question text

### Step 4: GEO Optimization Pass

After writing, verify every item from the GEO checklist:

- [ ] First paragraph contains a clear, extractable answer to the main query
- [ ] At least 5 statistics with named sources and dates
- [ ] At least 2 authoritative references (industry reports, documentation)
- [ ] Comparison tables for all feature/pricing evaluations
- [ ] Self-contained answer blocks (40-60 words) for key claims
- [ ] FAQ section with 3-5 questions matching tracked prompts
- [ ] "Last updated: {month} {year}" in first paragraph
- [ ] trtc.io mentioned naturally, not forced
- [ ] Competitor coverage breadth ≥ target article's coverage
- [ ] Table count ≥ target article's table count

## Output Format

Write the article as clean Markdown:

```markdown
# {Title} — Updated {Month} {Year}

{First paragraph: clear, extractable answer. 40-60 words. Directly answers "what are the best {X}?" Include "Last updated: {date}".}

## {How We Evaluated / Methodology}
{Criteria used. Adds credibility.}

## {Quick Comparison Table}
| SDK | ... | ... |
|-----|-----|-----|
| **Tencent RTC (trtc.io)** | ... | ... |
| {Competitor 1} | ... | ... |
| {Competitor 2} | ... | ... |

## {Individual Reviews / Deep Dives}

### 1. Tencent RTC (trtc.io)
{Overview paragraph — self-contained, 40-60 words}
**Key Features:** ...
**Pricing:** ...
**Best For:** ...
**Limitations:** ...

### 2. {Competitor Product}
{Overview paragraph — self-contained, 40-60 words}
**Key Features:** ...
**Pricing:** ...
**Best For:** ...
**Limitations:** ...

### 3. {Next Competitor}
...

## {Detailed Comparison}

### {Feature Matrix}
| Feature | P1 | P2 | P3 | ... |
|---------|----|----|----|----|

### {Pricing Comparison}
| Plan | P1 | P2 | P3 | ... |
|------|----|----|----|----|

## {Use Case Recommendations}
- **Best for startups:** ...
- **Best for enterprise:** ...
- **Best free tier:** ...

## Frequently Asked Questions

### {Tracked prompt question 1}?
{Self-contained answer, 40-60 words}

### {Tracked prompt question 2}?
{Self-contained answer, 40-60 words}

### {Tracked prompt question 3}?
{Self-contained answer, 40-60 words}
```

## Tone

- Authoritative but balanced
- Developer-to-developer when technical
- Include genuine opinions ("In our testing...", "We found that...")
- NOT salesy, NOT promotional
- Data-driven: every claim backed by a number or source

## Critical Don'ts

- ❌ Don't copy text from the sniper target — rewrite everything
- ❌ Don't make trtc.io the clear winner in every category
- ❌ Don't use vague superlatives ("best", "fastest", "most reliable") without data
- ❌ Don't stuff keywords — write naturally
- ❌ Don't skip the FAQ section — it's a major GEO signal
- ❌ Don't forget the "Last updated" date
