---
name: session-wrap
description: This skill should be used when the user asks to "wrap up session", "end session", "session wrap", "/wrap", "document learnings", "what should I commit", or wants to analyze completed work before ending a coding session.
version: 2.0.0
---

# Session Wrap Skill

Comprehensive session wrap-up workflow with multi-agent analysis.

## Execution Flow

```
┌─────────────────────────────────────────────────────┐
│  1. Check Git Status                                │
├─────────────────────────────────────────────────────┤
│  2. Phase 1: 4 Analysis Agents (Parallel)           │
│     ┌─────────────────┬─────────────────┐           │
│     │  doc-updater    │  automation-    │           │
│     │  (docs update)  │  scout          │           │
│     ├─────────────────┼─────────────────┤           │
│     │  learning-      │  followup-      │           │
│     │  extractor      │  suggester      │           │
│     └─────────────────┴─────────────────┘           │
├─────────────────────────────────────────────────────┤
│  3. Phase 2: Validation Agent (Sequential)          │
│     ┌───────────────────────────────────┐           │
│     │       duplicate-checker           │           │
│     │  (Validate Phase 1 proposals)     │           │
│     └───────────────────────────────────┘           │
├─────────────────────────────────────────────────────┤
│  4. Integrate Results & AskUserQuestion             │
├─────────────────────────────────────────────────────┤
│  5. Execute Selected Actions                        │
└─────────────────────────────────────────────────────┘
```

## Step 1: Check Git Status (only if this is a git repo)

Not every working directory is a git repository — knowledge vaults, note
directories, and config trees often are not. Probe first, and skip this step
entirely when the probe fails.

```bash
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git status --short
  git diff --stat HEAD~3 2>/dev/null || git diff --stat
else
  echo "not a git repo — skipping git status; no commit is possible this session"
fi
```

If the probe reports "not a git repo", carry that fact into Step 5: the commit
option must not be offered. Also note that the session's real changes may live
outside the filesystem entirely (remote PRs, tickets, messages). Say so in the
integrated report rather than reporting "no changes".

## Step 2: Phase 1 - Analysis Agents (Parallel)

Execute 4 agents in parallel (single message with 4 Task calls).

### Session Summary (Provide to all agents)

```
Session Summary:
- Work: [Main tasks performed in session]
- Files: [Created/modified files]
- Decisions: [Key decisions made]
```

### Parallel Execution

```
Task(
    subagent_type="doc-updater",
    description="Document update analysis",
    prompt="[Session Summary]\n\nAnalyze if CLAUDE.md, context.md need updates."
)

Task(
    subagent_type="automation-scout",
    description="Automation pattern analysis",
    prompt="[Session Summary]\n\nAnalyze repetitive patterns or automation opportunities."
)

Task(
    subagent_type="learning-extractor",
    description="Learning points extraction",
    prompt="[Session Summary]\n\nExtract learnings, mistakes, and new discoveries."
)

Task(
    subagent_type="followup-suggester",
    description="Follow-up task suggestions",
    prompt="[Session Summary]\n\nSuggest incomplete tasks and next session priorities."
)
```

### Agent Roles

| Agent | Role | Output |
|-------|------|--------|
| **doc-updater** | Analyze CLAUDE.md/context.md updates | Specific content to add |
| **automation-scout** | Detect automation patterns | skill/command/agent suggestions |
| **learning-extractor** | Extract learning points | TIL format summary |
| **followup-suggester** | Suggest follow-up tasks | Prioritized task list |

## Step 3: Phase 2 - Validation Agent (Sequential)

Run after Phase 1 completes (dependency on Phase 1 results).

```
Task(
    subagent_type="duplicate-checker",
    description="Phase 1 proposal validation",
    prompt="""
Validate Phase 1 analysis results.

## doc-updater proposals:
[doc-updater results]

## automation-scout proposals:
[automation-scout results]

Check if proposals duplicate existing docs/automation:
1. Complete duplicate: Recommend skip
2. Partial duplicate: Suggest merge approach
3. No duplicate: Approve for addition
"""
)
```

## Step 4: Integrate Results

```markdown
## Wrap Analysis Results

### Documentation Updates
[doc-updater summary]
- Duplicate check: [duplicate-checker feedback]

### Automation Suggestions
[automation-scout summary]
- Duplicate check: [duplicate-checker feedback]

### Learning Points
[learning-extractor summary]

### Follow-up Tasks
[followup-suggester summary]
```

## Step 5: Action Selection

Build the option list from what Step 1 actually found. **Include the commit
option only when Step 1 confirmed a git repo with changes to commit** — offering
it in a non-git directory presents an impossible action as the top
recommendation.

Git repo with uncommitted changes:

```
AskUserQuestion(
    questions=[{
        "question": "Which actions would you like to perform?",
        "header": "Wrap Options",
        "multiSelect": true,
        "options": [
            {"label": "Create commit (Recommended)", "description": "Commit changes"},
            {"label": "Update CLAUDE.md", "description": "Document new knowledge/workflows"},
            {"label": "Create automation", "description": "Generate skill/command/agent"},
            {"label": "Skip", "description": "End without action"}
        ]
    }]
)
```

Not a git repo, or nothing to commit — drop the commit option and lead with the
documentation action:

```
AskUserQuestion(
    questions=[{
        "question": "Which actions would you like to perform?",
        "header": "Wrap Options",
        "multiSelect": true,
        "options": [
            {"label": "Update CLAUDE.md (Recommended)", "description": "Document new knowledge/workflows"},
            {"label": "Create automation", "description": "Generate skill/command/agent"},
            {"label": "Skip", "description": "End without action"}
        ]
    }]
)
```

## Step 6: Execute Selected Actions

Execute only the actions selected by user.

---

## Quick Reference

### When to Use

- End of significant work session
- Before switching to different project
- After completing a feature or fixing a bug

### When to Skip

- Very short session with trivial changes
- Only reading/exploring code
- Quick one-off question answered

### Arguments

- Empty: Proceed interactively (full workflow)
- Message provided: Use as commit message and commit directly

## Additional Resources

See `references/multi-agent-patterns.md` for detailed orchestration patterns.
