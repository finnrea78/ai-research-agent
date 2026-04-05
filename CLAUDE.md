# AI Research Agent

## Purpose

This workspace is an AI agent for **curating daily AI engineering research digests**.

The agent scans podcasts, GitHub repos, news sites, blogs, and Reddit for high-signal AI engineering content. It filters and ranks findings using a scoring rubric, composes a formatted digest, and delivers it via email.

---

## Folder Structure

```
ai-research-agent/
├── CLAUDE.md                        ← You are here. Always read this first.
├── context/                         ← Configuration and preferences
│   ├── sources.md                   ← Seed list of sources to scan
│   ├── topics.md                    ← Focus areas and quality criteria
│   └── delivery_config.md           ← Email/messaging credentials (gitignored)
├── skills/                          ← Reusable research skills
│   ├── source_scanner.md            ← How to scan each source type
│   ├── signal_filter.md             ← How to score and rank findings
│   ├── digest_writer.md             ← How to compose the digest
│   ├── deliver.md                   ← How to send the digest
│   └── gemma4_router.md             ← How to use Gemma 4 for token-efficient bulk ops
├── gemma4/                          ← Gemma 4 integration (local open-weight model)
│   ├── setup.sh                     ← One-command bootstrap (Ollama + LiteLLM)
│   ├── litellm_config.yaml          ← Routes "haiku" alias → Gemma 4 locally
│   ├── gemma_router.py              ← Smart routing library (Gemma vs Claude)
│   └── gemma_mcp_server.py          ← MCP server: exposes Gemma tools to Claude
├── output/                          ← Daily digest archive (gitignored)
└── templates/
    └── email_template.html          ← HTML email layout
```

---

## Routing Table

**This is the most important section. For each task, read ONLY the listed files.**

| Task | Read these | Skip these | Use these skills |
|------|-----------|------------|-----------------|
| Scan sources | `context/sources.md`, `context/topics.md` | `context/delivery_config.md` | `source_scanner` |
| Filter & rank | Scan results (in memory), `context/topics.md` | `context/sources.md`, `context/delivery_config.md` | `signal_filter` |
| Write digest | Ranked findings (in memory) | `context/sources.md`, `context/delivery_config.md` | `digest_writer` |
| Deliver digest | Latest `output/YYYY-MM-DD-digest.md`, `context/delivery_config.md` | `context/sources.md`, `context/topics.md` | `deliver` |
| Full run | All `context/*.md` | Nothing | All skills in order |
| Bulk summarise / compress | Large raw content in memory | `context/delivery_config.md` | `gemma4_router` |
| Token optimisation | `skills/gemma4_router.md` | Everything else | `gemma4_router` |

**Rule:** Skills execute in sequence: `source_scanner` → `signal_filter` → `digest_writer` → `deliver`. Each skill passes its output to the next.

**Gemma 4 Rule:** When processing >10 sources or >8,000 tokens of raw content, read `skills/gemma4_router.md` and use Gemma 4 tools for bulk work before invoking Claude on the filtered subset. This reduces token costs by 80-95% on full digest runs.

---

## How to Start

- **"Scan sources"** → Read `context/sources.md` + `context/topics.md` → Use WebSearch to check each source → Return raw findings list
- **"Full run"** → Execute all 4 skills in sequence → End with delivered email + saved digest file
- **"Check [topic]"** → Read `context/topics.md` → Use WebSearch for that specific topic → Return quick summary (no email)
- **"Optimise tokens"** / **"use Gemma"** → Read `skills/gemma4_router.md` → Start `gemma4/setup.sh` if Gemma not yet running → Apply Gemma 4 routing to current task

---

## Output Format

Daily digests are saved as `output/YYYY-MM-DD-digest.md` with these sections:

1. **Highlights** — Top 3-5 items with "why this matters" context
2. **Podcasts** — New episodes worth listening to
3. **Repos & Tools** — Trending or notable AI repos (biased toward newer repos)
4. **News & Analysis** — Blog posts, articles, announcements
5. **AI in the Wild** — Startups, OSS projects, real-world AI deployments
6. **Discovered Sources** — New sources found during this scan (not in seed list)
