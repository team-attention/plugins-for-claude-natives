# Plugins for Claude Natives

Claude Code의 기능을 확장하고 싶은 파워 유저를 위한 플러그인 모음입니다.

## 목차

- [빠른 시작](#빠른-시작)
- [플러그인 목록](#플러그인-목록)
- [상세 설명](#상세-설명)
  - [agent-council](#agent-council) - 여러 AI 모델의 의견 종합
  - [clarify](#clarify) - 모호한 요구사항을 명세로 변환
  - [dev](#dev) - 커뮤니티 스캔 + 기술 의사결정
  - [interactive-review](#interactive-review) - 웹 UI로 계획 검토
  - [say-summary](#say-summary) - 응답을 음성으로 듣기
  - [youtube-digest](#youtube-digest) - YouTube 영상 요약 및 퀴즈
  - [google-calendar](#google-calendar) - 멀티 계정 캘린더 통합
  - [session-wrap](#session-wrap) - 세션 마무리 + 히스토리 분석
- [기여하기](#기여하기)
- [라이선스](#라이선스)

---

## 빠른 시작

```bash
# 마켓플레이스 추가
/plugin marketplace add team-attention/plugins-for-claude-natives

# 플러그인 설치
/plugin install <plugin-name>
```

---

## 플러그인 목록

| 플러그인 | 설명 | 소셜 |
|---------|------|------|
| [agent-council](./plugins/agent-council/) | 여러 AI 에이전트(Gemini, GPT, Codex)의 의견을 수집하고 종합 | [LinkedIn](https://www.linkedin.com/posts/gb-jeong_claude-code%EA%B0%80-codex-gemini-cli-%EA%B3%BC-%ED%9A%8C%EC%9D%98%ED%95%B4%EC%84%9C-%EA%B2%B0%EB%A1%A0%EC%9D%84-activity-7406083077258665984-L_fD) |
| [clarify](./plugins/clarify/) | 반복적인 질문을 통해 모호한 요구사항을 정확한 명세로 변환 | [LinkedIn](https://www.linkedin.com/posts/gb-jeong_%ED%81%B4%EB%A1%9C%EB%93%9C%EC%BD%94%EB%93%9C%EA%B0%80-%EA%B0%9D%EA%B4%80%EC%8B%9D%EC%9C%BC%EB%A1%9C-%EC%A7%88%EB%AC%B8%ED%95%98%EA%B2%8C-%ED%95%98%EB%8A%94-skills%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%B4%EB%B3%B4%EC%84%B8%EC%9A%94-clarify-activity-7413349697022570496-qLts) |
| [dev](./plugins/dev/) | 커뮤니티 의견 스캔 + 기술 의사결정 분석 | |
| [interactive-review](./plugins/interactive-review/) | 웹 UI를 통한 인터랙티브 마크다운 리뷰 | [LinkedIn](https://www.linkedin.com/posts/hoyeonleekr_claude-code%EA%B0%80-%EC%9E%91%EC%84%B1%ED%95%9C-%EA%B3%84%ED%9A%8D%EC%9D%B4%EB%82%98-%EA%B8%B4-%EB%AC%B8%EC%84%9C%EC%97%90-%EB%8C%80%ED%95%9C-%EC%96%B4%EB%96%BB%EA%B2%8C-%ED%94%BC%EB%93%9C%EB%B0%B1-%EC%A3%BC%EC%84%B8%EC%9A%94-activity-7412613598516051968-ujHp) |
| [say-summary](./plugins/say-summary/) | Claude 응답을 macOS TTS로 요약해서 읽어줌 (한국어/영어) | [LinkedIn](https://www.linkedin.com/posts/gb-jeong_claude-code%EC%9D%98-%EC%9D%91%EB%8B%B5%EC%9D%84-%EC%9A%94%EC%95%BD%ED%95%B4%EC%84%9C-%EC%9D%8C%EC%84%B1%EC%9C%BC%EB%A1%9C-%EB%93%A4%EC%9D%84-%EC%88%98-%EC%9E%88%EB%8A%94-hooks-activity-7412609821390249984-ekCd) |
| [youtube-digest](./plugins/youtube-digest/) | YouTube 영상 요약, 인사이트, 한글 번역, 퀴즈 제공 | [LinkedIn](https://www.linkedin.com/posts/gb-jeong_84%EB%B6%84%EC%A7%9C%EB%A6%AC-%EC%98%81%EC%96%B4-%ED%8C%9F%EC%BA%90%EC%8A%A4%ED%8A%B8%EB%A5%BC-5%EB%B6%84-%EB%A7%8C%EC%97%90-%ED%95%B5%EC%8B%AC-%ED%8C%8C%EC%95%85%ED%95%98%EA%B3%A0-%ED%80%B4%EC%A6%88%EA%B9%8C%EC%A7%80-%ED%92%80%EA%B3%A0-%EC%A7%81%EC%A0%91-activity-7414055598754848768-c0oy) |
| [google-calendar](./plugins/google-calendar/) | 멀티 계정 Google Calendar 통합, 병렬 조회 및 충돌 감지 | |
| [session-wrap](./plugins/session-wrap/) | 세션 마무리, 히스토리 분석, 세션 검증 툴킷 | |

---

## 상세 설명

### agent-council

**여러 AI 모델을 소환해서 질문에 대한 합의를 도출합니다.**

어려운 결정을 내려야 하거나 다양한 관점이 필요할 때, 이 플러그인은 여러 AI 에이전트(Gemini CLI, GPT, Codex)에 병렬로 질문하고 그 의견들을 하나의 균형 잡힌 답변으로 종합합니다.

**트리거 문구:**
- "summon the council"
- "다른 AI들한테 물어봐"
- "여러 모델 의견 듣고 싶어"

**동작 방식:**
1. 질문이 여러 AI 에이전트에 동시에 전송됨
2. 각 에이전트가 자신의 관점을 제시
3. Claude가 응답들을 종합하여 합의점과 이견을 정리

```bash
# 예시
User: "summon the council - TypeScript vs JavaScript 뭘 써야 할까?"
```

---

### clarify

**모호한 요구사항을 정확하고 실행 가능한 명세로 변환합니다.**

불명확한 지시사항으로 코드를 작성하기 전에, 이 플러그인이 구조화된 인터뷰를 통해 정확히 무엇이 필요한지 파악합니다. 더 이상 추측도, 재작업도 필요 없습니다.

**트리거 문구:**
- "/clarify"
- "요구사항 명확히 해줘"
- "내가 뭘 원하는 건지..."

**프로세스:**
1. **캡처** - 원본 요구사항을 그대로 기록
2. **질문** - 모호한 부분을 해결하기 위한 객관식 질문
3. **비교** - Before/After로 변환 결과 제시
4. **저장** - 선택적으로 명세를 파일로 저장

**변환 예시:**

| Before | After |
|--------|-------|
| "로그인 기능 추가해줘" | 목표: 사용자명/비밀번호 로그인과 자가 가입 추가. 범위: 로그인, 로그아웃, 가입, 비밀번호 재설정. 제약: 24시간 세션, bcrypt, 5회 시도 제한. |

---

### dev

**개발자 워크플로우 도구: 커뮤니티 스캔과 기술 의사결정.**

개발자 리서치와 의사결정을 위한 두 가지 강력한 스킬을 제공합니다.

#### 스킬

**`/dev-scan`** - 개발자 커뮤니티 의견 스캔
- Reddit (Gemini CLI 통해), Hacker News, Dev.to, Lobsters를 병렬 검색
- 공통 의견, 논쟁점, 주목할 시각을 종합
- 도구 도입 전 커뮤니티 분위기 파악에 유용

**`/tech-decision`** - 깊이 있는 기술 의사결정 분석
- 4개의 전문 에이전트가 병렬로 실행되는 다단계 워크플로우
- 코드베이스 분석, 문서 리서치, 커뮤니티 의견, AI 전문가 관점 종합
- 두괄식(결론 먼저) 보고서와 점수화된 비교 제공

**트리거 문구:**
- "개발자 반응...", "개발자들 뭐라고 해?"
- "A vs B", "어떤 라이브러리 써야 해?", "기술 의사결정"

**tech-decision 동작 방식:**

```
Phase 1: 병렬 정보 수집
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ codebase-       │ docs-           │ dev-scan        │ agent-council   │
│ explorer        │ researcher      │ (커뮤니티)       │ (AI 전문가)      │
└────────┬────────┴────────┬────────┴────────┬────────┴────────┬────────┘
         └─────────────────┴─────────────────┴─────────────────┘
                                    │
Phase 2: 분석 및 종합               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        tradeoff-analyzer                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       decision-synthesizer                               │
│                       (두괄식: 결론 먼저)                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

```bash
# 예시
User: "React vs Vue 뭐가 나을까?"
User: "상태관리 라이브러리 뭐 쓸지 고민이야"
User: "모놀리스 vs 마이크로서비스 어떻게 해야 할까?"
```

---

### interactive-review

**웹 인터페이스를 통해 Claude의 계획과 문서를 검토합니다.**

터미널에서 긴 마크다운을 읽는 대신, 이 플러그인은 브라우저 기반 UI를 열어 항목별로 체크/언체크하고, 코멘트를 추가하고, 구조화된 피드백을 제출할 수 있게 합니다.

**트리거 문구:**
- "/review"
- "이 계획 검토해줘"
- "확인해볼게"

**플로우:**
1. Claude가 계획이나 문서를 생성
2. 브라우저에 웹 UI가 자동으로 열림
3. 각 항목을 체크박스와 선택적 코멘트로 검토
4. Submit 클릭하여 구조화된 피드백 전송
5. Claude가 승인/거부된 항목에 따라 조정

---

### say-summary

**Claude의 응답을 음성으로 들을 수 있습니다 (macOS 전용).**

이 플러그인은 Stop hook을 사용하여 Claude의 응답을 짧은 헤드라인으로 요약하고 macOS 텍스트-투-스피치로 읽어줍니다. 코딩하면서 음성 피드백을 원할 때 딱입니다.

**기능:**
- Claude Haiku를 사용해 응답을 3-10단어로 요약
- 한국어 vs 영어 자동 감지
- 적절한 음성 사용 (한국어: Yuna, 영어: Samantha)
- 백그라운드 실행, Claude Code 차단 없음

**요구사항:**
- macOS (`say` 명령어 사용)
- Python 3.10+

---

### youtube-digest

**YouTube 영상을 트랜스크립트, 번역, 이해도 퀴즈와 함께 요약합니다.**

YouTube URL을 입력하면 완전한 분석을 받을 수 있습니다: 요약, 핵심 인사이트, 전체 트랜스크립트 한글 번역, 그리고 이해도를 테스트하는 3단계 퀴즈(총 9문제).

**트리거 문구:**
- "이 유튜브 정리해줘"
- "영상 요약해줘"
- YouTube URL

**받을 수 있는 것:**
1. **요약** - 핵심 포인트와 함께 3-5문장 개요
2. **인사이트** - 실행 가능한 테이크어웨이와 아이디어
3. **전체 트랜스크립트** - 한글 번역과 타임스탬프 포함
4. **3단계 퀴즈** - 기본, 중급, 심화 문제
5. **Deep Research** (선택) - 주제를 확장하는 웹 검색

**저장 위치:** `research/readings/youtube/YYYY-MM-DD-title.md`

---

### google-calendar

**Claude Code에서 여러 Google Calendar 계정을 관리합니다.**

여러 Google 계정(회사, 개인 등)의 일정을 조회, 생성, 수정, 삭제할 수 있으며 자동 충돌 감지 기능을 제공합니다.

**트리거 문구:**
- "일정 보여줘"
- "캘린더 확인"
- "미팅 만들어줘"
- "충돌 확인해줘"

**기능:**
- 여러 계정 병렬 조회
- 계정 간 충돌 감지
- 전체 CRUD 작업 (생성, 조회, 수정, 삭제)
- refresh token으로 사전 인증 (반복 로그인 불필요)

**설정 필요:**
1. Calendar API가 활성화된 Google Cloud 프로젝트 생성
2. 각 계정별 설정 스크립트 실행

```bash
# 계정별 최초 1회 설정
uv run python scripts/setup_auth.py --account work
uv run python scripts/setup_auth.py --account personal
```

---

### session-wrap

**종합 세션 마무리 및 분석 툴킷.**

코딩 세션을 철저히 분석하고 마무리하며, 세션 히스토리에서 인사이트를 추출합니다.

#### 스킬

**`/wrap`** - 세션 마무리 워크플로우
- 종합 세션 분석을 위한 2단계 멀티 에이전트 파이프라인
- 문서화 필요사항, 자동화 기회, 배운 점, 후속 작업 캡처
- `/wrap [커밋 메시지]`로 빠른 커밋

**`/history-insight`** - 세션 히스토리 분석
- Claude Code 세션 히스토리에서 패턴과 인사이트 분석
- 현재 프로젝트 또는 전체 세션 검색
- 주제, 결정사항, 반복 패턴 추출

**`/session-analyzer`** - 사후 세션 검증
- SKILL.md 명세 대비 세션 행동 검증
- 에이전트, 훅, 도구가 올바르게 실행되었는지 확인
- 상세한 준수 보고서 생성

**/wrap 동작 방식 (2단계 파이프라인):**

```
Phase 1: 분석 (병렬)
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ doc-updater  │ automation-  │ learning-    │ followup-    │
│              │ scout        │ extractor    │ suggester    │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┘
       └──────────────┴──────────────┴──────────────┘
                            │
Phase 2: 검증               ▼
┌─────────────────────────────────────────────────────────────┐
│                    duplicate-checker                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    사용자 선택
```

**장점:**
- 중요한 발견을 문서화하는 것을 잊지 않음
- 자동화할 가치가 있는 패턴 식별
- 미래 세션을 위한 명확한 인수인계점 생성
- 과거 세션의 반복 패턴 분석
- 스킬 구현이 명세대로 동작하는지 검증

---

## 기여하기

기여를 환영합니다! 이슈나 PR을 열어주세요.

## 라이선스

MIT
