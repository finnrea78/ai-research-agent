"""
gemma_mcp_server.py — MCP server that exposes Gemma 4 as tools for the Claude Agent SDK.

This is the "cleanest" integration path: Claude remains the autonomous orchestrator
and decides when to delegate to Gemma. No model routing tricks required.

Architecture:
    Claude Agent SDK (Claude as brain)
           ↓  MCP tool call
    This server (localhost subprocess)
           ↓  OpenAI-compatible call
    Ollama serving Gemma 4

Usage (in your agent code):
    options = ClaudeAgentOptions(
        mcp_servers={
            "gemma": {
                "command": "python",
                "args": ["/path/to/gemma4/gemma_mcp_server.py"]
            }
        }
    )

Or start manually for testing:
    python gemma4/gemma_mcp_server.py
"""

from __future__ import annotations

import asyncio
import json
import os
import textwrap

from openai import AsyncOpenAI

# fastmcp is the simplest way to build MCP servers in Python
# Install: pip install fastmcp
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit(
        "fastmcp not found. Install with: pip install fastmcp\n"
        "Or: pip install 'mcp[cli]'"
    )

# ── Config ─────────────────────────────────────────────────────────────────────

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
GEMMA_LARGE = os.environ.get("GEMMA_LARGE_MODEL", "gemma4:26b")   # 256K ctx
GEMMA_FAST = os.environ.get("GEMMA_FAST_MODEL", "gemma4:e4b")     # 128K ctx, fast

_gemma = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

mcp = FastMCP(
    "Gemma 4 Tools",
    instructions=textwrap.dedent("""
        Use these tools when you need to:
        - Compress or summarise large volumes of text cheaply
        - Perform bulk code review across many files
        - Extract structured JSON from unstructured content
        - Classify or triage content at low cost
        - Do OCR-style extraction from image descriptions

        These tools use Gemma 4 26B locally — they are fast, free, and handle
        up to 256K tokens of context. Use them to reduce the amount of content
        that needs to be processed by the main model.
    """).strip(),
)

# ── Helper ─────────────────────────────────────────────────────────────────────

async def _gemma_call(
    prompt: str,
    system: str = "",
    model: str = GEMMA_LARGE,
    max_tokens: int = 1024,
) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await _gemma.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.1,
    )
    return response.choices[0].message.content or ""


# ── Tools ──────────────────────────────────────────────────────────────────────

@mcp.tool()
async def summarise_text(
    text: str,
    focus: str = "key points, decisions, and important details",
    max_words: int = 200,
) -> str:
    """
    Summarise a large block of text using Gemma 4.

    Use this to compress large files, articles, or documents before passing
    them to the main model for analysis. Handles up to 256K tokens of input.
    Much cheaper than processing full text with the main model.

    Args:
        text:      The text to summarise (can be very large — up to 256K tokens).
        focus:     What aspects to preserve in the summary.
        max_words: Target length of the output summary.
    """
    prompt = textwrap.dedent(f"""
        Summarise the following text in approximately {max_words} words.
        Focus on: {focus}
        Output ONLY the summary — no preamble.

        ---
        {text[:200_000]}
    """).strip()

    return await _gemma_call(prompt, max_tokens=max_words * 2)


