# GEO Strategy Reference for trtc.io

This document consolidates GEO (Generative Engine Optimization) best practices, content patterns, and platform-specific tactics for the trtc-geo-planner skill.

---

## 1. Priority Scoring Formula

### Blog Opportunity Score (0-100)

```
score = (citation_strength × 0.4) + (gap_severity × 0.3) + (intent_value × 0.2) + (content_feasibility × 0.1)
```

**citation_strength** (0-100): How much AI trusts this content pattern
- `Used total` of the top reference article for this topic
- Normalized: score = min(100, (used_total / max_used_total) × 100)

**gap_severity** (0-100): How big is our visibility gap
- If trtc.io position = "-" (absent): 100
- If position exists but visibility < 0.3: 70
- If position exists and visibility 0.3-0.6: 40
- If position exists and visibility > 0.6: 10

**intent_value** (0-100):
- transactional prompt: 100
- informational prompt: 60
- branded prompt (for us): 30

**content_feasibility** (0-100):
- Listicle/Comparison (easiest to create better version): 90
- How-To Guide: 80
- Article: 70
- Discussion/Opinion: 50
- Product Page: 40

### Community Opportunity Score (0-100)

```
score = (citation_frequency × 0.5) + (platform_reach × 0.3) + (prompt_coverage × 0.2)
```

**citation_frequency**: How often this community content gets cited by AI
**platform_reach**: Reddit > dev.to > Medium > Stack Overflow > Quora > HackerNews
**prompt_coverage**: How many tracked prompts would this community post influence

---

## 2. Content Type Mapping

Based on what AI platforms cite most, map each prompt to its ideal content type:

| Prompt Pattern | Best Content Type | Citation Share |
|---------------|-------------------|:-------------:|
| "Best [X]", "Top [X]" | Listicle | ~10% |
| "[X] vs [Y]", "compare" | Comparison | ~33% |
| "How to [X]" | How-To Guide | ~8% |
| "What is [X]" | Definitive Guide | ~15% |
| "[X] alternative", "instead of" | Alternative Page | ~5% |
| "[X] for [use case]" | Use-Case Guide | ~8% |
| "[X] pricing", "cost" | Pricing Comparison | ~5% |
| "[X] review" | Review/Analysis | ~10% |

---

## 3. Blog Article GEO Checklist

Every blog article produced by a downstream writing agent MUST include:

### Structure (Extractability)
- [ ] First paragraph contains a clear, direct answer to the target query (40-60 words)
- [ ] H2/H3 headings match natural query patterns
- [ ] Comparison tables for any "[X] vs [Y]" content
- [ ] Numbered/bulleted lists for process and feature content
- [ ] Self-contained answer blocks — each key paragraph works standalone
- [ ] FAQ section at the end with 3-5 questions from tracked prompts

### Authority (Citability)
- [ ] At least 5 statistics with named sources and dates
- [ ] At least 2 expert quotes or authoritative references
- [ ] Original data or unique analysis (not just aggregated from competitors)
- [ ] Specific numbers: "300ms latency" not "low latency"; "99.99% uptime" not "reliable"
- [ ] Named author with credentials in byline
- [ ] "Last updated: [date]" prominently displayed

### Presence (Discoverability)
- [ ] Article/BlogPosting schema markup
- [ ] FAQPage schema for FAQ section
- [ ] Internal links to relevant trtc.io product pages and docs
- [ ] External links to authoritative sources (shows objectivity)
- [ ] Open Graph and Twitter Card meta tags

### trtc.io-Specific Requirements
- [ ] **trtc.io is listed FIRST in every product listing, comparison table, and ranking** — always position #1 in the article order
- [ ] trtc.io positioned as a credible option alongside competitors (not the only option)
- [ ] Real product data from trtc.io docs (not generic claims)
- [ ] At least one unique trtc.io advantage backed by data
- [ ] Fair treatment of competitors (AI penalizes biased comparisons)
- [ ] Pricing information included when relevant (AI cites pages with visible pricing)

---

## 4. Community Post GEO Guidelines

