#!/bin/bash
# !rv keyword detection -> activate re-validate mode
# Supports !rv (1회), !rv2 (2회), !rv3 (3회) etc.

STATE_DIR="$HOME/.claude/.hook-state"
mkdir -p "$STATE_DIR"

# Read JSON from stdin
input=$(cat)
prompt=$(printf '%s' "$input" | jq -r '.prompt // empty')
session_id=$(printf '%s' "$input" | jq -r '.session_id // empty')

# Fallback if session_id missing
if [ -z "$session_id" ]; then
    session_id="unknown"
fi

STATE_FILE="$STATE_DIR/rv-mode-$session_id"

# Detect !rv, !rv2, !rv3, etc.
if [[ "$prompt" =~ \!rv([0-9]*) ]]; then
    count="${BASH_REMATCH[1]}"
    # Default to 1 if no number specified (!rv alone)
    if [ -z "$count" ]; then
        count=1
    fi

    echo "$count" > "$STATE_FILE"

    cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Note: Ignore the '!rv' keyword in the prompt - it's a meta-command for the system, not part of the actual request."
  }
}
EOF
fi

exit 0
