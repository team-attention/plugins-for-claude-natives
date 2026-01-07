---
name: dev-opinions
description: >
  This skill should be used when the user wants to gather diverse developer
  opinions and community discussions about a technical topic. Triggers include:
  "개발자 반응", "커뮤니티 의견", "개발자들 생각", "여러 의견 모아줘",
  "what do developers think", "community opinions", "developer reactions",
  "gather opinions from multiple sources".
version: 1.0.0
---

# Dev Opinions

여러 개발 커뮤니티에서 특정 주제에 대한 다양한 의견을 수집하여 종합.

## Purpose

기술 주제에 대한 **다양한 시각**을 빠르게 파악:
- 찬반 의견 분포
- 실무자들의 경험담
- 숨겨진 우려사항이나 장점
- 커뮤니티별 온도 차이

## Data Sources

| Platform | Method | 특성 |
|----------|--------|------|
| Reddit | Gemini CLI | 실무자 경험, 솔직한 의견 |
| Hacker News | WebSearch | 깊은 기술 토론, 시니어 의견 |
| Dev.to | WebSearch | 튜토리얼, 입문자 관점 |
| Lobsters | WebSearch | 니치한 시니어 의견 |

## Execution

### Step 1: Topic Extraction
사용자 요청에서 핵심 주제 추출.

예시:
- "React 19에 대한 개발자들 반응" → `React 19`
- "Bun vs Deno 커뮤니티 의견" → `Bun vs Deno`

### Step 2: Parallel Search (Single Message, 4 Sources)

**Reddit** (Gemini CLI - WebFetch blocked):
```bash
# 병렬로 3개 쿼리 실행 (주제에 맞게 쿼리 구성)
gemini -p "{일반 검색: topic + site:reddit.com}" &
gemini -p "{관련 서브레딧 2-3개 + topic}" &
gemini -p "{다른 각도의 관련 서브레딧 + topic + opinions/thoughts}" &
wait
```

쿼리 구성 가이드:
- 첫 번째: 일반 Reddit 검색
- 두 번째: 주제에 가장 관련된 서브레딧들 (예: React → r/reactjs r/webdev)
- 세 번째: 시니어/경험자 관점 서브레딧 (예: r/ExperiencedDevs) 또는 다른 관련 커뮤니티

**Other Sources** (WebSearch, parallel):
```
WebSearch: "{topic} site:news.ycombinator.com"
WebSearch: "{topic} site:dev.to"
WebSearch: "{topic} site:lobste.rs"
```

**CRITICAL**: 4개 검색을 반드시 **하나의 메시지**에서 병렬로 실행.

### Step 3: Synthesize & Present

## Output Format

```markdown

## Key Insights

**Consensus (공통 의견)**:
- ...

**Controversy (논쟁점)**:
- ...

**Notable Perspective (주목할 시각)**:
- ...

## Community Opinions: {topic}
### Reddit
- [의견 요약...]

### Hacker News
- [의견 요약...]

### Dev.to
- [의견 요약...]

### Lobsters
- [의견 요약...]

---

## Sources
- [링크 목록...]
```

## Error Handling

| 상황 | 대응 |
|------|------|
| 검색 결과 없음 | 해당 플랫폼 생략, 다른 소스에 집중 |
| Gemini CLI 실패 | Reddit 생략하고 나머지 3개로 진행 |
| 주제가 너무 새로움 | 결과 부족 안내, 관련 키워드 제안 |

## Examples

**단순 주제**:
```
User: "Tailwind v4 개발자들 반응 어때?"
→ topic: "Tailwind v4"
→ 4개 소스 병렬 검색
→ 종합 인사이트 제공
```

**비교 주제**:
```
User: "pnpm vs yarn vs npm 커뮤니티 의견"
→ topic: "pnpm vs yarn vs npm comparison"
→ 4개 소스 병렬 검색
→ 각 도구별 선호도 정리
```

**논쟁적 주제**:
```
User: "Claude Code Plugin 에 대한 개발자들 생각"
→ topic: "Claude Code Plugin tips"
→ 4개 소스 병렬 검색
→ 종합 인사이트 제공
```
