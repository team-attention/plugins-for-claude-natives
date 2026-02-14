# Dev

> Developer workflow tools: community scanning and technical decision-making.

## Skills

### `/dev-scan` — Community Opinion Scanner

Scans 4 major development communities simultaneously (Reddit, Hacker News, Dev.to, Lobsters) and synthesizes consensus opinions, controversies, and notable perspectives.

```
"What do developers think about Bun?"
"Community opinions on microservices"
```

### `/tech-decision` — Technical Decision Analysis

Systematic 4-phase workflow for technology choices:

1. **Problem Definition** — Clarify topic, options, evaluation criteria
2. **Parallel Information Collection** — Run multiple agents simultaneously
3. **Trade-off Analysis** — Synthesize findings into structured pros/cons
4. **Final Report** — Conclusion-first report with evidence and confidence ratings

```
"React vs Vue for a new dashboard?"
"Which state management library should we use?"
"Monolith vs microservices?"
```

## Agents

| Agent | Role |
|-------|------|
| `codebase-explorer` | Analyze existing codebase for patterns and constraints |
| `docs-researcher` | Research official documentation and best practices |
| `tradeoff-analyzer` | Structured pros/cons comparison |
| `decision-synthesizer` | Conclusion-first final report |

## Setup

```bash
# Add the marketplace
/plugin marketplace add team-attention/plugins-for-claude-natives

# Install the plugin
/plugin install dev@plugins-for-claude-natives
```

## Project Structure

```
dev/
├── CLAUDE.md
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── codebase-explorer.md
│   ├── docs-researcher.md
│   ├── tradeoff-analyzer.md
│   └── decision-synthesizer.md
└── skills/
    ├── dev-scan/
    │   └── SKILL.md
    └── tech-decision/
        ├── SKILL.md
        └── references/
            ├── evaluation-criteria.md
            └── report-template.md
```

## License

MIT License
