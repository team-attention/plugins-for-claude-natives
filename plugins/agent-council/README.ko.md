# Agent Council

**[English Version](./README.md)**

> 여러 AI CLI(Codex, Gemini, ...)의 의견을 모으고, 설정 가능한 의장(Chairman)이 종합해 결론을 내리게 하는 스킬
> [Karpathy의 LLM Council](https://github.com/karpathy/llm-council)에서 영감을 받음

## LLM Council과의 차이점

**추가 API 비용이 들지 않습니다!**

Karpathy의 LLM Council은 각 LLM의 API를 직접 호출하여 비용이 발생하지만, Agent Council은 설치된 AI CLI(Claude Code, Codex CLI, Gemini CLI 등)를 활용합니다. 주로 하나의 호스트 CLI를 메인으로 쓰면서 다른 CLI들은 구독 플랜으로 필요할 때만 쓰는 분들에게 특히 유용합니다.

MCP보다 Skill이 훨씬 간단하고 재현 가능해서 npx로 설치 후 직접 커스터마이징하여 사용하시는 것을 추천합니다.

## 데모

https://github.com/user-attachments/assets/c550c473-00d2-4def-b7ba-654cc7643e9b

## 작동 방식

Agent Council은 AI 합의를 수집하기 위한 3단계 프로세스를 구현합니다:

**Stage 1: Initial Opinions (초기 의견 수집)**
설정된 모든 AI 에이전트가 동시에 질문을 받고 독립적으로 응답합니다.

**Stage 2: Response Collection (응답 수집)**
각 에이전트의 응답을 수집하여 포맷된 형태로 표시합니다.

**Stage 3: Chairman Synthesis (의장 종합)**
기본값(`role: auto`)에서는 “현재 사용 중인 호스트 에이전트(Claude Code / Codex CLI 등)”가 의장 역할을 하며, 모든 의견을 종합해 최종 추천을 제시합니다. 원하면 `chairman.command`를 설정해 `council.sh` 안에서 Stage 3 종합을 CLI로 직접 실행할 수도 있습니다.

## 설치

### 방법 A: npx로 설치 (권장)

```bash
npx github:team-attention/agent-council
```

현재 프로젝트 디렉토리에 스킬 파일들이 복사됩니다.
Agent Council을 업그레이드한 뒤 `Missing runtime dependency: yaml` 같은 런타임 에러가 나면, 위 설치 커맨드를 한 번 더 실행해서 설치된 스킬 파일을 갱신하세요.

기본값으로 설치 스크립트가 자동으로 Claude Code(`.claude/`) / Codex CLI(`.codex/`) 설치 여부를 감지해서 가능한 타깃에 설치합니다.

설치 위치:
- `.claude/skills/agent-council/` (Claude Code)
- `.codex/skills/agent-council/` (Codex CLI)

선택사항 (Codex용 레포 스킬로 설치):
```bash
npx github:team-attention/agent-council --target codex
```

다른 타깃:
```bash
npx github:team-attention/agent-council --target claude
npx github:team-attention/agent-council --target both
```

생성되는 `council.config.yaml`은 감지된 멤버 CLI(claude/codex/gemini 등)만 포함하며, 설치 타깃(호스트)은 members에 포함되지 않도록 처리합니다. 이 필터링은 **초기 생성 시점에만** 적용되며, 이후 편집 내용은 자동으로 정리되지 않습니다.

### 방법 B: Claude Code 플러그인으로 설치 (Claude Code 전용)

```bash
# 마켓플레이스 추가
/plugin marketplace add team-attention/plugins-for-claude-natives

# 플러그인 설치
/plugin install agent-council@plugins-for-claude-natives
```

참고(플러그인 설치): **Agent Council은 Node.js가 필요**하며, Claude Code 플러그인은 Node를 번들/자동 설치할 수 없습니다. Node를 별도로 설치하세요(예: macOS `brew install node`).

### 2. Agent CLI 설치

`council.config.yaml`의 `council.members`에 적힌 CLI를 설치하세요(템플릿 기본 포함: `claude`, `codex`, `gemini`):

```bash
# Anthropic Claude Code
# https://claude.ai/code

# OpenAI Codex CLI
# https://github.com/openai/codex

# Google Gemini CLI
# https://github.com/google-gemini/gemini-cli
#
# 참고: Gemini CLI는 무료/Pro/Ultra 사용자 대상 2026-06-18 종료되며 후속작 Antigravity
# CLI(`agy`)로 전환됩니다. `gemini`가 없고 `agy`가 설치돼 있으면 `gemini` 멤버는 자동으로
# `agy --dangerously-skip-permissions -p`로 실행됩니다.
# agy 설치: curl -fsSL https://antigravity.google/cli/install.sh | bash
```

설치 확인(멤버별):
```bash
command -v claude
command -v codex
command -v gemini
```

### 3. Council 멤버 설정 (선택사항)

설치된 스킬 폴더의 설정 파일을 편집해서 council을 커스터마이즈:
- `.claude/skills/agent-council/council.config.yaml`
- `.codex/skills/agent-council/council.config.yaml`

```yaml
council:
  chairman:
    role: "auto" # auto|claude|codex|gemini|...
    # command: "codex exec" # 선택: council.sh에서 Stage 3 종합까지 실행

  members:
    - name: codex
      command: "codex exec"
      emoji: "🤖"
      color: "BLUE"

    - name: gemini
      command: "gemini"
      emoji: "💎"
      color: "GREEN"

    # 필요에 따라 에이전트 추가
    # - name: grok
    #   command: "grok"
    #   emoji: "🚀"
    #   color: "MAGENTA"
```

## 사용법

### 호스트 에이전트를 통한 사용 (Claude Code / Codex CLI)

호스트 에이전트에게 council 소집을 요청하면 됩니다:

```
"다른 AI들 의견도 들어보자"
"council 소집해줘"
"여러 관점에서 검토해줘"
"codex랑 gemini 의견 물어봐"
```

### 스크립트 직접 실행

```bash
JOB_DIR=$(.codex/skills/agent-council/scripts/council.sh start "질문 내용")
.codex/skills/agent-council/scripts/council.sh status --text "$JOB_DIR"
.codex/skills/agent-council/scripts/council.sh results "$JOB_DIR"
.codex/skills/agent-council/scripts/council.sh clean "$JOB_DIR"
```

팁: `status --text`에 `--verbose`를 추가하면 멤버별 상태 라인이 함께 출력됩니다.
팁: `status --checklist`는 체크리스트 형태로 간단히 보여줍니다(Codex/Claude tool cell에 유용).
팁: `wait`를 쓰면 “의미 있는 진행”이 있을 때만 반환해서 tool cell 스팸을 줄일 수 있습니다(JSON 출력, 커서는 자동으로 저장/갱신; 기본값은 멤버 수에 따라 대략 ~5~10번 수준으로 자동 배치, `--bucket 1`이면 매 완료마다 반환).

원샷 실행(잡 시작 → 대기 → 결과 출력 → 정리):

```bash
.codex/skills/agent-council/scripts/council.sh "질문 내용"
```

참고: 호스트 에이전트 도구 UI(Codex CLI / Claude Code)에서는 원샷이 **블로킹하지 않습니다**. 네이티브 plan/todo UI를 갱신할 수 있도록 `wait` JSON을 한 번 반환하고 종료하며, 이후 `wait` → 네이티브 UI 갱신 → `results` → `clean` 순서로 진행하세요.

#### 진행상황

- 실제 터미널에서는 원샷이 멤버 완료에 맞춰 진행상황 라인을 주기적으로 출력합니다.
- 호스트 에이전트 도구 UI에서는 원샷이 `wait` JSON을 반환합니다(네이티브 plan/todo UI 갱신 목적).
- 스크립팅이 필요하면 job mode(`start` → `status` → `results` → `clean`)도 사용할 수 있습니다.

## 예시

```
User: "새 대시보드 프로젝트에 React vs Vue 어떨까? council 소집해줘"

호스트 에이전트(Claude Code / Codex CLI):
1. council.sh 실행하여 설정된 멤버(예: Codex, Gemini) 의견 수집
2. 각 에이전트의 관점 표시
3. 의장으로서 종합:
   "Council의 의견을 바탕으로, 대시보드의 데이터 시각화 요구사항과
   팀의 숙련도를 고려할 때..."
```

## 프로젝트 구조

```
agent-council/
├── .claude-plugin/
│   └── marketplace.json     # 마켓플레이스 설정 (Claude Code 전용)
├── bin/
│   └── install.js           # npx 설치 스크립트
├── skills/
│   └── agent-council/
│       ├── SKILL.md         # 스킬 문서
│       └── scripts/
│           ├── council.sh           # 실행 스크립트
│           ├── council-job.sh       # 백그라운드 Job runner (폴링 가능)
│           ├── council-job.js       # Job runner 구현
│           └── council-job-worker.js # 멤버별 워커
├── council.config.yaml      # Council 멤버 설정
├── README.md                # 영어 문서
├── README.ko.md             # 이 문서
└── LICENSE
```

## 주의사항

- 응답 시간은 가장 느린 에이전트에 의존 (병렬 실행)
- 민감한 정보는 council에 공유하지 않기
- 에이전트는 기본적으로 병렬로 실행되어 빠른 응답 제공
- 각 CLI 도구의 구독 플랜이 필요합니다 (API 비용 별도 발생 없음)

## 기여하기

기여를 환영합니다! 다음과 같은 기여가 가능합니다:
- 새로운 AI 에이전트 지원 추가
- 종합 프로세스 개선
- 설정 옵션 확장

## 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](./LICENSE) 참조

## 크레딧

- [Karpathy의 LLM Council](https://github.com/karpathy/llm-council)에서 영감
- [Claude Code](https://claude.ai/code) / [Codex CLI](https://github.com/openai/codex) 용으로 제작
