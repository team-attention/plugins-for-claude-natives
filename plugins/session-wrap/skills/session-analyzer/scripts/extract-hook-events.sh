#!/bin/bash
# extract-hook-events.sh - Extract Hook events from debug log
#
# Usage: extract-hook-events.sh <debug-log-path>
# Output: JSON with hook events, triggers, and results

set -euo pipefail

DEBUG_LOG="${1:-}"

if [[ -z "$DEBUG_LOG" ]] || [[ ! -f "$DEBUG_LOG" ]]; then
    echo "Usage: $0 <debug-log-path>" >&2
    exit 1
fi

echo "{"

# Extract PreToolUse hooks
echo '  "pre_tool_use": ['
first=true
while IFS= read -r line; do
    timestamp=$(echo "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+Z' || echo "")
    tool_name=$(echo "$line" | grep -oP 'PreToolUse with query: \K\S+' || echo "")

    if [[ -n "$tool_name" ]]; then
        if [[ "$first" != "true" ]]; then
            echo ","
        fi
        first=false
        printf '    {"timestamp": "%s", "tool": "%s"}' "$timestamp" "$tool_name"
    fi
done < <(grep "Getting matching hook commands for PreToolUse" "$DEBUG_LOG" 2>/dev/null || true)
echo ""
echo "  ],"

# Extract hook matches
echo '  "hook_matches": ['
first=true
while IFS= read -r line; do
    timestamp=$(echo "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+Z' || echo "")
    match_count=$(echo "$line" | grep -oP 'Matched \K\d+' || echo "0")
    query=$(echo "$line" | grep -oP 'for query "\K[^"]+' || echo "")

    if [[ "$match_count" -gt 0 ]]; then
        if [[ "$first" != "true" ]]; then
            echo ","
        fi
        first=false
        printf '    {"timestamp": "%s", "query": "%s", "matched": %s}' "$timestamp" "$query" "$match_count"
    fi
done < <(grep "Matched .* unique hooks for query" "$DEBUG_LOG" 2>/dev/null || true)
echo ""
echo "  ],"

# Extract prompt hook results
echo '  "prompt_hook_results": ['
first=true
while IFS= read -r line; do
    timestamp=$(echo "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+Z' || echo "")

    if echo "$line" | grep -q "Prompt hook condition was met"; then
        if [[ "$first" != "true" ]]; then
            echo ","
        fi
        first=false
        printf '    {"timestamp": "%s", "result": "met"}' "$timestamp"
    elif echo "$line" | grep -q "Prompt hook condition was not met"; then
        if [[ "$first" != "true" ]]; then
            echo ","
        fi
        first=false
        printf '    {"timestamp": "%s", "result": "not_met"}' "$timestamp"
    fi
done < <(grep "Prompt hook condition" "$DEBUG_LOG" 2>/dev/null || true)
echo ""
echo "  ],"

# Extract permission decisions
echo '  "permission_decisions": ['
first=true
while IFS= read -r line; do
    timestamp=$(echo "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+Z' || echo "")
    decision=$(echo "$line" | grep -oP 'permissionDecision.*:\s*"\K[^"]+' || echo "")

    if [[ -n "$decision" ]]; then
        if [[ "$first" != "true" ]]; then
            echo ","
        fi
        first=false
        printf '    {"timestamp": "%s", "decision": "%s"}' "$timestamp" "$decision"
    fi
done < <(grep "permissionDecision" "$DEBUG_LOG" 2>/dev/null || true)
echo ""
echo "  ],"

# Summary
stop_hooks=$(grep -c "Getting matching hook commands for Stop" "$DEBUG_LOG" 2>/dev/null || echo "0")
pre_tool_hooks=$(grep -c "Getting matching hook commands for PreToolUse" "$DEBUG_LOG" 2>/dev/null || echo "0")
post_tool_hooks=$(grep -c "Getting matching hook commands for PostToolUse" "$DEBUG_LOG" 2>/dev/null || echo "0")
subagent_stop=$(grep -c "Getting matching hook commands for SubagentStop" "$DEBUG_LOG" 2>/dev/null || echo "0")
prompt_hooks=$(grep -c "Processing prompt hook" "$DEBUG_LOG" 2>/dev/null || echo "0")

cat << EOF
  "summary": {
    "PreToolUse": $pre_tool_hooks,
    "PostToolUse": $post_tool_hooks,
    "Stop": $stop_hooks,
    "SubagentStop": $subagent_stop,
    "prompt_hooks_processed": $prompt_hooks
  }
}
EOF
