# Skill: Gemma 4 Router

## Purpose

Use Gemma 4 (a local open-weight model) to handle bulk, cheap, or large-context tasks
within the research agent workflow — dramatically reducing Claude API token spend
without sacrificing quality on tasks where Gemma is equally capable.

**When to load this skill:** Any time you are:
- Processing more than ~10 files or articles in a single run
- Receiving a context larger than ~8,000 tokens
- Doing bulk extraction, classification, or summarisation
- Running a full digest scan (source_scanner → signal_filter → digest_writer pipeline)

---

## Cost Context

| Model | Input $/1M | Output $/1M | Best for |
|---|---|---|---|
| Claude Opus 4.6 | $5.00 | $25.00 | Complex reasoning, architecture, safety |
| Claude Sonnet 4.6 | $3.00 | $15.00 | Default workhorse |
| Gemma 4 26B (local) | $0.00 | $0.00 | Bulk ops, summarisation, extraction |
| Gemma 4 26B (OpenRouter) | $0.13 | $0.40 | Same, when local GPU unavailable |

For a typical full digest run scanning 30-50 sources, routing bulk work to Gemma
reduces Claude costs by **80-95%**.

---

## Integration Architecture

Three ways Gemma integrates with this agent:

### 1. MCP Server (recommended — no config changes needed)

Gemma runs as a subprocess MCP server. Claude autonomously calls its tools when
appropriate. Launch with:

```bash
# In ClaudeAgentOptions:
mcp_servers={
    "gemma": {
        "command": "python",
        "args": ["gemma4/gemma_mcp_server.py"]
    }
}
```

Available tools:
- `summarise_text` — compress any text to a target word count
- `bulk_summarise_files` — parallelise summaries across many files/articles
- `extract_json` — pull structured data from unstructured content
- `code_review_batch` — routine code review across many files
- `classify_content` — batch triage/categorisation
- `compress_for_context` — shrink large context to a token budget

### 2. LiteLLM Proxy (seamless model aliasing)

Routes Claude Agent SDK's `model="haiku"` to Gemma 4. Zero changes to agent code.

```bash
# Start proxy
litellm --config gemma4/litellm_config.yaml --port 4000

# Activate routing
export ANTHROPIC_BASE_URL=http://localhost:4000
```

With this active, subagents using `model="haiku"` automatically use Gemma 4.

### 3. Direct Python API (for custom orchestration)

```python
from gemma4.gemma_router import route_query, compress_context, bulk_summarise

# Route a single query
answer = await route_query("Summarise this article", context=article_text)

# Compress before passing to Claude
compressed = await compress_context(big_document)
claude_response = await claude.messages.create(...)

# Summarise many files in parallel
summaries = await bulk_summarise({"file1.py": code1, "file2.py": code2})
```

---

## When to Use Gemma vs Claude

### Use Gemma 4 for:
- Reading and summarising source articles (source_scanner phase)
- Extracting metadata from raw search results
- First-pass relevance scoring (signal_filter pre-triage)
- Compressing multiple sources into a unified context
- Generating initial digest drafts from structured summaries
- Any task described as "scan all", "list all", "extract from", "classify"

### Use Claude for:
- Final quality scoring (signal_filter ranking decisions)
- Writing polished digest prose (digest_writer)
- Email subject line and highlights (high-judgment tasks)
- Multi-source synthesis that requires genuine reasoning
- Any "why this matters" context requires Claude's depth

---

## Recommended Workflow for Full Digest Run

```
1. source_scanner  →  Gemma 4 MCP tool: bulk_summarise_files
                       (compress all raw articles/posts to ~100 words each)

2. signal_filter   →  Gemma 4 MCP tool: classify_content
                       (pre-triage: "high_signal" | "medium" | "skip")
                   →  Claude: final ranking of high_signal items only

3. digest_writer   →  Gemma 4: first-pass draft from structured summaries
                   →  Claude: polish highlights, "why this matters" context

4. deliver         →  Claude only (email composition, subject line)
```

This structure means Claude only ever sees the small, high-signal subset.

---

## Setup

```bash
# One-time setup (installs Ollama, pulls Gemma 4 26B, starts LiteLLM)
./gemma4/setup.sh
```

Requirements:
- 18GB disk space (Gemma 4 26B model)
- 16GB RAM (runs on CPU, ~5 tok/s) or 16GB VRAM GPU (fast inference)
- Python 3.11+, `pip install fastmcp openai litellm`

---

## Gemma 4 Model Quick Reference

| Variant | Size | Context | RAM needed | Use for |
|---|---|---|---|---|
| E2B | 7.2GB | 128K | 8GB | Audio, ultra-light tasks |
| E4B | 9.6GB | 128K | 8GB | Classification, triage |
| 26B A4B | 18GB | 256K | 16GB | **Recommended default** |
| 31B | 20GB | 256K | 24GB | Max quality (RTX 4090) |

The 26B A4B (Mixture-of-Experts) runs at ~4B parameter speed while producing
near-31B quality. It is the best cost-quality choice for this workflow.

---

## Key Technical Facts (for context-aware decisions)

- **License**: Apache 2.0 — fully permissive, commercial use OK
- **Benchmarks**: Gemma 4 31B scores 80 on LiveCodeBench (Claude Haiku: 48.5)
- **Context**: 256K tokens on 26B and 31B variants
- **Thinking mode**: Supported via `<|think|>` system prompt token
- **Function calling**: Native support via vLLM (`--tool-call-parser gemma4`)
- **Multimodal**: All variants support image input; E2B/E4B also support audio
- **Released**: April 3, 2026 by Google DeepMind
