# Calendar Configuration Examples

## Config File Format

캘린더 설정은 `accounts/{account}.config.yaml` 파일에 YAML 형식으로 저장됩니다.

### Basic Example

```yaml
# accounts/personal.config.yaml
calendars:
  - id: primary
    alias: Main
    enabled: true
  - id: abc123xyz@group.calendar.google.com
    alias: Work Tasks
    enabled: true
  - id: ko.south_korea#holiday@group.v.calendar.google.com
    alias: Korean Holidays
    enabled: false  # Excluded from queries
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Google Calendar ID |
| `alias` | No | Display name (auto-synced from Google Calendar's summary) |
| `enabled` | No | Whether to include in queries (defaults to true) |

> **Note**: `alias`는 Google Calendar의 이름(summary)과 자동 동기화됩니다. `--sync` 옵션으로 최신 상태를 유지할 수 있습니다.

## Usage Examples

### 1. Initial Setup (Interactive)

```bash
$ uv run python scripts/setup_auth.py --account personal

🔐 'personal' 계정 인증을 시작합니다...
[Browser login completed]

✅ 인증 완료! 토큰 저장됨: accounts/personal.json

📅 캘린더 설정을 진행합니다...

📋 사용 가능한 캘린더:
  [ 1] user@gmail.com (기본)  (owner)
  [ 2] Work Tasks  (owner)
  [ 3] Side Projects  (owner)
  [ 4] Family  (reader)
  [ 5] Holidays  (reader)

조회할 캘린더 번호를 입력하세요 (쉼표 구분, 예: 1,2,3)
Enter를 누르면 모든 캘린더 선택
> 1,2

✅ 캘린더 설정 저장됨: accounts/personal.config.yaml
   선택된 캘린더: 2개
     - user@gmail.com
     - Work Tasks
```

### 2. View Current Config (with change detection)

```bash
$ uv run python scripts/manage_config.py --account personal --list

📋 'personal' 계정의 캘린더 설정:

  ✅ user@gmail.com
  ✅ Work Tasks

  총 2개 캘린더 (2개 활성)

[변경 감지]
  🆕 Side Projects → 새로 추가됨
  📝 My Calendar → 이름 변경됨 (이전: Old Name)

  --sync 옵션으로 동기화하세요.
```

> **Note**: Google Calendar와 비교하여 변경사항(새 캘린더, 삭제된 캘린더, 이름 변경)을 자동으로 감지합니다.

### 3. Disable a Calendar

```bash
$ uv run python scripts/manage_config.py --account personal --disable "Work Tasks"
❌ 'Work Tasks' 캘린더 비활성화됨

# Config file is now:
# calendars:
#   - id: user@gmail.com
#     alias: user@gmail.com
#     enabled: true
#   - id: abc123xyz@group.calendar.google.com
#     alias: Work Tasks
#     enabled: false  # Changed!
```

### 4. Enable a Calendar

```bash
$ uv run python scripts/manage_config.py --account personal --enable "Work Tasks"
✅ 'Work Tasks' 캘린더 활성화됨
```

### 5. Sync with Google Calendar

```bash
$ uv run python scripts/manage_config.py --account personal --sync

🔄 Google Calendar와 동기화 중...

[변경 감지]
  🆕 Side Projects → 추가됨
  ⚠️  Old Calendar → 제거됨

📋 사용 가능한 캘린더:
  [ 1] Work Tasks  (owner)
  [ 2] Family  (reader)
  [ 3] Side Projects  (owner) 🆕

조회할 캘린더 번호를 입력하세요 (쉼표 구분, 예: 1,2,3)
Enter를 누르면 모든 캘린더 선택
> 1,3

✅ 캘린더 설정 동기화됨: accounts/personal.config.yaml
   선택된 캘린더: 2개
     - Work Tasks
     - Side Projects
```

> **Note**: 변경사항이 없으면 "✅ 변경사항이 없습니다. 설정이 최신 상태입니다." 메시지만 표시됩니다.

### 6. Reconfigure (Re-select calendars)

```bash
$ uv run python scripts/manage_config.py --account personal --reconfigure

📋 'personal' 계정에서 사용 가능한 캘린더:
  [ 1] user@gmail.com (기본)  (owner)
  [ 2] Work Tasks  (owner)
  [ 3] Side Projects  (owner)
  [ 4] Family  (reader)
  [ 5] Holidays  (reader)

조회할 캘린더 번호를 입력하세요 (쉼표 구분, 예: 1,2,3)
Enter를 누르면 모든 캘린더 선택
> 1,2,3

✅ 캘린더 설정 저장됨: accounts/personal.config.yaml
   선택된 캘린더: 3개
     - user@gmail.com
     - Work Tasks
     - Side Projects
```

### 7. Add a Calendar by ID

```bash
$ uv run python scripts/manage_config.py --account personal \
    --add "new_calendar_id@group.calendar.google.com"
✅ 캘린더 추가됨: New Calendar
```

> **Note**: alias는 Google Calendar에서 자동으로 가져옵니다.

### 8. Remove a Calendar

```bash
$ uv run python scripts/manage_config.py --account personal --remove "Side Projects"
✅ 캘린더 제거됨: Side Projects
```

## Backward Compatibility

설정 파일이 없는 경우:
- `fetch_events.py`는 기존처럼 `primary` 캘린더만 조회합니다
- 기존 사용자에게 영향 없음

```bash
# Config file does not exist
$ uv run python scripts/fetch_events.py --account personal --days 7 --pretty
📅 'personal' 계정 - 향후 7일간 일정 (primary 캘린더만)
...

# Config file exists
$ uv run python scripts/fetch_events.py --account personal --days 7 --pretty
📅 'personal' 계정 - 향후 7일간 일정 (설정 파일 사용)
...
```

## Manual Editing

설정 파일을 직접 편집할 수 있습니다:

```yaml
# accounts/personal.config.yaml
calendars:
  # Main calendar - always enabled
  - id: primary
    alias: Main
    enabled: true

  # Work-related calendar
  - id: abc123xyz@group.calendar.google.com
    alias: Work Tasks
    enabled: true

  # Disabled - excluded from queries
  - id: ko.south_korea#holiday@group.v.calendar.google.com
    alias: Korean Holidays
    enabled: false
```
