---
name: kakaotalk
description: This skill should be used when the user asks to "카톡 보내줘", "카카오톡 메시지", "KakaoTalk message", "채팅 읽어줘", "~에게 메시지 보내줘", or needs to send/read messages via KakaoTalk on macOS.
version: 2.0.0
---

# KakaoTalk CLI

macOS에서 CLI를 통해 카카오톡 메시지를 읽고 보내는 스킬.

## 트리거

- "카카오톡 메시지", "카톡 읽어줘", "~에게 메시지 보내줘"

## 스크립트 구조

| 파일 | 용도 |
|------|------|
| `kakao_read.py` | 채팅방 검색, 열기, 메시지 읽기 |
| `kakao_send.py` | 메시지 발송 |

---

## 메시지 발송 워크플로우

### Step 1: 채팅방 열고 대화 내역 읽기

대상 이름으로 채팅방을 열고 대화 내역을 읽습니다:

```bash
uv run python .claude/skills/kakaotalk/scripts/kakao_read.py "대상이름" --json
```

**출력 예시:**
```json
{
  "chat_name": "구봉",
  "messages": [
    {"sender": "나", "text": "오늘 저녁 뭐 먹을까?", "time": "오후 3:24"},
    {"sender": "구봉", "text": "파스타 어때?", "time": "오후 3:45"}
  ]
}
```

**메시지 분석 시 주의:**
- 배열 끝부분이 최신 메시지 (최근일수록 가치 높음)
- 1주일 이상 된 내용은 상황이 바뀌었을 수 있음
- 최근 대화 주제와 자연스럽게 이어지는 메시지 작성

### Step 2: 맥락 파악 후 메시지 작성

읽은 대화 내역을 바탕으로:
1. 최근 대화 흐름 파악
2. 사용자 요청에 맞는 메시지 초안 작성
3. 자연스럽고 맥락에 맞는 내용 구성

### Step 3: 사용자 확인 (필수)

**먼저 텍스트로 메시지 내용을 보여준 후** AskUserQuestion으로 확인:

```
[텍스트 출력]
**최근 대화 요약:**
- {최근 대화 내용 요약}

**보낼 메시지:**
받는 사람: {채팅방}
---
{메시지 내용}

sent with claude code
---

[AskUserQuestion]
질문: "이 메시지를 보낼까요?"
옵션: ["보내기", "수정 필요"]
```

### Step 4: 발송

사용자 확인 후 메시지 발송:

```bash
uv run python .claude/skills/kakaotalk/scripts/kakao_send.py "채팅방이름" "메시지"
```

---

## 메시지 읽기 전용 워크플로우

단순히 대화 내역만 확인할 때:

```bash
uv run python .claude/skills/kakaotalk/scripts/kakao_read.py "대상이름" --json
```

읽은 후 사용자에게 요약 제공:
- 최근 대화 2-3개 요약
- 현재 진행 중인 대화 주제
- 답장이 필요한 내용이 있는지

---

## CLI 옵션 레퍼런스

### kakao_read.py

```bash
# 기본: 채팅방 열고 메시지 읽기
kakao_read.py "채팅방이름" [--limit N] [--json]

# 채팅 목록
kakao_read.py --list [--json]

# 검색
kakao_read.py --search "검색어" [--json]

# 읽고 창 닫기
kakao_read.py "채팅방이름" --close
```

### kakao_send.py

```bash
# 기본 (서명 포함)
kakao_send.py "채팅방" "메시지"
# → "메시지\n\nsent with claude code"

# 서명 없이
kakao_send.py "채팅방" "메시지" --no-signature

# 보내고 창 닫기
kakao_send.py "채팅방" "메시지" --close
```

---

## 예시 시나리오

### "구봉한테 보낼 메시지 제안"

```
[Step 1] 채팅방 열고 읽기
uv run python .../kakao_read.py "구봉" --json

[Step 2] 맥락 파악
최근 대화: 저녁 메뉴 논의 중

[Step 3] 메시지 제안
"파스타 좋아! 오늘 7시에 만날까?"

[Step 4] 사용자 확인 후 발송
```

---

## 요구사항

1. **atomacos 설치**: `uv add atomacos`
2. **Accessibility 권한**: System Settings > Privacy & Security > Accessibility에서 Terminal 허용
3. **카카오톡 실행**: macOS용 카카오톡 앱 실행 중
