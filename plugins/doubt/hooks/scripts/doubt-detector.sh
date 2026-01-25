#!/bin/bash
# !rv keyword detection -> activate doubt mode

STATE_DIR="$HOME/.claude/.hook-state"
mkdir -p "$STATE_DIR"

# Read JSON from stdin
input=$(cat)
prompt=$(echo "$input" | jq -r '.prompt // empty')
session_id=$(echo "$input" | jq -r '.session_id // empty')

# Fallback if session_id missing
if [ -z "$session_id" ]; then
    session_id="unknown"
fi

STATE_FILE="$STATE_DIR/doubt-mode-$session_id"

# Detect !rv keyword
if [[ "$prompt" == *"!rv"* ]]; then
    echo "enabled" > "$STATE_FILE"
    # Output JSON with additionalContext to tell Claude to ignore the keyword
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