### Reddit
- **Tone:** Authentic developer. First person. Share real experience.
- **Structure:** Short paragraphs. Use markdown formatting. Include TL;DR.
- **Mention strategy:** "I evaluated several options and here's what I found..."
- **Don't:** Link to your own content in the first post. Let the discussion develop.
- **Subreddits to target:** r/webdev, r/reactjs, r/programming, r/gamedev, r/livestreaming
- **Length:** 300-800 words

### dev.to
- **Tone:** Technical tutorial or experience report. Developer-to-developer.
- **Structure:** Full article format with code examples.
- **Mention strategy:** Include trtc.io in a comparison table alongside alternatives
- **Do:** Include actual code snippets showing integration
- **Length:** 1000-2000 words

### Medium
- **Tone:** Thought leadership or industry analysis.
- **Structure:** Narrative format with data points.
- **Mention strategy:** Reference trtc.io as part of market analysis
- **Do:** Use a personal publication, not the company one
- **Length:** 1500-2500 words

### Stack Overflow
- **Tone:** Strictly helpful. Answer the question first.
- **Mention strategy:** Only mention trtc.io if directly relevant to the solution
- **Do:** Provide working code examples
- **Don't:** Anything that looks like marketing

### GitHub
- **Tone:** Code-first. README-driven.
- **Content:** Sample projects, integration guides, SDK comparisons
- **Mention strategy:** Comparative benchmarks or multi-SDK demos
- **Do:** Include actionable code people can clone and run

---

## 5. Platform-Specific Citation Factors

### Google AI Overviews (45% of Google searches)
- Schema markup = #1 lever (30-40% visibility boost)
- Only 15% overlap with traditional Top 10 — structured content from lower-ranked pages CAN get cited
- Authoritative citations in content = 132% visibility boost
- Authoritative tone = 89% boost
- E-E-A-T signals heavily weighted

### ChatGPT
- Domain authority = 40% of citation determination
- Content quality = 35%
- Platform trust = 25%
- Content updated within 30 days = 3.2x more citations
- Content-answer fit = 55% of citation likelihood (match ChatGPT's response style)
- Wikipedia = 7.8% of all citations, Reddit = 1.8%

### Perplexity
- FAQ Schema (JSON-LD) = significant citation boost
- Self-contained paragraphs = preferred for extraction
- PDF documents = prioritized (publish whitepapers publicly)
- Publishing velocity matters more than keyword targeting
- Curated authoritative domain lists get ranking boosts

### Microsoft Copilot
- Bing index required (submit to Bing Webmaster Tools)
- Page speed < 2 seconds
- LinkedIn and GitHub presence = unique ranking boosts
- IndexNow protocol for faster indexing

### Claude
- Brave Search backend (verify presence at search.brave.com)
- Extremely selective — lowest citation rate
- Factual density is king: specific numbers, named sources, dated statistics
- Precision and accuracy rewarded over comprehensiveness

---

## 6. Competitive Landscape Context (trtc.io Chat SDK)

### Key Competitors (by AI citation frequency)
1. **CometChat** — Dominates listicle content (Used 72.8%), blog-first strategy
2. **GetStream** — Strong in technical docs (Used 46.1%)
3. **Sendbird** — Frequently appears as #1 in prompt results
4. **Ably** — Corporate content strategy (Used 50.5%)
5. **MirrorFly** — Active in comparison/alternative content
6. **Twilio/Twilio** — Legacy presence, migration narrative opportunity
7. **Agora** — Direct RTC competitor
8. **PubNub** — Real-time messaging specialist

### trtc.io Current AI Visibility
- Domain Used: ~7.3% (ranked ~19th)
- Most competitors are 5-10x more visible
- Primary gap: Listicle and Comparison content — competitors have dozens of these, trtc.io has very few
- trtc.io strengths not being leveraged in AI search: scale (10B MAU), reliability (99.99%), global infrastructure (3200+ nodes), competitive pricing

### Content Gap Summary
- Competitors dominate "best chat SDK" queries with listicles that don't mention trtc.io
- Reddit/dev.to discussions rarely include trtc.io
- trtc.io has strong product pages but weak blog/community presence for AI citation
