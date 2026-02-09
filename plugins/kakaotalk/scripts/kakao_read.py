#!/usr/bin/env python3
"""
KakaoTalk 채팅방 읽기 CLI

Usage:
    # 기본: 채팅방 열고 메시지 읽기
    python kakao_read.py "채팅방이름"
    python kakao_read.py "채팅방이름" --limit 50
    python kakao_read.py "채팅방이름" --close

    # 채팅 목록
    python kakao_read.py --list

    # 검색어로 채팅방 검색
    python kakao_read.py --search "검색어"
"""

import argparse
import json
import re
import subprocess
import sys
import time

try:
    import atomacos
except ImportError:
    print("Error: atomacos not installed. Run: uv add atomacos")
    sys.exit(1)

# Constants
KAKAO_BUNDLE_ID = "com.kakao.KakaoTalkMac"
CLAUDE_SIGNATURE = "sent with claude code"
FILE_EXTENSIONS = ['.heic', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.pdf', '.zip']
IGNORED_KEYWORDS = ['유효기간', '용량', 'KB', 'MB']
TIME_PATTERNS = ['오전', '오후', '어제', '그제', '월', '일',
                 'AM', 'PM', 'Yesterday', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', ':']
MAIN_WINDOW_TITLES = ('카카오톡', 'KakaoTalk')


# ============================================================================
# AppleScript & Keyboard Helpers
# ============================================================================

def run_applescript(script: str) -> str:
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip()


def key_code(code: int, modifiers: str = ""):
    modifier_clause = f"using {{{modifiers}}}" if modifiers else ""
    run_applescript(f'''
        tell application "System Events"
            key code {code} {modifier_clause}
        end tell
    ''')


# ============================================================================
# KakaoTalk App & Window Management
# ============================================================================

def get_kakao_app():
    try:
        return atomacos.getAppRefByBundleId(KAKAO_BUNDLE_ID)
    except ValueError:
        print("Error: KakaoTalk is not running.")
        sys.exit(1)
    except atomacos.ErrorAPIDisabled:
        print("Error: Accessibility API disabled.")
        sys.exit(1)


def find_main_window(kakao_app):
    """메인 창(카카오톡 채팅 목록 창) 찾기."""
    for win in kakao_app.windows():
        if win.AXTitle in MAIN_WINDOW_TITLES:
            return win
    return None


def find_open_chat(kakao_app, chat_name: str):
    """이미 열린 채팅방 창에서 이름이 일치하는 것 찾기."""
    for win in kakao_app.windows():
        title = win.AXTitle
        if title != "카카오톡" and chat_name.lower() in title.lower():
            return win
    return None


def get_all_chat_windows(kakao_app) -> list:
    return [win for win in kakao_app.windows() if win.AXTitle not in MAIN_WINDOW_TITLES]


def ensure_main_window_focused():
    """메인 창(채팅 목록)이 확실히 포커스되도록 함."""
    run_applescript('tell application "KakaoTalk" to activate')
    time.sleep(0.3)

    kakao = get_kakao_app()
    main_win = find_main_window(kakao)
    if not main_win:
        return False

    try:
        main_win.Raise()
        time.sleep(0.3)
    except Exception:
        pass

    return True


def clear_search_and_go_main():
    """메인 창으로 돌아가고 검색 기록 초기화."""
    run_applescript('tell application "KakaoTalk" to activate')
    time.sleep(0.3)

    kakao = get_kakao_app()
    chat_windows = [w for w in kakao.windows() if w.AXTitle != "카카오톡"]
    if chat_windows:
        key_code(53)  # ESC
        time.sleep(0.3)

    ensure_main_window_focused()


def search_and_open_chat(chat_name: str):
    """검색으로 채팅방 열기."""
    clear_search_and_go_main()

    key_code(3, "command down")  # Cmd+F
    time.sleep(0.5)
    key_code(0, "command down")  # Cmd+A
    time.sleep(0.1)

    subprocess.run(["pbcopy"], input=chat_name.encode(), check=True)
    key_code(9, "command down")  # Cmd+V
    time.sleep(0.8)

    key_code(125)  # Down arrow
    time.sleep(0.2)
    key_code(36)  # Enter
    time.sleep(0.8)


def close_chat():
    """현재 채팅창 닫기."""
    key_code(53)  # Escape
    time.sleep(0.2)


# ============================================================================
# Pattern Matching Helpers
# ============================================================================

def is_date_pattern(val: str) -> bool:
    """날짜 구분선 패턴인지 확인 (예: '1월 17일', '2025. 1. 17.', '어제', '그제')"""
    if not val:
        return False
    if re.match(r'^\d{1,2}월\s*\d{1,2}일', val):
        return True
    if re.match(r'^\d{4}\.\s*\d{1,2}\.\s*\d{1,2}', val):
        return True
    if val in ['어제', '그제']:
        return True
    return False


def is_time_pattern(val: str) -> bool:
    """시간 패턴인지 확인 (예: '오전 10:30', '오후 7:41')"""
    if not val:
        return False
    return bool(re.match(r'^(오전|오후)\s*\d{1,2}:\d{2}$', val))


def is_valid_sender_name(val: str) -> bool:
    """유효한 발신자 이름인지 확인."""
    if not val or len(val) >= 20:
        return False
    if val.startswith('[') or val.isdigit():
        return False

    # 특수문자/공백만 있는 경우 무시
    cleaned = val.strip().replace('·', '').replace('•', '').replace(' ', '')
    if not cleaned:
        return False

    # 파일명 패턴 무시
    if any(val.lower().endswith(ext) for ext in FILE_EXTENSIONS):
        return False

    # 무시할 키워드 포함 시 무시
    if any(kw in val for kw in IGNORED_KEYWORDS):
        return False

    return True


# ============================================================================
# Accessibility Helpers
# ============================================================================

def safe_get_attr(elem, attr_name, default=None):
    """안전하게 AX 속성 가져오기."""
    try:
        return getattr(elem, attr_name, default)
    except AttributeError:
        return default


def get_window_width(chat_window) -> int:
    """창 너비 가져오기."""
    try:
        win_size = chat_window.AXSize
        return win_size.width if win_size else 400
    except Exception:
        return 400


# ============================================================================
# Message Extraction
# ============================================================================

def extract_messages(chat_window, limit: int = 100) -> list[dict]:
    """채팅 창에서 메시지 추출."""
    messages = []
    chat_name = safe_get_attr(chat_window, 'AXTitle', '')
    partner_name = None
    current_date = None
    current_time = None

    children = safe_get_attr(chat_window, 'AXChildren', [])
    for child in children:
        if safe_get_attr(child, 'AXRole') != 'AXScrollArea':
            continue

        for table_child in safe_get_attr(child, 'AXChildren', []):
            if safe_get_attr(table_child, 'AXRole') != 'AXTable':
                continue

            win_width = get_window_width(chat_window)
            rows = safe_get_attr(table_child, 'AXChildren', [])

            for row in rows[:limit]:
                if safe_get_attr(row, 'AXRole') != 'AXRow':
                    continue

                row_sender = None
                row_time = None

                for cell in safe_get_attr(row, 'AXChildren', []):
                    if safe_get_attr(cell, 'AXRole') != 'AXCell':
                        continue

                    cell_pos = None
                    try:
                        cell_pos = cell.AXPosition
                    except Exception:
                        pass

                    for elem in safe_get_attr(cell, 'AXChildren', []):
                        role = safe_get_attr(elem, 'AXRole')

                        if role == 'AXStaticText':
                            row_sender, row_time, current_date, partner_name = _parse_static_text(
                                elem, row_sender, row_time, current_date, partner_name
                            )

                        elif role == 'AXTextArea':
                            msg_data = _parse_message(
                                elem, cell_pos, win_width, row_sender, row_time,
                                current_date, current_time, partner_name, chat_name
                            )
                            if msg_data:
                                messages.append(msg_data)
                                if row_time:
                                    current_time = row_time
            break
        break

    return messages


def _parse_static_text(elem, row_sender, row_time, current_date, partner_name):
    """StaticText 요소 파싱."""
    try:
        val = elem.AXValue
        if not val:
            return row_sender, row_time, current_date, partner_name

        # 줄바꿈으로 값이 합쳐진 경우
        if '\n' in val:
            for part in val.split('\n'):
                part = part.strip()
                if part.isdigit():
                    continue
                if is_date_pattern(part):
                    current_date = part.split()[0] if '요일' in part else part
                elif is_time_pattern(part):
                    row_time = part
        elif is_date_pattern(val):
            current_date = val.split()[0] if '요일' in val else val
        elif is_time_pattern(val):
            row_time = val
        elif is_valid_sender_name(val):
            row_sender = val
            partner_name = val
    except Exception:
        pass

    return row_sender, row_time, current_date, partner_name


def _parse_message(elem, cell_pos, win_width, row_sender, row_time,
                   current_date, current_time, partner_name, chat_name) -> dict | None:
    """TextArea 요소에서 메시지 파싱."""
    try:
        msg = elem.AXValue
        if not msg or not msg.strip():
            return None

        # is_me 판단 1: Claude Code 시그니처
        is_me = CLAUDE_SIGNATURE in msg

        # is_me 판단 2: 좌표 기반
        if not is_me and cell_pos:
            try:
                elem_pos = elem.AXPosition
                center_threshold = cell_pos.x + (win_width * 0.4)
                is_me = elem_pos.x > center_threshold
            except Exception:
                pass

        # 발신자 결정
        if is_me:
            sender = "나"
        elif row_sender:
            sender = row_sender
        else:
            sender = partner_name or chat_name or "상대방"

        # 시간 문자열 생성
        time_val = row_time or current_time
        if current_date and time_val:
            time_str = f"{current_date} {time_val}"
        else:
            time_str = time_val or current_date

        return {
            'sender': sender,
            'time': time_str,
            'message': msg,
            'is_me': is_me
        }
    except Exception:
        return None


# ============================================================================
# Chat List Operations
# ============================================================================

def list_chats(kakao_app, limit: int = 30) -> list[str]:
    """메인 창에서 채팅방 목록 추출."""
    chats = []

    for win in kakao_app.windows():
        if safe_get_attr(win, 'AXTitle') not in MAIN_WINDOW_TITLES:
            continue

        for child in safe_get_attr(win, 'AXChildren', []):
            if safe_get_attr(child, 'AXRole') != 'AXScrollArea':
                continue

            for table_child in safe_get_attr(child, 'AXChildren', []):
                if safe_get_attr(table_child, 'AXRole') != 'AXTable':
                    continue

                rows = safe_get_attr(table_child, 'AXChildren', [])
                for row in rows[:limit]:
                    if safe_get_attr(row, 'AXRole') != 'AXRow':
                        continue

                    texts = _extract_row_texts(row)
                    if len(texts) >= 2 and any(t in texts[1] for t in TIME_PATTERNS):
                        chats.append(texts[0])
                break
            break

    return chats


def search_chats(query: str, limit: int = 20) -> list[str]:
    """카카오톡 검색창에서 검색 후 결과 목록 반환."""
    clear_search_and_go_main()

    key_code(3, "command down")  # Cmd+F
    time.sleep(0.5)
    key_code(0, "command down")  # Cmd+A
    time.sleep(0.1)
    subprocess.run(["pbcopy"], input=query.encode(), check=True)
    key_code(9, "command down")  # Cmd+V
    time.sleep(1.0)

    kakao = get_kakao_app()
    chats = []

    for win in kakao.windows():
        if safe_get_attr(win, 'AXTitle') not in MAIN_WINDOW_TITLES:
            continue

        for child in safe_get_attr(win, 'AXChildren', []):
            if safe_get_attr(child, 'AXRole') != 'AXScrollArea':
                continue

            for table_child in safe_get_attr(child, 'AXChildren', []):
                if safe_get_attr(table_child, 'AXRole') != 'AXTable':
                    continue

                rows = safe_get_attr(table_child, 'AXChildren', [])
                for row in rows[:limit]:
                    if safe_get_attr(row, 'AXRole') != 'AXRow':
                        continue

                    texts = _extract_row_texts(row)
                    if len(texts) >= 2 and any(t in texts[1] for t in TIME_PATTERNS):
                        chats.append(texts[0])
                break
            break

    return chats


def _extract_row_texts(row) -> list[str]:
    """Row에서 모든 StaticText 값 추출."""
    texts = []
    for cell in safe_get_attr(row, 'AXChildren', []):
        if safe_get_attr(cell, 'AXRole') != 'AXCell':
            continue
        for elem in safe_get_attr(cell, 'AXChildren', []):
            if safe_get_attr(elem, 'AXRole') == 'AXStaticText':
                try:
                    val = elem.AXValue
                    if val:
                        texts.append(val)
                except Exception:
                    pass
    return texts


# ============================================================================
# Main API
# ============================================================================

def read_chat(chat_name: str, limit: int = 100) -> tuple[str | None, list[dict]]:
    """채팅방 열고 메시지 읽기."""
    kakao = get_kakao_app()

    chat_win = find_open_chat(kakao, chat_name)
    if chat_win:
        return chat_win.AXTitle, extract_messages(chat_win, limit)

    before_titles = set(win.AXTitle for win in get_all_chat_windows(kakao))
    search_and_open_chat(chat_name)
    kakao = get_kakao_app()

    after_windows = get_all_chat_windows(kakao)
    new_windows = [win for win in after_windows if win.AXTitle not in before_titles]

    if new_windows:
        chat_win = new_windows[0]
    elif (chat_win := find_open_chat(kakao, chat_name)):
        pass
    elif after_windows:
        chat_win = after_windows[0]
    else:
        return None, []

    return chat_win.AXTitle, extract_messages(chat_win, limit)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='KakaoTalk 채팅방 읽기 CLI')
    parser.add_argument('chat_name', nargs='?', help='채팅방 이름 (부분 일치)')
    parser.add_argument('--limit', '-l', type=int, default=100, help='최대 메시지 수 (기본: 100)')
    parser.add_argument('--list', action='store_true', help='채팅방 목록 보기')
    parser.add_argument('--search', '-s', type=str, help='카카오톡 검색창에서 검색 후 결과 목록')
    parser.add_argument('--close', '-c', action='store_true', help='읽고 나서 창 닫기')
    parser.add_argument('--json', '-j', action='store_true', help='JSON 출력')

    args = parser.parse_args()

    # 모드 1: 카카오톡 검색창에서 검색
    if args.search:
        chats = search_chats(args.search)
        if args.json:
            print(json.dumps({'search': args.search, 'chats': chats}, ensure_ascii=False, indent=2))
        else:
            print(f"=== '{args.search}' 검색 결과 ===\n")
            for c in chats:
                print(f"  • {c}")
            print(f"\n총 {len(chats)}개")
        return

    # 모드 2: 전체 채팅방 목록
    if args.list:
        kakao = get_kakao_app()
        chats = list_chats(kakao)
        if args.json:
            print(json.dumps({'chats': chats}, ensure_ascii=False, indent=2))
        else:
            print("=== 채팅방 목록 ===\n")
            for c in chats:
                print(f"  • {c}")
            print(f"\n총 {len(chats)}개")
        return

    # 모드 3: 기본 - 채팅방 열고 메시지 읽기
    if not args.chat_name:
        parser.print_help()
        return

    chat_name, messages = read_chat(args.chat_name, args.limit)

    if not messages:
        if args.json:
            print(json.dumps({
                'error': f"'{args.chat_name}' 채팅방을 찾을 수 없습니다.",
                'chat': None,
                'messages': []
            }, ensure_ascii=False, indent=2))
        else:
            print(f"'{args.chat_name}' 채팅방을 찾을 수 없거나 메시지가 없습니다.")
        return

    if args.json:
        print(json.dumps({'chat': chat_name, 'messages': messages}, ensure_ascii=False, indent=2))
    else:
        print(f"\n=== {chat_name} ({len(messages)}개) ===\n")
        for m in messages:
            sender = m['sender']
            time_str = m['time'] or ''
            msg = m['message'].replace('\n', ' ')
            if len(msg) > 80:
                msg = msg[:80] + '...'
            print(f"[{time_str}] {sender}: {msg}")

    if args.close:
        close_chat()
        if not args.json:
            print("\n[창 닫힘]")


if __name__ == '__main__':
    main()
