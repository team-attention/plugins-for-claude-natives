# Session Wrap Plugin

A Claude Code plugin for comprehensive session wrap-up with multi-agent analysis.

## Features

- **Multi-Agent Analysis Pipeline**: 5 specialized agents analyze your session from different perspectives
- **2-Phase Architecture**: Parallel analysis followed by sequential validation
- **Documentation Updates**: Identify what should be added to CLAUDE.md and context.md
- **Automation Discovery**: Find patterns worth automating as skills/commands/agents
- **Learning Capture**: Extract insights, mistakes, and discoveries in TIL format
- **Follow-up Planning**: Prioritized task list for next session
- **Duplicate Prevention**: Validates proposals against existing content

## Installation

### Option 1: Plugin Directory

```bash
# Clone or copy to your plugins directory
git clone https://github.com/team-attention/plugins-for-claude-natives
cd plugins-for-claude-natives/plugins/session-wrap

# Or copy directly
cp -r session-wrap ~/.claude/plugins/
```

### Option 2: Direct Use

```bash
claude --plugin-dir /path/to/session-wrap
```

## Usage

### Basic Usage

```
/wrap
```

Runs the full wrap-up workflow:
1. Check git status
2. Phase 1: Run 4 analysis agents in parallel
3. Phase 2: Validate proposals for duplicates
4. Present results and let you choose actions
5. Execute selected actions

### Quick Commit

```
/wrap fix typo in README
```

When arguments are provided, creates a commit with that message directly.

## Architecture

```
Phase 1: Analysis (Parallel)
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ doc-updater  │ automation-  │ learning-    │ followup-    │
│              │ scout        │ extractor    │ suggester    │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┘
       └──────────────┴──────────────┴──────────────┘
                            │
                            ▼
Phase 2: Validation (Sequential)
┌─────────────────────────────────────────────────────────────┐
│                    duplicate-checker                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    User Selection
```

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `doc-updater` | sonnet | Analyze documentation update needs |
| `automation-scout` | sonnet | Detect automation opportunities |
| `learning-extractor` | sonnet | Extract learnings and mistakes |
| `followup-suggester` | sonnet | Suggest prioritized follow-up tasks |
| `duplicate-checker` | haiku | Validate proposals for duplicates |

## Skills

### session-wrap
Session wrap-up best practices, multi-agent orchestration patterns, 2-phase pipeline design guidance.

**Trigger phrases:** "session wrap-up", "wrap best practices", "multi-agent orchestration", "2-phase pipeline"

### history-insight
Claude Code 세션 히스토리를 분석하고 인사이트를 추출합니다.

**Trigger phrases:** "capture session", "save session history", "what we discussed", "today's work", "session history"

### session-analyzer
Post-hoc analysis tool for validating Claude Code session behavior against SKILL.md specifications.

**Trigger phrases:** "analyze session", "세션 분석", "evaluate skill execution", "check session logs"

## Directory Structure

```
session-wrap/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── commands/
│   └── wrap.md               # /wrap command
├── agents/
│   ├── doc-updater.md        # Documentation analysis
│   ├── automation-scout.md   # Automation detection
│   ├── learning-extractor.md # Learning capture
│   ├── followup-suggester.md # Task prioritization
│   └── duplicate-checker.md  # Validation
├── skills/
│   ├── session-wrap/
│   │   ├── SKILL.md          # Best practices guide
│   │   └── references/
│   │       └── multi-agent-patterns.md
│   ├── history-insight/
│   │   ├── SKILL.md          # Session history analysis
│   │   ├── scripts/
│   │   │   └── extract-session.sh
│   │   └── references/
│   │       └── session-file-format.md
│   └── session-analyzer/
│       ├── SKILL.md          # Post-hoc session validation
│       ├── scripts/
│       │   ├── extract-hook-events.sh
│       │   ├── extract-subagent-calls.sh
│       │   └── find-session-files.sh
│       └── references/
│           ├── analysis-patterns.md
│           └── common-issues.md
└── README.md
```

## When to Use

**Use `/wrap` when:**
- Ending a significant work session
- Before switching to a different project
- After completing a feature or bug fix
- When unsure what to document

**Skip when:**
- Very short session with trivial changes
- Only reading/exploring code
- Quick one-off question answered

## Integration with plugin-dev

When `automation-scout` recommends creating a new skill/command/agent, use:

```
/plugin-dev:create-plugin
```

This will guide you through creating a well-structured automation.

## References

- [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Azure AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)

## License

MIT
