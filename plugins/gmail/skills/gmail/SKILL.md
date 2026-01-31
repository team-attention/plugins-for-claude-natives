---
name: gmail
description: Gmail 읽기, 검색, 발송, 라벨 관리. "메일 확인", "이메일 읽어줘", "메일 보내줘", "답장해줘" 요청에 사용. 여러 Google 계정 지원.
---

# Gmail Skill

## Overview

Gmail API를 통해 이메일을 읽고, 검색하고, 발송하고, 관리하는 skill.

주요 기능:
- **메시지 조회**: 받은편지함, 검색, 스레드 조회
- **메시지 발송**: 새 메일, 답장, 첨부파일
- **메시지 관리**: 읽음/안읽음, 별표, 보관, 휴지통, 라벨
- **초안 관리**: 생성, 수정, 발송
- **라벨 관리**: 생성, 삭제, 수정

## 트리거 조건

### 조회
- "메일 확인해줘", "받은편지함 보여줘"
- "안 읽은 메일 있어?", "오늘 온 메일"
- "user@example.com 한테 온 메일"

### 검색
- "지난주에 온 중요한 메일 찾아줘"
- "첨부파일 있는 메일 검색"
- "프로젝트 관련 메일"

### 발송
- "메일 보내줘", "답장해줘"
- "이 내용으로 메일 작성해줘"
- "파일 첨부해서 보내줘"

### 관리
- "이 메일 읽음 처리해줘"
- "별표 추가해줘", "보관처리해줘"
- "라벨 붙여줘", "휴지통으로 이동"

## 계정 설정

### accounts.yaml

**스킬 실행 전 `accounts.yaml`을 먼저 읽어 등록된 계정 확인:**

```yaml
# accounts.yaml 예시
accounts:
  personal:
    email: user@gmail.com
    description: 개인 Gmail

  work:
    email: user@company.com
    description: 회사 업무용
```

계정 목록 확인:
```bash
uv run python scripts/setup_auth.py --list
```

### 계정 추가 (최초 1회)

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/gmail

# 의존성 설치
uv sync

# 개인 계정 인증 (이메일은 자동 감지)
uv run python scripts/setup_auth.py --account personal --description '개인 Gmail'

# 회사 계정 인증
uv run python scripts/setup_auth.py --account work --description '회사 업무용'
```

브라우저에서 Google 로그인 → 계정 정보가 `accounts.yaml`에, 토큰이 `accounts/{name}.json`에 저장됨.

### Google Cloud 프로젝트 설정

**Option 1: Claude in Chrome (비개발자 권장)**

gcloud CLI가 설치되어 있지 않다면, Claude가 브라우저 자동화를 통해 설정을 도와줍니다:

1. Claude에게 말하기: "Claude in Chrome으로 Gmail API 설정 도와줘"
2. Claude가 안내하는 단계:
   - Google Cloud Console 접속 및 로그인
   - 새 프로젝트 생성
   - Gmail API 활성화
   - OAuth 2.0 클라이언트 ID 생성 (Desktop 유형)
   - `credentials.json` 다운로드

**Option 2: 수동 설정**

1. [Google Cloud Console](https://console.cloud.google.com)에서 프로젝트 생성
2. Gmail API 활성화
3. OAuth 2.0 Client ID 생성 (Desktop 유형)
4. `credentials.json` 다운로드 → `references/credentials.json`에 저장

### (선택) gcloud ADC 사용

OAuth 클라이언트 대신 gcloud ADC 사용 가능:

```bash
gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.labels
```

스크립트 실행 시 `--adc` 플래그 추가.

## CLI 사용법

### 메시지 조회

```bash
# 최근 메일 10개
uv run python scripts/list_messages.py --account ${ACCOUNT_NAME} --max 10

# 안 읽은 메일
uv run python scripts/list_messages.py --account ${ACCOUNT_NAME} --query "is:unread"

# 특정 발신자
uv run python scripts/list_messages.py --account ${ACCOUNT_NAME} --query "from:user@example.com"

# 날짜 범위
uv run python scripts/list_messages.py --account ${ACCOUNT_NAME} --query "after:2024/01/01 before:2024/12/31"

