---
name: history-insight
description: This skill should be used when user wants to access, capture, or reference Claude Code session history. Trigger when user says "capture session", "save session history", or references past/current conversation as a source - whether for saving, extracting, summarizing, or reviewing. This includes any mention of "what we discussed", "today's work", "session history", or when user treats the conversation itself as source material (e.g., "from our conversation").
version: 1.1.0
user-invocable: true
---

# History Insight

Claude Code 세션 히스토리를 분석하고 인사이트를 추출합니다.

---

## Data Location

```
~/.claude/projects/<encoded-cwd>/*.jsonl
```

**Path Encoding:** `/Users/foo/project` → `-Users-foo-project`

> 상세 파일 포맷: `${baseDir}/references/session-file-format.md`

---

## Execution Algorithm

### Step 1: Ask Scope [MANDATORY]

**스코프 결정:**

1. **명시된 경우** (AskUserQuestion 생략 가능):
   - "현재 프로젝트만" / "이 프로젝트" → `current_project`
   - "모든 세션" / "전체" → `all_sessions`

2. **명시되지 않은 경우** - AskUserQuestion 호출:
   ```
   question: "세션 검색 범위를 선택하세요"
   options:
     - "현재 프로젝트만" → ~/.claude/projects/<encoded-cwd>/*.jsonl
     - "모든 Claude Code 세션" → ~/.claude/projects/**/*.jsonl
   ```

---

### Step 2: Find Session Files

```bash
# Current project only
find ~/.claude/projects/<encoded-cwd> -name "*.jsonl" -type f

# All sessions (모든 프로젝트)
find ~/.claude/projects -name "*.jsonl" -type f
```

**날짜 필터링**: 파일의 mtime(수정시간) 확인 후 필터. OS별 `stat` 옵션 다름:
- macOS: `stat -f "%Sm" -t "%Y-%m-%d" <file>`
- Linux: `stat -c "%y" <file>`

---

### Step 3: Process Sessions

#### Decision Tree

```
Session files found?
├─ No → Error: "No sessions found"
└─ Yes → How many files?
    ├─ 1-3 files → Direct Read + parse
    └─ 4+ files → Batch Extract Pipeline
```

#### 1-3 Files

직접 Read로 JSONL 파싱. 파일이 크면(≥5000 tokens) `extract-session.sh` 사용:
```bash
${baseDir}/scripts/extract-session.sh <session.jsonl>
```

#### 4+ Files: Batch Extract Pipeline

1. 캐시 디렉토리 생성 (`/tmp/cc-cache/<analysis-name>/`)
2. 세션 목록 저장 (`sessions.txt`)
3. jq로 메시지 일괄 추출 (`user_messages.txt`)
4. 정리 및 필터링 (`clean_messages.txt`)
5. Task(opus)로 종합 분석

#### 파일이 너무 클 때: 병렬 배치 분석

`clean_messages.txt`가 너무 커서 Read 실패 시:

1. **파일 분할**:
   ```bash
   split -l 2000 clean_messages.txt /tmp/cc-cache/<name>/batch_
   ```

2. **병렬 Task(opus) 호출**:
   ```
   Task(subagent_type="general-purpose", model="opus", run_in_background=true)
   prompt: "batch_XX 파일을 읽고 주제/패턴 요약해줘"
   ```

3. **결과 병합**: Task(opus)로 종합

---

### Step 4: Report Results

```markdown
## Session Capture Complete

- **Sessions:** N files processed
- **Messages:** X total, Y after filter

### Extracted Insights
[분석 결과]
```

---

## Error Handling

| Scenario | Response |
|----------|----------|
| No session files found | "No session files found for this project." |
| File too large | Auto-preprocess with extract-session.sh |
| jq not installed | "Error: jq is required. Install with: brew install jq" |
| Task failed | "Warning: Could not process [file]. Skipping." |
| 0 relevant sessions | "No sessions matched your criteria." |

---

## Security Notes

- 출력에 전체 경로 노출 금지 (`~` prefix 사용)

---

## Related Resources

- **`${baseDir}/scripts/extract-session.sh`** - JSONL 압축 (thinking, tool_use 제거)
- **`${baseDir}/references/session-file-format.md`** - JSONL 구조 및 파싱
