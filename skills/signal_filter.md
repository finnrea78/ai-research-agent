# Skill: Signal Filter

## Purpose

This skill defines how to score, rank, and categorize raw findings from the source scanner into a curated set of high-signal items for the digest.

---

## Step 1: Score Each Finding

Apply three scoring dimensions to every raw finding:

### Relevance (0-10)

How closely does this match the user's focus areas in `context/topics.md`?

| Score | Criteria |
|-------|----------|
| 9-10 | Directly about Tier 1 topics (Claude Code, MCP, agent SDKs, LLM tooling) |
| 7-8 | Directly about Tier 2 topics (model releases, AI infra, open-source AI) |
| 5-6 | About Tier 3 topics (research papers with practical implications, notable launches) |
| 3-4 | Tangentially related to AI engineering |
| 0-2 | General tech news with weak AI connection |

### Signal Quality (0-10)

Is this noise or substance?

| Score | Criteria |
|-------|----------|
| 9-10 | Original research, major launch, deep technical analysis, practitioner-written |
| 7-8 | Solid tutorial, meaningful release, well-analyzed benchmark |
| 5-6 | Competent overview, minor release, decent commentary |
| 3-4 | Repackaged news, surface-level content, listicle |
| 0-2 | Hype piece, marketing content, AI-generated fluff |

### Timeliness (0-5)

How fresh is this?

| Score | Criteria |
|-------|----------|
| 5 | Published today or yesterday |
| 4 | Published 2-3 days ago |
| 3 | Published 4-5 days ago |
| 2 | Published this week |
| 1 | Published this month |
| 0 | Older than a month |

---

## Step 2: Apply Threshold

- **Total score = Relevance + Signal Quality + Timeliness** (max 25)
- **Threshold:** Items scoring **15 or higher** make the digest
- **Highlight threshold:** Items scoring **20 or higher** get highlight status

If fewer than 5 items pass the threshold, lower it to 12 and note that it was a quiet period.
If more than 20 items pass, raise the threshold to 18 to keep the digest focused.

---

## Step 3: Categorize

Sort passing items into these categories:

| Category | What goes here |
|----------|---------------|
| **Highlights** | Top 3-5 highest-scoring items (any source type). These lead the digest. |
| **Podcasts** | Podcast episodes that passed the filter |
| **Repos & Tools** | GitHub repos, tools, and frameworks |
| **News & Analysis** | Blog posts, articles, announcements |
| **Discovered Sources** | Items with `discovered: true` — new sources not in the seed list |

Within each category, sort by total score (highest first).

---

## Step 4: Enrich Top Items

For the **Highlights** (top 3-5 items), add extra context:

- **Why this matters:** 1-2 sentences explaining significance for AI practitioners
- **Key takeaway:** The single most important point
- **Action item:** What the reader might want to do (listen, read, try, watch)

For **Podcast** items, add:
- Recommended listen time if long (e.g., "Key segment: 23:00-45:00")
- Whether it's a must-listen or nice-to-have

---

## Step 5: Output

Pass the categorized and enriched findings to the `digest_writer` skill.

**Expected output structure:**

```
highlights:
  - [3-5 enriched items]
podcasts:
  - [filtered podcast items]
repos_and_tools:
  - [filtered GitHub items]
news_and_analysis:
  - [filtered news/blog items]
discovered:
  - [discovered source items]
metadata:
  scan_date: YYYY-MM-DD
  total_scanned: N
  total_passed: N
  threshold_used: 15 (or adjusted value)
```
