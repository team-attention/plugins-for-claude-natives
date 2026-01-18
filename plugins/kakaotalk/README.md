# KakaoTalk Plugin for Claude Code

macOS에서 카카오톡 메시지를 발송하고 읽는 Claude Code 플러그인.

## Features

- **메시지 발송**: 자연어로 카카오톡 메시지 전송 (발송 전 확인)
- **메시지 읽기**: 채팅방 대화 내역 조회
- **채팅방 목록**: 현재 채팅방 목록 확인
- **서명 자동 추가**: 기본적으로 "sent with claude code" 서명 포함

## Requirements

- **macOS only** (uses Accessibility API)
- **KakaoTalk for Mac** must be running
- **Accessibility permission**: System Settings > Privacy & Security > Accessibility
- **atomacos**: `uv add atomacos` or `pip install atomacos`

## Usage

### Send Message

Claude가 메시지를 보내기 전에 항상 확인을 요청합니다.

```bash
# 기본 (서명 포함)
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/kakao_send.py "구봉" "밥 먹었어?"
# → "밥 먹었어?\n\nsent with claude code" 전송

# 서명 없이
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/kakao_send.py "구봉" "밥 먹었어?" --no-signature

# 보내고 창 닫기
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/kakao_send.py "구봉" "밥 먹었어?" --close
```

### Read Messages

```bash
# 메시지 읽기
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/kakao_read.py "구봉" --json

# 채팅방 목록
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/kakao_read.py --list

# 채팅방 검색
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/kakao_read.py --search "검색어"
```

## Options

### kakao_send.py

| Option | Description |
|--------|-------------|
| `--close`, `-c` | 발송 후 채팅창 닫기 |
| `--no-signature` | "sent with claude code" 서명 없이 보내기 |
| `--json`, `-j` | JSON 형식 출력 |

### kakao_read.py

| Option | Description |
|--------|-------------|
| `--limit N`, `-l N` | 최대 N개 메시지 읽기 (기본: 100) |
| `--close`, `-c` | 읽고 나서 채팅창 닫기 |
| `--json`, `-j` | JSON 형식 출력 |
| `--list` | 채팅방 목록 보기 |
| `--search "검색어"`, `-s` | 채팅방 검색 |

## How It Works

This plugin uses macOS Accessibility API (via atomacos) to:
1. Find and activate KakaoTalk windows
2. Search for chat rooms using Cmd+F
3. Read message content from UI elements
4. Send messages via clipboard paste + Enter

## Limitations

- **macOS only**: Uses platform-specific APIs
- **Visible messages only**: Can only read messages currently visible in the chat window
- **UI dependent**: May break if KakaoTalk updates its UI structure
- **KakaoTalk must be running**: Cannot start the app automatically

## License

MIT
