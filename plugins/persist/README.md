# persist

AI 응답의 신뢰성을 높이는 persistence 도구 모음.

## Features

### 1. Re-Validate (`!rv`)

Claude의 응답을 강제로 재검증시킵니다. 횟수 지정 가능.

```
이 코드 분석해줘 !rv       # 1회 재검증
이 코드 분석해줘 !rv2      # 2회 재검증
이 코드 분석해줘 !rv3      # 3회 재검증
```

**Why `!rv`?** `doubt` 같은 키워드는 Claude의 행동에 영향을 줍니다. `!rv`(re-validate)는 중립적이라 Claude가 먼저 정상적으로 작업한 뒤 마지막에 검증합니다.

### 2. Ralph Loop (`!rph`)

DoD(Definition of Done) 기반 반복 검증 루프. 모든 완료 기준을 충족할 때까지 자동 재시도합니다.

```
피보나치 함수 만들어줘 !rph
```

**How It Works:**

1. `!rph` 감지 → state 파일 생성
2. Claude가 사용자에게 완료 기준 질문
3. `- [ ]` 마크다운 체크리스트로 저장
4. 태스크 실행, 완료 항목 `- [x]`로 업데이트
5. Stop hook 검증 → 미체크 항목 있으면 block
6. 모든 항목 `- [x]`이면 정상 종료 + cleanup

**Safety:** Max 10 iterations 초과 시 강제 종료

## State Files

```
~/.claude/.hook-state/
├── rv-mode-{session_id}         # !rv state (remaining count)
├── rph-{session_id}.json        # !rph loop state
└── rph-{session_id}-dod.md      # !rph DoD checklist
```

## Installation

```bash
claude plugins add /path/to/plugins/persist
```