# 라벨 필터
uv run python scripts/list_messages.py --account ${ACCOUNT_NAME} --labels INBOX,IMPORTANT

# 전체 내용 포함
uv run python scripts/list_messages.py --account ${ACCOUNT_NAME} --full

# JSON 출력
uv run python scripts/list_messages.py --account ${ACCOUNT_NAME} --json
```

### 메시지 읽기

```bash
# 메시지 읽기
uv run python scripts/read_message.py --account ${ACCOUNT_NAME} --id <message_id>

# 스레드 전체 읽기
uv run python scripts/read_message.py --account ${ACCOUNT_NAME} --thread <thread_id>

# 첨부파일 저장
uv run python scripts/read_message.py --account ${ACCOUNT_NAME} --id <message_id> --save-attachments ./downloads
```

### 메시지 발송

```bash
# 새 메일
uv run python scripts/send_message.py --account ${ACCOUNT_NAME} \
    --to "recipient@example.com" \
    --subject "제목" \
    --body "메일 내용입니다."

# HTML 메일
uv run python scripts/send_message.py --account ${ACCOUNT_NAME} \
    --to "recipient@example.com" \
    --subject "공지" \
    --body "<h1>제목</h1><p>내용</p>" \
    --html

# 첨부파일
uv run python scripts/send_message.py --account ${ACCOUNT_NAME} \
    --to "recipient@example.com" \
    --subject "파일 전송" \
    --body "첨부파일을 확인해주세요." \
    --attach file1.pdf,file2.xlsx

# 답장
uv run python scripts/send_message.py --account ${ACCOUNT_NAME} \
    --to "recipient@example.com" \
    --subject "Re: 원본 제목" \
    --body "답장 내용" \
    --reply-to <message_id> \
    --thread <thread_id>

# 초안으로 저장
uv run python scripts/send_message.py --account ${ACCOUNT_NAME} \
    --to "recipient@example.com" \
    --subject "나중에 보낼 메일" \
    --body "초안 내용" \
    --draft
```

### 라벨 및 메시지 관리

```bash
# 라벨 목록
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} list-labels

# 라벨 생성
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} create-label --name "프로젝트/A"

# 읽음 표시
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} mark-read --id <message_id>

# 별표 추가/제거
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} star --id <message_id>
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} unstar --id <message_id>

# 보관처리
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} archive --id <message_id>

# 휴지통
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} trash --id <message_id>
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} untrash --id <message_id>

# 라벨 추가/제거
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} modify --id <message_id> \
    --add-labels "Label_123,STARRED" --remove-labels "INBOX"

# 초안 목록
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} list-drafts

# 초안 발송
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} send-draft --draft-id <draft_id>

# 프로필 조회
uv run python scripts/manage_labels.py --account ${ACCOUNT_NAME} profile
```

## Gmail 검색 쿼리 예시

| 쿼리 | 설명 |
|------|------|
| `from:user@example.com` | 특정 발신자 |
| `to:user@example.com` | 특정 수신자 |
| `subject:프로젝트` | 제목에 포함 |
| `is:unread` | 읽지 않음 |
| `is:starred` | 별표 있음 |
| `is:important` | 중요 표시 |
| `has:attachment` | 첨부파일 있음 |
| `filename:pdf` | PDF 첨부 |
| `after:2024/01/01` | 이후 날짜 |
| `before:2024/12/31` | 이전 날짜 |
| `older_than:7d` | 7일 이전 |
| `newer_than:1d` | 1일 이내 |
| `in:inbox` | 받은편지함 |
| `in:sent` | 보낸편지함 |
| `label:work` | 특정 라벨 |

복합 쿼리:
```
from:boss@company.com is:unread after:2024/01/01
has:attachment filename:xlsx newer_than:7d
```

## 메일 발송 워크플로우 (Task 기반 4단계)

메일 발송 시 **반드시 TaskCreate로 4단계 Task를 생성**하고 순차적으로 진행한다.

### Task 생성 예시

```
TaskCreate: "Step 1: 이전 대화 맥락 파악"
TaskCreate: "Step 2: 메일 드래프트 작성 및 피드백"
TaskCreate: "Step 3: 나에게 테스트 발송"
TaskCreate: "Step 4: 실제 수신자에게 발송"
```

---

### Step 1: 이전 대화 맥락 파악

**Task 상태**: `in_progress`

수신자와의 이전 대화를 검색하여 맥락을 파악한다:

```bash
# 수신자와의 최근 대화 검색 (90일 이내)
uv run python scripts/list_messages.py --account ${ACCOUNT_NAME} \
    --query "to:recipient@example.com OR from:recipient@example.com newer_than:90d" \
    --max 5
