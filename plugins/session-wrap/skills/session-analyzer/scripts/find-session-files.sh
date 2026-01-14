#!/bin/bash
# find-session-files.sh - Locate all files related to a Claude Code session
#
# Usage: find-session-files.sh <session-id>
# Output: JSON with paths to session files

set -euo pipefail

SESSION_ID="${1:-}"

if [[ -z "$SESSION_ID" ]]; then
    echo "Usage: $0 <session-id>" >&2
    exit 1
fi

CLAUDE_DIR="$HOME/.claude"

# Find main session log (in projects directory)
MAIN_LOG=$(find "$CLAUDE_DIR/projects" -name "${SESSION_ID}.jsonl" 2>/dev/null | head -1)

# Find debug log
DEBUG_LOG="$CLAUDE_DIR/debug/${SESSION_ID}.txt"
if [[ ! -f "$DEBUG_LOG" ]]; then
    DEBUG_LOG=""
fi

# Find agent transcripts (subagent sessions)
AGENT_LOGS=$(find "$CLAUDE_DIR/projects" -name "agent-*.jsonl" 2>/dev/null | xargs grep -l "$SESSION_ID" 2>/dev/null || true)

# Find todo file
TODO_FILE=$(find "$CLAUDE_DIR/todos" -name "*${SESSION_ID}*.json" 2>/dev/null | head -1)

# Find session environment
SESSION_ENV="$CLAUDE_DIR/session-env/${SESSION_ID}"
if [[ ! -d "$SESSION_ENV" ]]; then
    SESSION_ENV=""
fi

# Output as JSON
cat << EOF
{
  "session_id": "$SESSION_ID",
  "main_log": "$MAIN_LOG",
  "debug_log": "$DEBUG_LOG",
  "agent_logs": [$(echo "$AGENT_LOGS" | sed 's/^/"/' | sed 's/$/"/' | tr '\n' ',' | sed 's/,$//' | sed 's/^""$//')],
  "todo_file": "$TODO_FILE",
  "session_env": "$SESSION_ENV",
  "found": {
    "main_log": $([ -n "$MAIN_LOG" ] && echo "true" || echo "false"),
    "debug_log": $([ -n "$DEBUG_LOG" ] && echo "true" || echo "false")
  }
}
EOF
