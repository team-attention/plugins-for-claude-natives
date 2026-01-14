# Analysis Patterns for Session Analyzer

Detailed grep/search patterns for extracting information from Claude Code debug logs.

---

## Debug Log Structure

Debug logs are located at `~/.claude/debug/{sessionId}.txt` and contain timestamped entries:

```
2026-01-13T09:39:26.905Z [DEBUG] {message}
```

---

## SubAgent Patterns

### SubAgent Start
```bash
# Pattern
grep "SubagentStart with query:" debug.txt

# Example output
2026-01-13T09:39:26.905Z [DEBUG] Getting matching hook commands for SubagentStart with query: Explore
```

### SubAgent Stop
```bash
# Pattern
grep "SubagentStop with query:" debug.txt

# With agent ID (session tracking)
grep "agent_id.*agent_transcript_path" debug.txt
```

### SubAgent Session Registration
```bash
# Pattern - shows when hooks are registered for subagent
grep "Registered.*frontmatter hook.*from agent" debug.txt

# Example
2026-01-13T09:43:08.203Z [DEBUG] Registered 1 frontmatter hook(s) from agent 'gap-analyzer' for session a373157
```

---

## Hook Patterns

### PreToolUse Hook Trigger
```bash
# Pattern
grep "executePreToolHooks called for tool:" debug.txt

# Example
2026-01-13T09:39:40.000Z [DEBUG] executePreToolHooks called for tool: Write
```

### Hook Matcher Check
```bash
# Pattern
grep "Getting matching hook commands for PreToolUse with query:" debug.txt

# With match count
grep "Matched.*unique hooks for query" debug.txt

# Example
2026-01-13T09:39:40.000Z [DEBUG] Matched 1 unique hooks for query "Write" (1 before deduplication)
```

### Hook Permission Decision
```bash
# Pattern
grep "permissionDecision" debug.txt

# Example (allow)
"permissionDecision": "allow"

# Example (deny)
"permissionDecision": "deny"
```

### Prompt-Based Hook Processing
```bash
# Pattern - hook is being processed
grep "Hooks: Processing prompt hook with prompt:" debug.txt

# Pattern - model response
grep "Hooks: Model response:" debug.txt

# Pattern - condition result
grep "Prompt hook condition was" debug.txt

# Example (met)
2026-01-13T09:48:09.076Z [DEBUG] Hooks: Prompt hook condition was met

# Example (not met)
2026-01-13T09:45:59.297Z [DEBUG] Hooks: Prompt hook condition was not met: REJECT - ...
```

### Stop Hook Events
```bash
# Pattern
grep "Getting matching hook commands for Stop" debug.txt
```

### SubagentStop Hook Events
```bash
# Pattern - converted from Stop to SubagentStop
grep "Converting Stop hook to SubagentStop" debug.txt

# Example
2026-01-13T09:43:08.202Z [DEBUG] Converting Stop hook to SubagentStop for agent 'gap-analyzer'
```

---

## Tool Usage Patterns

### Tool Execution
```bash
# Pattern
grep "executePreToolHooks called for tool:" debug.txt
```

### File Write Operations
```bash
# Pattern - file creation/modification
grep "FileHistory: Tracked file modification for" debug.txt

# Pattern - atomic write
grep "File.*written atomically" debug.txt

# Example
2026-01-13T09:39:40.036Z [DEBUG] File /path/to/file.md written atomically
```

### Bash Command Execution
```bash
# Pattern - PreToolHooks for Bash
grep "executePreToolHooks called for tool: Bash" debug.txt
```

---

## Skill/Session Patterns

### Skill Loading
```bash
# Pattern - skill hooks registered
grep "Added session hook for event" debug.txt
grep "Registered.*hooks from skill" debug.txt

# Example
2026-01-13T09:39:14.449Z [DEBUG] Added session hook for event PreToolUse in session 3cc71c9f-...
2026-01-13T09:39:14.449Z [DEBUG] Registered 2 hooks from skill 'specify'
```

### Session Hook Cleanup
```bash
# Pattern
grep "Cleared all session hooks for session" debug.txt
```

---

## AskUserQuestion Patterns

```bash
# Pattern - PreToolHooks
grep "executePreToolHooks called for tool: AskUserQuestion" debug.txt

# Pattern - PostToolHooks
grep "PostToolUse with query: AskUserQuestion" debug.txt
```

---

## Error Patterns

### Hook Errors
```bash
# Pattern
grep -i "error\|failed\|exception" debug.txt | grep -i hook
```

### Tool Errors
```bash
# Pattern
grep "Tool.*error\|Tool.*failed" debug.txt
```

---

## Reviewer-Specific Patterns

### Reviewer Verdict Extraction
```bash
# Pattern - look for model response containing OKAY or REJECT
grep -A5 "Hooks: Model response:" debug.txt | grep -E '"ok":|"reason":'

# Example (OKAY)
{
  "ok": true,
  "reason": "Plan approved by reviewer..."
}

# Example (REJECT)
{
  "ok": false,
  "reason": "REJECT - The plan has a critical contradiction..."
}
```

---

## Artifact Patterns

### Draft File Operations
```bash
# Pattern - draft creation
grep "\.dev-flow/drafts/" debug.txt | grep "written atomically"

# Pattern - draft deletion (look for rm command)
grep "rm.*\.dev-flow/drafts/" debug.txt
```

### Plan File Operations
```bash
# Pattern - plan creation
grep "\.dev-flow/plans/" debug.txt | grep "written atomically"
```

---

## Timeline Reconstruction

To reconstruct a session timeline:

```bash
# Extract all timestamped events for key operations
grep -E "(SubagentStart|SubagentStop|executePreToolHooks|Prompt hook condition|written atomically)" debug.txt | sort
```

---

## Combined Analysis Query

Full analysis of a specify skill session:

```bash
# 1. Check Explore agents
grep "SubagentStart with query: Explore" debug.txt | wc -l

# 2. Check gap-analyzer
grep "SubagentStart with query: gap-analyzer" debug.txt

# 3. Check reviewer calls and results
grep -E "(SubagentStart with query: reviewer|Prompt hook condition)" debug.txt

# 4. Check plan-guard.sh hook
grep "permissionDecision" debug.txt

# 5. Check artifacts
grep -E "(\.dev-flow/drafts/|\.dev-flow/plans/).*written atomically" debug.txt

# 6. Final Stop hook result
grep -A10 "Getting matching hook commands for Stop" debug.txt | tail -20
```