```

> **검색 한계**: 이 쿼리는 To/From 필드만 검색한다. CC/BCC로 포함된 대화나 이메일 별칭(alias)을 사용한 경우 누락될 수 있다.

#### 이전 대화가 있는 경우

AskUserQuestion으로 스레드 선택:

```
📧 이전 대화 발견

recipient@example.com과의 최근 대화:
1. [2026-01-05] Re: 프로젝트 일정 논의
2. [2026-01-02] 미팅 요청

이 중 하나에 이어서 답장할까요?

- 1번 스레드에 답장
- 2번 스레드에 답장
- 새 메일로 보내기
```

**Task 상태**: `completed` → Step 2로 이동

---

### Step 2: 메일 드래프트 작성 및 피드백

**Task 상태**: `in_progress`

맥락을 바탕으로 메일 초안을 작성하고 AskUserQuestion으로 피드백 요청:

```
📝 메일 드래프트

수신자: recipient@example.com
제목: 미팅 일정 안내
스레드: 새 메일 / Re: 프로젝트 일정 논의

---
안녕하세요,

(메일 내용)

---
Sent with Claude Code
---

- 다음 단계로 (테스트 발송)
- 수정 필요
```

사용자가 "수정 필요" 선택 시 피드백 반영 후 다시 드래프트 제시.

**Task 상태**: `completed` → Step 3로 이동

---

### Step 3: 나에게 테스트 발송

**Task 상태**: `in_progress`

**실제 발송 전, 사용자 본인에게 테스트 메일을 발송**한다:

```bash
# 사용자 본인 이메일로 테스트 발송
uv run python scripts/send_message.py --account ${ACCOUNT_NAME} \
    --to "${YOUR_EMAIL}" \
    --subject "[테스트] 미팅 일정 안내" \
    --body "메일 내용"
```

발송 후 AskUserQuestion으로 확인:

```
📧 테스트 메일 발송 완료

${YOUR_EMAIL}으로 테스트 메일을 보냈습니다.
메일함에서 내용을 확인해주세요.

- 확인 완료, 실제 발송하기
- 수정 필요 (Step 2로 돌아가기)
- 취소
```

**Task 상태**: `completed` → Step 4로 이동

---

### Step 4: 실제 수신자에게 발송

**Task 상태**: `in_progress`

최종 확인 후 실제 수신자에게 발송:

```bash
uv run python scripts/send_message.py --account ${ACCOUNT_NAME} \
    --to "recipient@example.com" \
    --subject "미팅 일정 안내" \
    --body "메일 내용" \
    [--reply-to <message_id> --thread <thread_id>]  # 스레드 답장인 경우
```

발송 완료 메시지:

```
✅ 메일 발송 완료

수신자: recipient@example.com
제목: 미팅 일정 안내
```

**Task 상태**: `completed`

---

### 서명 자동 추가

모든 발송 메일 본문 하단에 다음 서명을 추가:

```
---
Sent with Claude Code
```

HTML 메일의 경우:
```html
<hr style="margin-top: 20px; border: none; border-top: 1px solid #ddd;">
<p style="color: #888; font-size: 12px;">Sent with Claude Code</p>
```

## 워크플로우 예시

### 사용자: "안 읽은 중요 메일 확인해줘"

```
1. accounts.yaml 읽기
   └── 등록된 계정:
       - personal: user@gmail.com (개인 Gmail)
       - work: user@company.com (회사 업무용)

2. 쿼리 실행
   └── "is:unread is:important"

3. 결과 표시
   └── 3개 메일 발견
       📩 [긴급] 내일 미팅 건
       📩 Q4 실적 보고서
       📩 계약서 검토 요청
