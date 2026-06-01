# Agent Council

**[한국어 버전 (Korean)](./README.ko.md)**

> A skill that gathers opinions from multiple AI CLIs (Codex, Gemini, ...) and lets a configurable Chairman synthesize a conclusion.
> Inspired by [Karpathy's LLM Council](https://github.com/karpathy/llm-council)

## Key Difference from LLM Council

**No additional API costs!**

Unlike Karpathy's LLM Council which directly calls each LLM's API (incurring costs), Agent Council uses your installed AI CLIs (Claude Code, Codex CLI, Gemini CLI, ...). This is especially useful if you mainly use one host CLI and occasionally consult others via subscriptions.

Skills are much simpler and more reproducible than MCP. We recommend installing via npx and customizing it yourself!

## Demo

https://github.com/user-attachments/assets/c550c473-00d2-4def-b7ba-654cc7643e9b

## How it Works

Agent Council implements a 3-stage process for gathering AI consensus:

**Stage 1: Initial Opinions**
All configured AI agents receive your question simultaneously and respond independently.

**Stage 2: Response Collection**
Responses from each agent are collected and displayed to you in a formatted view.

**Stage 3: Chairman Synthesis**
Your host agent (Claude Code / Codex CLI / etc.) acts as the Chairman by default (`role: auto`), synthesizing all opinions into a final recommendation. Optionally, you can configure a Chairman CLI command to run synthesis inside `council.sh`.

## Setup

### Option A: Install via npx (Recommended)

```bash
npx github:team-attention/agent-council
```

This copies the skill files to your current project directory.
If you upgrade Agent Council and hit a runtime error like `Missing runtime dependency: yaml`, re-run the installer command above to refresh your installed skill files.

By default, the installer auto-detects whether to install for Claude Code (`.claude/`) and/or Codex CLI (`.codex/`) based on what’s available on your machine and in the repo.

Installed paths:
- `.claude/skills/agent-council/` (Claude Code)
- `.codex/skills/agent-council/` (Codex CLI)

Optional (Codex repo skill):
```bash
npx github:team-attention/agent-council --target codex
```

Other targets:
```bash
npx github:team-attention/agent-council --target claude
npx github:team-attention/agent-council --target both
```

The generated `council.config.yaml` includes only detected member CLIs (e.g. `claude`, `codex`, `gemini`) and avoids adding the host target as a member. This filtering happens only at initial generation; later edits will not auto-remove missing CLIs.

### Option B: Install via Claude Code Plugin (Claude Code only)

```bash
# Add the marketplace
/plugin marketplace add team-attention/plugins-for-claude-natives

# Install the plugin
/plugin install agent-council@plugins-for-claude-natives
```

Note (Plugin installs): **Agent Council requires Node.js**, and Claude Code plugins can’t bundle or auto-install Node for you. Install Node separately (e.g. `brew install node` on macOS).

### 2. Install Agent CLIs

Install the CLIs listed under `council.members` in your `council.config.yaml` (template includes `claude`, `codex`, `gemini`):

```bash
# Anthropic Claude Code
# https://claude.ai/code

# OpenAI Codex CLI
# https://github.com/openai/codex

# Google Gemini CLI
# https://github.com/google-gemini/gemini-cli
#
# Note: the Gemini CLI is being retired for free/Pro/Ultra users (2026-06-18) in favor
# of the Antigravity CLI (`agy`). If `gemini` is missing but `agy` is installed, the
# `gemini` member transparently runs `agy --dangerously-skip-permissions -p` instead.
# Install agy: curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Verify each member CLI:
```bash
command -v claude
command -v codex
command -v gemini
```

### 3. Configure Council Members (Optional)

Edit the generated config in your installed skill directory:
- `.claude/skills/agent-council/council.config.yaml`
- `.codex/skills/agent-council/council.config.yaml`

```yaml
council:
  chairman:
    role: "auto" # auto|claude|codex|gemini|...
    # command: "codex exec" # optional: run Stage 3 inside council.sh

  members:
    - name: codex
      command: "codex exec"
      emoji: "🤖"
      color: "BLUE"

    - name: gemini
      command: "gemini"
      emoji: "💎"
      color: "GREEN"

    # Add more agents as needed
    # - name: grok
    #   command: "grok"
    #   emoji: "🚀"
    #   color: "MAGENTA"
```

## Usage

### Via your host agent (Claude Code / Codex CLI)

Ask your host agent to summon the council:

```
"Let's hear opinions from other AIs"
"Summon the council"
"Review this from multiple perspectives"
"Ask codex and gemini for their opinions"
```

### Direct Script Execution

```bash
JOB_DIR=$(.codex/skills/agent-council/scripts/council.sh start "Your question here")
.codex/skills/agent-council/scripts/council.sh status --text "$JOB_DIR"
.codex/skills/agent-council/scripts/council.sh results "$JOB_DIR"
.codex/skills/agent-council/scripts/council.sh clean "$JOB_DIR"
```

Tip: add `--verbose` to `status --text` to include per-member lines.
Tip: use `status --checklist` for a compact checkbox view (handy in Codex/Claude tool cells).
Tip: use `wait` to block until meaningful progress without spamming tool cells (prints JSON, persists a cursor automatically; auto-batches to a small number of updates (typically ~5–10); `--bucket 1` for every completion).

One-shot (runs job → waits → prints results → cleans):

```bash
.codex/skills/agent-council/scripts/council.sh "Your question here"
```

Note: In host-agent tool UIs (Codex CLI / Claude Code), one-shot does **not** block. It returns a single `wait` JSON payload so the host agent can update native plan/todo UIs. Continue with `wait` → native UI update → `results` → `clean`.

#### Progress

- In a real terminal, one-shot prints periodic progress lines as members complete.
- In host-agent tool UIs, one-shot returns `wait` JSON (so the host can update native plan/todo UIs).
- Job mode is still available for scripting (`start` → `status` → `results` → `clean`).

## Example

```
User: "React vs Vue for a new dashboard project - summon the council"

Host agent (Claude Code / Codex CLI):
1. Executes council.sh to collect opinions from configured members (e.g., Codex, Gemini)
2. Displays each agent's perspective
3. Synthesizes as Chairman:
   "Based on the council's input, considering your dashboard's
   data visualization needs and team's familiarity, I recommend..."
```

## Project Structure

```
agent-council/
├── .claude-plugin/
│   └── marketplace.json     # Marketplace config (Claude Code only)
├── bin/
│   └── install.js           # npx installer
├── skills/
│   └── agent-council/
│       ├── SKILL.md         # Skill documentation
│       └── scripts/
│           ├── council.sh       # Execution script
│           ├── council-job.sh   # Background job runner (pollable)
│           ├── council-job.js   # Job runner implementation
│           └── council-job-worker.js # Per-member worker
├── council.config.yaml      # Council member configuration
├── README.md                # This file
├── README.ko.md             # Korean documentation
└── LICENSE
```

## Notes

- Response time depends on the slowest agent (parallel execution)
- Do not share sensitive information with the council
- Agents run in parallel by default for faster responses
- Subscription plans for each CLI tool are required (no additional API costs)

## Contributing

Contributions are welcome! Feel free to:
- Add support for new AI agents
- Improve the synthesis process
- Enhance the configuration options

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Credits

- Inspired by [Karpathy's LLM Council](https://github.com/karpathy/llm-council)
- Built for [Claude Code](https://claude.ai/code) and [Codex CLI](https://github.com/openai/codex)
