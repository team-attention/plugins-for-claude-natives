#!/bin/bash
# extract-subagent-calls.sh - Extract SubAgent invocations from debug log
#
# Usage: extract-subagent-calls.sh <debug-log-path>
# Output: JSON array of subagent calls with timestamps and results

set -euo pipefail

DEBUG_LOG="${1:-}"

if [[ -z "$DEBUG_LOG" ]] || [[ ! -f "$DEBUG_LOG" ]]; then
    echo "Usage: $0 <debug-log-path>" >&2
    exit 1
fi

echo "{"
echo '  "subagent_calls": ['

# Extract SubagentStart events
first=true
while IFS= read -r line; do
    timestamp=$(echo "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+Z' || echo "")
    agent_name=$(echo "$line" | grep -oP 'SubagentStart with query: \K\S+' || echo "")

    if [[ -n "$agent_name" ]]; then
        if [[ "$first" != "true" ]]; then
            echo ","
        fi
        first=false
        printf '    {"timestamp": "%s", "event": "start", "agent": "%s"}' "$timestamp" "$agent_name"
    fi
done < <(grep "SubagentStart with query:" "$DEBUG_LOG" 2>/dev/null || true)

echo ""
echo "  ],"

# Extract SubagentStop events with results
echo '  "subagent_results": ['

first=true
while IFS= read -r line; do
    timestamp=$(echo "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+Z' || echo "")

    if [[ -n "$timestamp" ]]; then
        # Look for hook result after this line
        if [[ "$first" != "true" ]]; then
            echo ","
        fi
        first=false
        printf '    {"timestamp": "%s", "event": "stop"}' "$timestamp"
    fi
done < <(grep "SubagentStop with query:" "$DEBUG_LOG" 2>/dev/null || true)

echo ""
echo "  ],"

# Summary counts
explore_count=$(grep -c "SubagentStart with query: Explore" "$DEBUG_LOG" 2>/dev/null || echo "0")
gap_analyzer_count=$(grep -c "SubagentStart with query: gap-analyzer" "$DEBUG_LOG" 2>/dev/null || echo "0")
reviewer_count=$(grep -c "SubagentStart with query: reviewer" "$DEBUG_LOG" 2>/dev/null || echo "0")
worker_count=$(grep -c "SubagentStart with query: worker" "$DEBUG_LOG" 2>/dev/null || echo "0")

cat << EOF
  "summary": {
    "Explore": $explore_count,
    "gap-analyzer": $gap_analyzer_count,
    "reviewer": $reviewer_count,
    "worker": $worker_count,
    "total": $((explore_count + gap_analyzer_count + reviewer_count + worker_count))
  }
}
EOF