```

### 사용자: "김팀장한테 온 메일 중에 첨부파일 있는 거 찾아줘"

```
1. 검색 쿼리 구성
   └── "from:kim@company.com has:attachment"

2. 결과 반환
   └── 5개 메일 발견
```

### 사용자: "박대리한테 내일 미팅 일정 메일 보내줘"

```
[Task 생성]
  #1: Step 1: 이전 대화 맥락 파악
  #2: Step 2: 메일 드래프트 작성 및 피드백
  #3: Step 3: 나에게 테스트 발송
  #4: Step 4: 실제 수신자에게 발송

[Task #1 시작] 이전 대화 맥락 파악
  └── 검색: "to:park@company.com OR from:park@company.com"
  └── 이전 대화 발견 → AskUserQuestion
      - 1번 스레드에 답장
      - 2번 스레드에 답장
      - 새 메일로 보내기
  └── 사용자 선택: "새 메일로 보내기"
  └── Task #1 완료

[Task #2 시작] 드래프트 작성 및 피드백
  └── 메일 초안 작성 후 AskUserQuestion
      📝 메일 드래프트
      수신자: park@company.com
      제목: 내일 미팅 일정 안내
      ---
      (메일 내용)
      ---
      - 다음 단계로 (테스트 발송)
      - 수정 필요
  └── 사용자: "다음 단계로"
  └── Task #2 완료

[Task #3 시작] 나에게 테스트 발송
  └── 사용자 본인 이메일로 테스트 발송
  └── AskUserQuestion: 메일함 확인 요청
      - 확인 완료, 실제 발송하기
      - 수정 필요
      - 취소
  └── 사용자: "확인 완료"
  └── Task #3 완료

[Task #4 시작] 실제 발송
  └── park@company.com에게 발송
  └── ✅ 발송 완료
  └── Task #4 완료
```

## 파일 구조

```
skills/gmail/
├── SKILL.md                    # 이 파일
├── pyproject.toml              # 의존성
├── accounts.yaml               # 계정 메타데이터 (이메일, 설명)
├── scripts/
│   ├── gmail_client.py         # API 클라이언트
│   ├── setup_auth.py           # 인증 설정
│   ├── list_messages.py        # 메시지 조회 CLI
│   ├── read_message.py         # 메시지 읽기 CLI
│   ├── send_message.py         # 메시지 발송 CLI
│   └── manage_labels.py        # 라벨/메시지 관리 CLI
├── references/
│   └── credentials.json        # OAuth Client ID (gitignore)
└── accounts/                   # 계정별 토큰 (gitignore)
    └── {account_name}.json
```

## API 권한 (Scopes)

| Scope | 용도 |
|-------|------|
| `gmail.modify` | 메시지 읽기/수정/삭제 |
| `gmail.send` | 메일 발송 |
| `gmail.labels` | 라벨 관리 |

## 에러 처리

| 상황 | 처리 |
|------|------|
| accounts/ 폴더 비어있음 | 초기 설정 안내 |
| 토큰 만료 | 자동 갱신 시도, 실패 시 재인증 안내 |
| API 할당량 초과 | 잠시 후 재시도 안내 |
| 권한 부족 | 필요한 scope 안내 |

## 보안 주의사항

- `accounts/*.json`: refresh token 포함, 절대 커밋 금지
- `references/credentials.json`: Client Secret 포함, 커밋 금지
- `.gitignore`에 추가 필수:

```gitignore
accounts/
references/credentials.json
```

## 출력 형식 예시

```
📬 3개 메시지

📩 [긴급] 내일 미팅 관련
   From: 김팀장 <kim@company.com>
   Date: Mon, 6 Jan 2025 09:30:00 +0900
   첨부된 자료 검토 부탁드립니다. 내일 오전 10시까지...

📧 주간 리포트
   From: 리포트봇 <report@company.com>
   Date: Mon, 6 Jan 2025 08:00:00 +0900
   이번 주 주간 리포트입니다...

📧 뉴스레터
   From: newsletter@service.com
   Date: Sun, 5 Jan 2025 18:00:00 +0900
   이번 주 주요 뉴스...
```
