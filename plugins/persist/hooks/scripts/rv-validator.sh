#!/bin/bash
# If re-validate mode is active, block and force re-validation
# Decrements remaining count each time; removes state when 0

STATE_DIR="$HOME/.claude/.hook-state"

# Read JSON from stdin
input=$(cat)
session_id=$(printf '%s' "$input" | jq -r '.session_id // empty')

# Fallback if session_id missing
if [ -z "$session_id" ]; then
    session_id="unknown"
fi

STATE_FILE="$STATE_DIR/rv-mode-$session_id"

if [ -f "$STATE_FILE" ]; then
    remaining=$(cat "$STATE_FILE")

    # Decrement
    remaining=$((remaining - 1))

    if [ "$remaining" -le 0 ]; then
        # Last round - delete state file after this block
        rm -f "$STATE_FILE"
    else
        # More rounds remaining - update count
        echo "$remaining" > "$STATE_FILE"
    fi

    # Block and demand re-verification
    cat << EOF
{
  "decision": "block",
  "reason": "WAIT! You are lying or hallucinating! Go back and verify EVERYTHING you just said. Check the actual code, re-read the files, and make sure you're not making things up. I don't trust you yet! (Re-validation remaining: $remaining)"
}
EOF
    exit 0
fi

# Normal exit if not in rv mode
exit 0
