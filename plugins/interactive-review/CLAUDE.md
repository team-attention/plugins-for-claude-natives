# Interactive Review Plugin

Claude Code plugin for interactive markdown review with web UI.

## Directory Structure

```
interactive-review/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata and version
├── mcp-server/
│   ├── server.py        # MCP server (PEP 723 dependencies)
│   └── web_ui.py        # HTML/CSS generation
├── skills/
│   └── review/
│       └── SKILL.md     # /review skill definition
└── .mcp.json            # MCP server configuration
```

## Development

### MCP Server

`uv run`을 사용하여 의존성 자동 설치. `server.py` 상단의 PEP 723 metadata 참조:

```python
# /// script
# dependencies = ["mcp>=1.0.0"]
# ///
```

### Testing Locally

```bash
cd mcp-server
uv run python server.py
```

## Versioning

### Before Commit/Push

**반드시 `.claude-plugin/plugin.json`의 버전을 올려야 합니다.**

```json
{
  "version": "1.0.3"  // <- 이 값을 수정
}
```

### Semantic Versioning

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes, API 변경
- **MINOR** (1.0.0 → 1.1.0): 새 기능 추가 (하위 호환)
- **PATCH** (1.0.0 → 1.0.1): 버그 수정, 문서 업데이트

### Checklist

- [ ] 기능 변경 시 버전 올리기
- [ ] `plugin.json` 버전 업데이트
- [ ] 변경 사항 테스트

## Marketplace Publishing

**Marketplace 퍼블리싱은 선택 사항입니다.**

| 상황 | Marketplace 필요? |
|------|------------------|
| 개인용/로컬 테스트 | 불필요 |
| 팀 내부 공유 | 선택적 |
| 커뮤니티 배포 | 권장 |

현재 이 플러그인은 `team-attention/agents` 레포에 포함되어 있어 별도 marketplace 등록 없이 사용 가능합니다.

### 참고 문서

- [Claude Code Plugins](https://www.anthropic.com/news/claude-code-plugins)
- [Plugin Marketplaces Guide](https://code.claude.com/docs/en/plugin-marketplaces)
