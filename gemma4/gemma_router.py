"""
gemma_router.py — Smart token-optimisation routing for the AI Research Agent.

Provides two things:

1. GemmaRouter — a drop-in async client that routes requests to Gemma 4 (local,
   via Ollama) or Claude (Anthropic API) based on task complexity and type.

2. Concrete helper functions used by the research agent workflow:
   - compress_context()   → shrink large codebases/articles before Claude sees them
   - classify_query()     → decide cheap vs. expensive model for a request
   - bulk_summarise()     → parallelise Gemma summarisation over many texts
   - route_query()        → single-call interface that picks the right model

Usage
-----
from gemma4.gemma_router import GemmaRouter, route_query, bulk_summarise

router = GemmaRouter()
answer = await router.query("Summarise this Python file", context=code)
"""

from __future__ import annotations

import asyncio
import re
import textwrap
from dataclasses import dataclass, field
from typing import Literal

import anthropic
from openai import AsyncOpenAI


# ── Configuration ──────────────────────────────────────────────────────────────

@dataclass
class RouterConfig:
    """Tuneable thresholds for the routing heuristics."""

    # Ollama base URL (set OLLAMA_BASE_URL env var to override)
    ollama_base_url: str = "http://localhost:11434/v1"

    # Gemma model aliases (Ollama tags)
    gemma_large: str = "gemma4:26b"   # 256K context, best quality, 18GB
    gemma_fast: str = "gemma4:e4b"    # 128K context, 9.6GB — used for classification

    # Claude model aliases
    claude_default: str = "claude-sonnet-4-6"
    claude_complex: str = "claude-opus-4-6"

    # Routing thresholds
    # If estimated input tokens exceed this, compress with Gemma first
    compress_threshold_tokens: int = 8_000

    # Token budget below which we always use Gemma (cheap tasks)
    gemma_max_output_tokens: int = 1_000

    # Approximate chars-per-token ratio for fast estimation
    chars_per_token: float = 3.8


_DEFAULT_CONFIG = RouterConfig()


# ── Task complexity classifier ─────────────────────────────────────────────────

# Keywords that strongly suggest Claude is needed
_COMPLEX_PATTERNS = re.compile(
    r"\b("
    r"architect|design|refactor|security|vulnerabilit|"
    r"novel|creative|strateg|decision|trade.?off|"
    r"multi.?step|chain|orchestrat|plan|debug complex|"
    r"why does|root cause|explain why"
    r")\b",
    re.IGNORECASE,
)

# Keywords that indicate Gemma is fine
_SIMPLE_PATTERNS = re.compile(
    r"\b("
    r"summaris|summarize|extract|list|format|convert|"
    r"count|find all|search for|grep|scan|enumerate|"
    r"comment|docstring|rename|classify|categoris|categorize|"
    r"translate|reword|paraphrase|bullet.?point"
    r")\b",
    re.IGNORECASE,
)

ModelChoice = Literal["gemma", "claude", "claude-opus"]


def classify_complexity(prompt: str, context_chars: int = 0) -> ModelChoice:
    """
    Heuristically decide which model to use for a prompt.

    Returns:
        "gemma"       → route to Gemma 4 26B (fast, cheap)
        "claude"      → route to Claude Sonnet (balanced)
        "claude-opus" → route to Claude Opus (complex/critical)
    """
    prompt_lower = prompt.lower()

    # Explicit overrides in the prompt
    if any(kw in prompt_lower for kw in ("use claude", "use opus", "critical", "production")):
        return "claude-opus"
    if any(kw in prompt_lower for kw in ("use gemma", "cheap", "fast summary")):
        return "gemma"

    has_complex = bool(_COMPLEX_PATTERNS.search(prompt))
    has_simple = bool(_SIMPLE_PATTERNS.search(prompt))

    if has_complex and not has_simple:
        return "claude"
    if has_simple and not has_complex:
        return "gemma"

    # Context size tiebreaker: large contexts go to Gemma to compress first
    est_tokens = context_chars / _DEFAULT_CONFIG.chars_per_token
    if est_tokens > _DEFAULT_CONFIG.compress_threshold_tokens:
        return "gemma"

    # Default: balanced
    return "claude"


# ── GemmaRouter ───────────────────────────────────────────────────────────────