@mcp.tool()
async def bulk_summarise_files(files_json: str, instruction: str = "Summarise key logic") -> str:
    """
    Summarise multiple files in parallel using Gemma 4.

    Pass a JSON object mapping file paths to their contents.
    Returns a JSON object mapping each path to its summary.

    Use this when you need to process many files (10-500) and only need
    a high-level understanding of each — far cheaper than reading them all
    with the main model.

    Args:
        files_json:  JSON string: {"path/to/file.py": "file contents", ...}
        instruction: What to produce for each file (default: "Summarise key logic").
    """
    try:
        files: dict[str, str] = json.loads(files_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {e}"})

    semaphore = asyncio.Semaphore(6)  # max 6 parallel Gemma calls

    async def _one(path: str, content: str) -> tuple[str, str]:
        async with semaphore:
            summary = await _gemma_call(
                prompt=f"{instruction} for {path}:\n\n{content[:8_000]}",
                max_tokens=180,
            )
            return path, summary.strip()

    results = await asyncio.gather(*[_one(p, c) for p, c in files.items()])
    return json.dumps(dict(results), indent=2)


@mcp.tool()
async def extract_json(
    text: str,
    schema_description: str,
    example: str = "",
) -> str:
    """
    Extract structured JSON data from unstructured text using Gemma 4.

    Use for: parsing log files, extracting metadata from articles, pulling
    structured data from code comments, etc.

    Args:
        text:               The source text to extract from.
        schema_description: Natural language description of what to extract.
        example:            Optional example of the expected JSON output.
    """
    example_block = f"\nExample output:\n{example}" if example else ""
    prompt = textwrap.dedent(f"""
        Extract data from the text below.
        Schema: {schema_description}
        {example_block}
        Return ONLY valid JSON, nothing else.

        Text:
        {text[:50_000]}
    """).strip()

    return await _gemma_call(prompt, max_tokens=2000)


@mcp.tool()
async def code_review_batch(
    files_json: str,
    review_focus: str = "bugs, style issues, missing error handling, security concerns",
) -> str:
    """
    Review multiple code files for common issues using Gemma 4.

    Gemma 4 31B scores 80 on LiveCodeBench (vs Claude Haiku's 48.5), making it
    well-suited for routine code review tasks at a fraction of the cost.

    Use for: style checks, obvious bug detection, missing null checks,
    TODO/FIXME extraction, import audits, dead code detection.
    Reserve Claude for security audits and architectural reviews.

    Args:
        files_json:    JSON string: {"path/to/file.py": "file contents", ...}
        review_focus:  What to focus on during review.
    """
    try:
        files: dict[str, str] = json.loads(files_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {e}"})

    semaphore = asyncio.Semaphore(4)

    async def _review_one(path: str, content: str) -> tuple[str, str]:
        async with semaphore:
            review = await _gemma_call(
                system="You are a senior code reviewer. Be concise and actionable.",
                prompt=textwrap.dedent(f"""
                    Review this file for: {review_focus}

                    File: {path}
                    ```
                    {content[:10_000]}
                    ```

                    List findings as bullet points. If nothing notable, write "No issues found."
                """).strip(),
                max_tokens=400,
            )
            return path, review.strip()

    results = await asyncio.gather(*[_review_one(p, c) for p, c in files.items()])
    sections = [f"### {path}\n{review}" for path, review in results]
    return "\n\n".join(sections)


@mcp.tool()
async def classify_content(
    items_json: str,
    categories: str,
    output_format: str = "json",
) -> str:
    """
    Classify a batch of text items into categories using Gemma 4.

    Use for: triaging research findings, classifying log entries,
    tagging articles by topic, relevance scoring.

    Args:
        items_json:    JSON string: {"id": "text to classify", ...}
        categories:    Comma-separated list of valid categories.
        output_format: "json" (default) or "csv".
    """
    try:
        items: dict[str, str] = json.loads(items_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {e}"})

    cat_list = [c.strip() for c in categories.split(",")]

    semaphore = asyncio.Semaphore(8)

    async def _classify_one(item_id: str, text: str) -> tuple[str, str]:
        async with semaphore:
            result = await _gemma_call(
                prompt=textwrap.dedent(f"""
                    Classify the following text into EXACTLY ONE of these categories:
                    {", ".join(cat_list)}

                    Text: {text[:500]}

                    Answer with only the category name:
                """).strip(),
                model=GEMMA_FAST,
                max_tokens=10,
            )
            # Normalise: find best matching category
            result_clean = result.strip().lower()
            matched = next(
                (c for c in cat_list if c.lower() in result_clean),
                cat_list[-1],  # fallback to last category
            )
            return item_id, matched

    results = await asyncio.gather(*[_classify_one(k, v) for k, v in items.items()])
    classifications = dict(results)

    if output_format == "csv":
        lines = ["id,category"] + [f"{k},{v}" for k, v in classifications.items()]
        return "\n".join(lines)
    return json.dumps(classifications, indent=2)


@mcp.tool()
async def compress_for_context(
    text: str,
    purpose: str = "detailed analysis",
    target_tokens: int = 2000,
) -> str:
    """
    Compress large text to fit within a token budget using Gemma 4.

    Use this when you have content that is too large to fit in your context
    window but you need to preserve the essential information for further
    analysis. Gemma 4 handles 256K input tokens.

    Args:
        text:          The text to compress (up to 256K tokens supported).
        purpose:       What the compressed text will be used for (helps Gemma
                       decide what to preserve).
        target_tokens: Approximate token budget for the output (~4 chars/token).
    """
    target_words = int(target_tokens * 0.7)  # conservative estimate
    prompt = textwrap.dedent(f"""
        Compress the following text to approximately {target_words} words.
        This will be used for: {purpose}

        Preserve: decisions, constraints, error conditions, key data structures,
                  interfaces, configuration values, and anything unusual.
        Discard:  boilerplate, repeated patterns, verbose comments, examples
                  that duplicate other examples.

        Output ONLY the compressed text — no meta-commentary.

        ---
        {text[:200_000]}
    """).strip()

    return await _gemma_call(prompt, max_tokens=int(target_tokens * 1.2))


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
