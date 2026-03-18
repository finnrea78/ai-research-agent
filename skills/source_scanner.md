# Skill: Source Scanner

## Purpose

This skill defines the step-by-step process for scanning all configured sources to find recent AI engineering content.

---

## Step 1: Load Source Configuration

Read `context/sources.md` to get the full list of sources to scan.
Read `context/topics.md` to understand what topics are relevant.

---

## Step 2: Scan Podcasts

For each podcast in the seed list:

1. Use **WebSearch** to search: `"[podcast name]" latest episode [current month] [current year]`
2. Check the podcast's website or feed for recent episodes
3. For each episode published in the last 7 days, record:

```
- title: Episode title
- podcast: Podcast name
- date: YYYY-MM-DD
- url: Link to episode
- duration: Episode length (if available)
- guest: Guest name (if applicable)
- topics: Key topics discussed
- snippet: 1-2 sentence summary of what's covered
- source_type: podcast
```

**Priority signals for podcasts:**
- Practitioner guests (engineers, researchers at labs) > commentators
- Topics matching Tier 1 focus areas > general AI discussion
- Episodes with show notes or timestamps > episodes without

---

## Step 3: Scan GitHub

### Trending Repos
1. Use **WebSearch** to search: `github trending [language] today` for Python, TypeScript, Rust
2. Also search: `github trending AI LLM agent MCP`
3. For each relevant repo found, record:

```
- title: repo-owner/repo-name
- url: GitHub URL
- stars: Star count
- language: Primary language
- description: Repo description
- created: When the repo was created (new vs established)
- snippet: What it does and why it's notable
- source_type: github
```

### Watched Repos
1. For each repo in the "Specific Repos to Watch" list in `context/sources.md`:
2. Use **WebSearch** to search: `"[repo name]" release OR changelog OR update site:github.com [current month]`
3. Only record if there's been activity in the last 7 days

---

## Step 4: Scan News & Blogs

For each news source in the seed list:

1. Use **WebSearch** to search: `site:[source URL] [current month] [current year]`
2. For Hacker News: search `site:news.ycombinator.com AI OR LLM OR Claude OR agent [current month]`
3. For each relevant post found, record:

```
- title: Article title
- author: Author name
- date: YYYY-MM-DD
- url: Link to article
- snippet: 1-2 sentence summary
- engagement: Points/upvotes if available
- source_type: news
```

**Priority signals for news:**
- Original content > aggregated summaries
- Posts with code examples or benchmarks > opinion pieces
- High engagement (100+ HN points, many comments) > low engagement

---

## Step 5: Scan Reddit

For each subreddit in the seed list:

1. Use **WebSearch** to search: `site:reddit.com/r/[subreddit] [current month] [current year]`
2. Look for top posts from the past week with 50+ upvotes
3. For each relevant post found, record:

```
- title: Post title
- subreddit: r/SubredditName
- date: YYYY-MM-DD
- url: Reddit link
- upvotes: Upvote count
- snippet: Key takeaway or summary
- source_type: reddit
```

---

## Step 6: Discovery Search

Search for content NOT in the seed list:

1. Use **WebSearch** for broad discovery queries:
   - `"AI engineering" podcast new [current month] [current year]`
   - `"MCP server" new github [current month]`
   - `"Claude Code" tips OR workflow OR tutorial [current month]`
   - `"LLM agent" framework launch [current month]`
2. For each new source found, record the same fields as above plus:

```
- discovered: true
- discovery_query: The search query that found it
```

---

## Step 7: Compile Raw Findings

Combine all findings into a single list. Pass this list to the `signal_filter` skill.

**Expected output:** A list of 20-50 raw findings across all source types.

If fewer than 10 findings are found, broaden search queries and try again.
If more than 50 findings are found, that's fine — the signal filter will pare it down.

---

## Parallel Scanning

When running a full scan, launch searches in parallel where possible:
- Podcast searches can all run in parallel
- GitHub trending + watched repos can run in parallel
- News searches can all run in parallel
- Reddit searches can all run in parallel

Discovery searches should run AFTER the main scan, so you know what's already been found.
