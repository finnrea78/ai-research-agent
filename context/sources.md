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
| Meta AI Blog | ai.meta.com/blog | Model releases, research papers |
| Microsoft Research Blog | microsoft.com/en-us/research/blog | AI research, tooling |
| Mistral Blog | mistral.ai/news | Model releases, benchmarks |
| Cohere Blog | cohere.com/blog | Enterprise AI, model releases |
| xAI Blog | x.ai/blog | Model releases, Grok updates |
| NVIDIA AI Blog | blogs.nvidia.com | GPU, inference, training |
| AWS AI Blog | aws.amazon.com/blogs/machine-learning | Cloud AI services |
| Databricks Blog | databricks.com/blog | Data + AI platform, MLOps |
| Hugging Face Blog | huggingface.co/blog | Open-source models, libraries |
| a16z AI | a16z.com/ai | AI market analysis, investment thesis |
| Sequoia AI | sequoiacap.com (filter AI) | AI market perspectives |
| State of AI (Nathan Benaich) | stateof.ai | Annual report, updates |

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

## AI in the Wild

Sources for AI startup activity, OSS project launches, and real-world business deployments.

| Source | URL pattern | What to look for |
|--------|-----------|-----------------|
| TechCrunch AI | techcrunch.com/category/artificial-intelligence | Funding rounds, startup launches |
| Product Hunt AI | producthunt.com (filter: AI, ML) | New AI product launches |
| CB Insights AI | cbinsights.com/research/artificial-intelligence | Market maps, funding data |
| HBR / MIT Sloan AI | hbr.org, sloanreview.mit.edu | Enterprise AI deployments, ROI analysis |

**When scanning AI in the Wild:**
- Prioritise concrete outcomes over announcements (revenue, users, deployment scale)
- Funding rounds: only Series A+ or pre-seed/seed if the team or tech is notable
- OSS projects: must have a clear mission, not just a bare repo
- Business deployments: only include if they share specifics (metrics, architecture, lessons)

---

## Discovery Rules

On every run, also search for:
- New AI engineering podcasts or YouTube channels gaining traction
- New GitHub repos with 500+ stars created in the last month
- New GitHub repos with 100+ stars if created in the last 90 days (freshness exception)
- Blog posts from new authors appearing on HN or Reddit with high engagement
- New MCP servers or Claude Code plugins
- New AI startups with notable funding or launches this month
- Open-source AI projects with a mission gaining traction
- Real-world AI deployment case studies published this month

Add any discoveries to the "Discovered Sources" section of the digest.
