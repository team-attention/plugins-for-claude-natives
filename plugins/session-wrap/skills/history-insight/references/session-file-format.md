# Session File Format (.jsonl)

Claude Code 세션 파일의 상세 구조 및 파싱 방법

## JSONL Type 분류

| type | 설명 | 필요 여부 |
|------|------|---------|
| `user` | 사용자 메시지 | ✅ 필요 |
| `assistant` | Claude 응답 | ✅ 필요 (text만) |
| `file-history-snapshot` | 파일 백업 스냅샷 | ❌ 버림 |
| `queue-operation` | 큐 연산 로그 | ❌ 버림 |
| `system` | 시스템 메시지 | ⚪ 선택 |
| `summary` | 세션 요약 | ⚪ 선택 |

## 실제 분석 결과 (12MB 파일 예시)

| Type | Lines | Size | 비율 |
|------|-------|------|------|
| `file-history-snapshot` | 7,984 | 8.4MB | **67%** |
| `queue-operation` | 15,948 | 3.4MB | **27%** |
| `user` | 127 | 542KB | 4% |
| `assistant` | 163 | 255KB | 2% |
| `system` | 13 | 9KB | <1% |
| `summary` | 5 | 600B | <1% |

**결론:** 실제 대화는 6%, 나머지 94%는 메타데이터

## assistant 메시지 내부 구조

`.message.content[]` 배열 내부:

| 내부 type | 설명 | 필요 여부 |
|-----------|------|---------|
| `thinking` | Claude 생각 과정 + signature | ❌ 버림 |
| `tool_use` | tool 호출 정보 | ❌ 버림 |
| `text` | **실제 응답 텍스트** | ✅ 필요 |

## JSON 파싱 명령어

**user 메시지 추출:**
```bash
jq -c 'select(.type == "user") | {type, content: .message.content, ts: .timestamp}' <file.jsonl>
```

**assistant 메시지 추출 (text만):**
```bash
jq -c 'select(.type == "assistant") | {type, texts: [.message.content[] | select(.type == "text") | .text], ts: .timestamp}' <file.jsonl>
```

**한 번에 대화만 추출:**
```bash
jq -c '
  if .type == "user" then
    {type: "user", content: .message.content, ts: .timestamp}
  elif .type == "assistant" then
    {type: "assistant", texts: [.message.content[]? | select(.type == "text") | .text], ts: .timestamp}
    | select(.texts | length > 0)
  else empty end
' <file.jsonl>
```

**결과:** 12MB → ~160KB (99% 감소)
