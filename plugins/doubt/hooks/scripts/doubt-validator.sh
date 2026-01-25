#!/bin/bash
# If doubt mode is active, request Claude to re-validate

STATE_DIR="$HOME/.claude/.hook-state"

# Read JSON from stdin
input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id // empty')

# Fallback if session_id missing
if [ -z "$session_id" ]; then
    session_id="unknown"
fi

STATE_FILE="$STATE_DIR/doubt-mode-$session_id"

if [ -f "$STATE_FILE" ]; then
    # Delete state file to run only once
    rm -f "$STATE_FILE"

    # Block decision + strong message
    cat << 'EOF'
{
  "decision": "block",
  "reason": "WAIT! You are lying or hallucinating! Go back and verify EVERYTHING you just said. Check the actual code, re-read the files, and make sure you're not making things up. I don't trust you yet!"
}
EOF
    exit 0
fi

# Normal exit if not in doubt mode
exit 0
