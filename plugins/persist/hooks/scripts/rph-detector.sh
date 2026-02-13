#!/bin/bash
# !rph keyword detection -> activate Ralph Loop (DoD-based iterative verification)

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

STATE_FILE="$STATE_DIR/rph-$session_id.json"
DOD_FILE="$STATE_DIR/rph-$session_id-dod.md"

# Detect !rph keyword
if [[ "$prompt" == *"!rph"* ]]; then
    # Strip !rph from the prompt
    stripped_prompt=$(printf '%s' "$prompt" | sed 's/!rph//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # Create state file using jq for proper JSON encoding
    jq -n \
      --arg prompt "$stripped_prompt" \
      --arg dod_file "$DOD_FILE" \
      --arg created_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      '{prompt: $prompt, iteration: 0, max_iterations: 10, dod_file: $dod_file, created_at: $created_at}' \
      > "$STATE_FILE"

    # Return minimal additionalContext - just strip keyword and ask for DoD
    # The Stop hook will handle all verification logic
    cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Note: Ignore the '!rph' keyword in the prompt - it's a meta-command for the system, not part of the actual request. Before starting the task, ask the user for their Definition of Done criteria using AskUserQuestion, then write them as a '- [ ]' markdown checklist to: $DOD_FILE"
  }
}
EOF
fi

exit 0
