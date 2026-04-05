#!/usr/bin/env bash
# setup.sh — Bootstrap Gemma 4 integration for the AI Research Agent
#
# What this does:
#   1. Checks for Ollama and pulls Gemma 4 26B A4B
#   2. Installs Python dependencies (litellm, openai, mcp)
#   3. Starts the LiteLLM proxy in the background
#   4. Prints the environment variables needed to activate Gemma routing
#
# Usage:
#   chmod +x gemma4/setup.sh
#   ./gemma4/setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Gemma 4 Integration Setup ==="
echo ""

# ── 1. Check / Install Ollama ──────────────────────────────────────────────────
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✓ Ollama found: $(ollama --version 2>&1 | head -1)"
fi

# Ensure Ollama server is running
if ! curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama server..."
    ollama serve &
    sleep 3
fi

# ── 2. Pull Gemma 4 models ─────────────────────────────────────────────────────
echo ""
echo "Pulling Gemma 4 26B A4B (18GB, 256K context)..."
echo "This may take 10-20 minutes on first run."
ollama pull gemma4:26b

# Optional: also pull the smaller E4B for ultra-fast classification tasks
read -rp "Also pull Gemma 4 E4B (9.6GB, fast classifier)? [y/N] " pull_e4b
if [[ "${pull_e4b,,}" == "y" ]]; then
    ollama pull gemma4:e4b
fi

echo "✓ Model(s) pulled"

# ── 3. Install Python dependencies ────────────────────────────────────────────
echo ""
echo "Installing Python dependencies..."
pip install --quiet \
    "litellm[proxy]>=1.56.0" \
    "openai>=1.50.0" \
    "mcp>=1.0.0" \
    "fastmcp>=0.4.0" \
    "anthropic>=0.40.0"

echo "✓ Dependencies installed"

# ── 4. Start LiteLLM proxy ────────────────────────────────────────────────────
echo ""
LITELLM_PID_FILE="/tmp/litellm_gemma4.pid"

if [[ -f "$LITELLM_PID_FILE" ]] && kill -0 "$(cat "$LITELLM_PID_FILE")" 2>/dev/null; then
    echo "✓ LiteLLM proxy already running (PID $(cat "$LITELLM_PID_FILE"))"
else
    echo "Starting LiteLLM proxy on port 4000..."
    nohup litellm \
        --config "$SCRIPT_DIR/litellm_config.yaml" \
        --port 4000 \
        > /tmp/litellm_gemma4.log 2>&1 &
    echo $! > "$LITELLM_PID_FILE"
    sleep 3

    if curl -sf http://localhost:4000/health > /dev/null 2>&1; then
        echo "✓ LiteLLM proxy running (PID $(cat "$LITELLM_PID_FILE"))"
    else
        echo "✗ LiteLLM proxy failed to start. Check /tmp/litellm_gemma4.log"
        exit 1
    fi
fi

# ── 5. Print activation instructions ──────────────────────────────────────────
echo ""
echo "=== Gemma 4 routing is ready ==="
echo ""
echo "Add these exports to your shell (or .env) to activate:"
echo ""
echo "  export ANTHROPIC_BASE_URL=http://localhost:4000"
echo "  export ANTHROPIC_API_KEY=your-anthropic-api-key"
echo ""
echo "With these set, the Claude Agent SDK will route:"
echo "  model='haiku'   → Gemma 4 26B A4B (local, free)"
echo "  model='sonnet'  → Claude Sonnet 4.6"
echo "  model='opus'    → Claude Opus 4.6"
echo ""
echo "To stop the proxy:  kill \$(cat $LITELLM_PID_FILE)"
echo "Proxy logs:         tail -f /tmp/litellm_gemma4.log"
echo ""
echo "To test Gemma directly:"
echo "  curl http://localhost:11434/api/chat -d '{\"model\":\"gemma4:26b\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}'"
