# AI Research Agent

A Claude Code-orchestrated agent that curates daily digests of AI engineering content. No framework code — just markdown skills, context files, and a routing table.

## What It Does

1. **Scans** podcasts, GitHub repos, Hacker News, blogs, and Reddit for AI engineering content
2. **Filters** using a 25-point scoring system (relevance + signal quality + timeliness)
3. **Writes** a daily digest with "why this matters" context for each item
4. **Delivers** via Gmail and saves a markdown archive

## Setup

### 1. Clone and open in Claude Code

```bash
cd ~/Developer/ai-research-agent
claude
```

### 2. Configure email delivery

Edit `context/delivery_config.md` with your email address.

Authenticate the Gmail MCP server in Claude Code when prompted.

### 3. Customize sources and topics

- Edit `context/sources.md` to add/remove sources
- Edit `context/topics.md` to adjust focus areas and quality criteria

## Usage

### Manual run

Open the repo in Claude Code and say:

```
full run
```

### Scheduled runs with /loop

```
/loop 12h full run
```

Runs every 12 hours while Claude Code is open.

### Cron job (runs without Claude Code open)

```bash
0 7 * * * cd ~/Developer/ai-research-agent && claude -p "full run"
```

## Architecture

This uses the "folder-as-workspace" pattern:

```
CLAUDE.md           → Router (read first, maps tasks to files)
context/            → Configuration (sources, topics, delivery)
skills/             → Reusable processes (scan, filter, write, deliver)
output/             → Daily digest archive
templates/          → HTML email template
```

No Python, no TypeScript, no dependencies. Just Claude Code reading markdown instructions and executing them.

## Customization

- **Add a source:** Edit `context/sources.md`
- **Change focus areas:** Edit `context/topics.md`
- **Adjust filtering:** Edit `skills/signal_filter.md` (thresholds and scoring rubric)
- **Change email format:** Edit `templates/email_template.html`
