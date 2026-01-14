#!/bin/bash
# extract-session.sh
# Extract essential conversation from Claude Code session JSONL files
#
# Usage: ./extract-session.sh <session.jsonl>
# Output: Filtered JSON to stdout
#
# ============================================================
# 세션 파일 구조 분석 결과 (12MB 파일 예시)
# ============================================================
#
# JSONL type 분포:
#   file-history-snapshot : 67% (8.4MB) → 버림
#   queue-operation       : 27% (3.4MB) → 버림
#   user + assistant      :  6% (800KB) → 추출
#   system, summary       : <1%         → 선택적
#
# assistant.message.content[] 내부:
#   thinking  : Claude 생각 + signature → 버림
#   tool_use  : tool 호출 정보          → 버림
#   text      : 실제 응답 텍스트        → 추출
#
# 결과: 12MB → ~800KB (93% 감소)
# ============================================================

set -e

SESSION_FILE="$1"

if [ -z "$SESSION_FILE" ]; then
  echo "Usage: $0 <session.jsonl>" >&2
  exit 1
fi

if [ ! -f "$SESSION_FILE" ]; then
  echo "Error: File not found: $SESSION_FILE" >&2
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "Error: jq is required. Install with: brew install jq" >&2
  exit 1
fi

# Extract conversation only:
# - summary: 세션 요약
# - user: 사용자 메시지 (.message.content)
# - assistant: Claude 응답 중 text만 (.message.content[].type == "text")
#
# Explicitly ignored (94% of file size):
# - file-history-snapshot: 파일 백업 스냅샷
# - queue-operation: 큐 연산 로그
# - assistant.thinking: 생각 과정 + signature
# - assistant.tool_use: tool 호출 정보

jq -c '
  if .type == "summary" then
    {type: "summary", summary: .summary}
  elif .type == "user" then
    {
      type: "user",
      content: .message.content,
      ts: .timestamp
    }
  elif .type == "assistant" then
    {
      type: "assistant",
      texts: [.message.content[]? | select(.type == "text") | .text],
      ts: .timestamp
    } | select(.texts | length > 0)
  else
    empty
  end
' "$SESSION_FILE" 2>/dev/null | jq -s '{
  file: "'"$SESSION_FILE"'",
  message_count: length,
  messages: .
}'
