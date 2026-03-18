# Source Seed List

These are the known sources to scan on every run. The agent also discovers new sources via trending searches.

---

## Podcasts

| Podcast | Focus | Where to check |
|---------|-------|----------------|
| Oxide and Friends | Systems engineering, infrastructure, deep technical | oxide.computer/podcasts |
| Latent Space | AI engineering, practitioner content, LLM tooling | latent.space/podcast |
| Practical AI | Applied ML/AI, real-world use cases | changelog.com/practicalai |
| The Cognitive Revolution | AI research interviews, frontier models | thecognitiverevolution.com |
| Lex Fridman | Long-form AI/tech interviews (filter for AI episodes only) | lexfridman.com/podcast |
| AI Explained | Model analysis, benchmark breakdowns, reasoning | YouTube — AI Explained channel |

**When scanning podcasts:**
- Check for episodes published in the last 7 days
- Include episode title, duration, guest name, and key topics
- Flag episodes with practitioner guests (engineers, researchers) over commentators

---

## GitHub

### Trending
- Check GitHub Trending for repositories tagged: `ai`, `llm`, `machine-learning`, `agent`, `mcp`
- Filter by: daily and weekly trending
- Note: star count, primary language, and one-line description

### Specific Repos to Watch
| Repo | What to check |
|------|---------------|
| anthropics/claude-code | New releases, changelog updates |
| anthropics/anthropic-sdk-python | New features, breaking changes |
| anthropics/courses | New tutorials or labs |
| langchain-ai/langchain | Major releases, new integrations |
| run-llama/llama_index | Major releases, new features |
| ollama/ollama | New model support, performance updates |
| open-webui/open-webui | New features, integrations |
| modelcontextprotocol/servers | New MCP servers, updates |

**When scanning repos:**
- Check for commits/releases in the last 7 days
- Note: what changed, why it matters, star count delta if notable

---

## News & Blogs

| Source | URL pattern | What to look for |
|--------|-----------|-----------------|
| Hacker News | news.ycombinator.com | AI/ML posts with 100+ points |
| Anthropic Blog | anthropic.com/news | Any new posts |
| OpenAI Blog | openai.com/blog | Major announcements |
| Google DeepMind Blog | deepmind.google/discover | Research posts, model releases |
| Simon Willison | simonwillison.net | AI tooling posts (very high signal) |
| Latent Space Newsletter | latent.space | Weekly roundups |

**When scanning news:**
- Prioritize original research and launches over commentary
- Hacker News: check front page and search for "Show HN" + AI terms
- Blogs: check for posts in the last 7 days

---

## Reddit

| Subreddit | Focus |
|-----------|-------|
| r/LocalLLaMA | Local model running, quantization, new models |
| r/MachineLearning | Research papers, industry news |
| r/ClaudeAI | Claude-specific tooling, workflows, tips |

**When scanning Reddit:**
- Check top posts from the past week
- Filter for posts with 50+ upvotes
- Ignore memes, complaints, and support requests

---

## Newsletters

| Newsletter | Focus |
|-----------|-------|
| Latent Space | AI engineering weekly digest |
| TLDR AI | Daily AI news summary |
| The Batch (Andrew Ng) | Weekly AI news and education |

---

## Discovery Rules

On every run, also search for:
- New AI engineering podcasts or YouTube channels gaining traction
- New GitHub repos with 500+ stars created in the last month
- Blog posts from new authors appearing on HN or Reddit with high engagement
- New MCP servers or Claude Code plugins

Add any discoveries to the "Discovered Sources" section of the digest.