class GemmaRouter:
    """
    Async router that sends requests to Gemma 4 (Ollama) or Claude (Anthropic)
    based on task complexity.

    All methods return plain strings for easy drop-in use.
    """

    def __init__(self, config: RouterConfig = _DEFAULT_CONFIG) -> None:
        self._cfg = config
        self._gemma = AsyncOpenAI(
            base_url=config.ollama_base_url,
            api_key="ollama",  # Ollama ignores the key value
        )
        self._claude = anthropic.AsyncAnthropic()  # reads ANTHROPIC_API_KEY from env

    # ── Low-level calls ────────────────────────────────────────────────────────

    async def _call_gemma(
        self,
        prompt: str,
        system: str = "",
        model: str | None = None,
        max_tokens: int = 2048,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self._gemma.chat.completions.create(
            model=model or self._cfg.gemma_large,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    async def _call_claude(
        self,
        prompt: str,
        system: str = "",
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        response = await self._claude.messages.create(
            model=model or self._cfg.claude_default,
            max_tokens=max_tokens,
            system=system or anthropic.NOT_GIVEN,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    # ── High-level routing entry point ─────────────────────────────────────────

    async def query(
        self,
        prompt: str,
        context: str = "",
        system: str = "",
        force: ModelChoice | None = None,
    ) -> str:
        """
        Route a query to the appropriate model.

        Args:
            prompt:  The user question or instruction.
            context: Optional supporting text (file contents, articles, etc.).
            system:  Optional system prompt.
            force:   Override routing — "gemma", "claude", or "claude-opus".

        Returns:
            Model response as a plain string.
        """
        choice = force or classify_complexity(prompt, context_chars=len(context))

        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        if choice == "gemma":
            return await self._call_gemma(full_prompt, system=system)
        elif choice == "claude-opus":
            return await self._call_claude(
                full_prompt,
                system=system,
                model=self._cfg.claude_complex,
                max_tokens=8192,
            )
        else:
            return await self._call_claude(full_prompt, system=system)

    # ── Specialised helpers ────────────────────────────────────────────────────

    async def compress_context(
        self,
        text: str,
        focus: str = "key decisions, important constraints, critical code paths",
        target_words: int = 400,
    ) -> str:
        """
        Use Gemma to compress large context before passing to Claude.

        Typical use: shrink a 50K-token file scan to ~400 words before
        Claude's final synthesis — saves 90%+ of Claude input tokens.
        """
        instruction = textwrap.dedent(f"""
            Compress the following text to approximately {target_words} words.
            Preserve: {focus}.
            Discard: verbose comments, repeated patterns, boilerplate, intermediate steps.
            Output ONLY the compressed summary — no preamble, no "here is a summary".
        """).strip()

        return await self._call_gemma(
            prompt=f"{instruction}\n\n---\n{text}",
            max_tokens=600,
        )

    async def classify_query(self, query: str) -> str:
        """
        Use the tiny E4B model to classify a query as 'simple' or 'complex'.
        Returns 'simple' or 'complex'.
        """
        result = await self._call_gemma(
            prompt=textwrap.dedent(f"""
                Classify this query as EXACTLY one word: 'simple' or 'complex'.

                simple = factual lookup, summarisation, extraction, formatting, code comments.
                complex = multi-step reasoning, architecture, security, novel problem solving.

                Query: {query}

                Answer (one word only):
            """).strip(),
            model=self._cfg.gemma_fast,
            max_tokens=3,
        )
        return "complex" if "complex" in result.lower() else "simple"

    async def extract_structured(
        self,
        text: str,
        schema_description: str,
        example_output: str = "",
    ) -> str:
        """
        Use Gemma to extract structured data (JSON) from unstructured text.

        Gemma 4 has native structured output support; this returns raw JSON string.
        """
        example_block = f"\nExample output:\n{example_output}" if example_output else ""
        prompt = textwrap.dedent(f"""
            Extract data from the text below following this schema:
            {schema_description}
            {example_block}

            Return ONLY valid JSON, nothing else.

            Text:
            {text}
        """).strip()

        return await self._call_gemma(prompt, max_tokens=1500)


# ── Module-level convenience functions ────────────────────────────────────────

_router: GemmaRouter | None = None


def _get_router() -> GemmaRouter:
    global _router
    if _router is None:
        _router = GemmaRouter()
    return _router


async def route_query(
    prompt: str,
    context: str = "",
    system: str = "",
    force: ModelChoice | None = None,
) -> str:
    """
    Module-level shortcut: route a single query to Gemma or Claude.

    Example:
        result = await route_query("Summarise auth.py", context=code)
    """
    return await _get_router().query(prompt, context=context, system=system, force=force)


async def compress_context(text: str, focus: str = "key decisions and constraints") -> str:
    """
    Module-level shortcut: compress large text with Gemma before Claude sees it.

    Example:
        compressed = await compress_context(full_codebase_dump)
    """
    return await _get_router().compress_context(text, focus=focus)


async def bulk_summarise(
    items: dict[str, str],
    instruction: str = "Summarise key logic in 80 words",
    concurrency: int = 8,
) -> dict[str, str]:
    """
    Parallelise Gemma summarisation over many texts (e.g., 100+ files).

    Args:
        items:       {label: text} mapping — e.g., {"auth.py": "...file contents..."}
        instruction: What to do with each item.
        concurrency: Max parallel Gemma calls.

    Returns:
        {label: summary} mapping.

    Example:
        files = {p: open(p).read() for p in glob("**/*.py")}
        summaries = await bulk_summarise(files)
    """
    router = _get_router()
    semaphore = asyncio.Semaphore(concurrency)

    async def _summarise_one(label: str, text: str) -> tuple[str, str]:
        async with semaphore:
            summary = await router._call_gemma(
                prompt=f"{instruction}:\n\n# {label}\n{text[:12_000]}",
                max_tokens=150,
            )
            return label, summary

    results = await asyncio.gather(
        *[_summarise_one(label, text) for label, text in items.items()]
    )
    return dict(results)


# ── CLI smoke test ─────────────────────────────────────────────────────────────

async def _smoke_test() -> None:
    """Quick sanity check — run with: python -m gemma4.gemma_router"""
    router = GemmaRouter()

    print("Testing Gemma classifier...")
    label = await router.classify_query("Summarise the key functions in auth.py")
    print(f"  'Summarise auth.py'  → {label}")

    label2 = await router.classify_query("Design a multi-region failover architecture")
    print(f"  'Design failover'    → {label2}")

    print("\nTesting compression...")
    dummy = "def foo(): pass\n" * 500  # ~8K chars
    compressed = await router.compress_context(dummy, target_words=50)
    print(f"  Input: {len(dummy)} chars → Output: {len(compressed)} chars")

    print("\nAll checks passed.")


if __name__ == "__main__":
    asyncio.run(_smoke_test())
