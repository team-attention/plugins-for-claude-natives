#!/usr/bin/env python3
"""
KakaoTalk 메시지 발송

Usage:
    python kakao_send.py "채팅방이름" "메시지"
    python kakao_send.py "구봉" "안녕하세요!"
    python kakao_send.py "구봉" "밥 먹었어?" --close        # 보내고 창 닫기
    python kakao_send.py "구봉" "밥 먹었어?" --no-signature  # 서명 없이 보내기
"""

SIGNATURE = "\n\nsent with claude code"

import argparse
import subprocess
import sys
import time

try:
    import atomacos
except ImportError:
    print("Error: atomacos not installed. Run: uv add atomacos")
    sys.exit(1)

KAKAO_BUNDLE_ID = "com.kakao.KakaoTalkMac"
MAIN_WINDOW_TITLES = ("카카오톡", "KakaoTalk")


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


def type_text(text: str):
    """클립보드를 통해 텍스트 입력 (한글 지원)."""
    subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
    key_code(9, "command down")  # Cmd+V


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


def raise_main_window(kakao_app):
    """메인 창을 앞으로 가져오기."""
    main_win = find_main_window(kakao_app)
    if main_win:
        try:
            main_win.Raise()
            return True
        except Exception:
            pass
    return False


def find_open_chat(kakao_app, chat_name: str):
    """이미 열린 채팅방 창에서 이름이 일치하는 것 찾기."""
    for win in kakao_app.windows():
        title = win.AXTitle
        if title in MAIN_WINDOW_TITLES:
            continue
        if chat_name.lower() in title.lower():
            return win
    return None


def get_all_chat_windows(kakao_app) -> list:
    return [win for win in kakao_app.windows() if win.AXTitle not in MAIN_WINDOW_TITLES]


def search_and_open_chat(chat_name: str):
    """검색으로 채팅방 열기."""
    run_applescript('tell application "KakaoTalk" to activate')
    time.sleep(0.3)

    kakao = get_kakao_app()
    raise_main_window(kakao)
    time.sleep(0.3)

    key_code(3, "command down")  # Cmd+F (검색)
    time.sleep(0.5)

    subprocess.run(["pbcopy"], input=chat_name.encode(), check=True)
    key_code(9, "command down")  # Cmd+V
    time.sleep(0.8)

    key_code(125)  # Down arrow
    time.sleep(0.2)
    key_code(36)  # Enter
    time.sleep(0.8)


def open_chat(chat_name: str):
    """채팅방 열기 (이미 열려있으면 그대로, 아니면 검색해서 열기)."""
    kakao = get_kakao_app()

    # 이미 열린 채팅방 확인
    chat_win = find_open_chat(kakao, chat_name)
    if chat_win:
        # 해당 창을 앞으로
        run_applescript('tell application "KakaoTalk" to activate')
        time.sleep(0.2)
        try:
            chat_win.Raise()
        except:
            pass
        return chat_win.AXTitle

    # 검색해서 열기
    before_titles = set(win.AXTitle for win in get_all_chat_windows(kakao))
    search_and_open_chat(chat_name)

    kakao = get_kakao_app()
    after_windows = get_all_chat_windows(kakao)
    new_windows = [win for win in after_windows if win.AXTitle not in before_titles]

    if new_windows:
        return new_windows[0].AXTitle

    chat_win = find_open_chat(kakao, chat_name)
    if chat_win:
        return chat_win.AXTitle

    if after_windows:
        return after_windows[0].AXTitle

    return None


def send_message_via_keyboard(message: str):
    """키보드 입력으로 메시지 전송."""
    # 텍스트 입력 (클립보드 사용)
    type_text(message)
    time.sleep(0.3)

    # Enter로 전송
    key_code(36)  # Enter
    time.sleep(0.3)


def close_chat():
    """현재 채팅창 닫기."""
    key_code(53)  # Escape
    time.sleep(0.2)


def send_message(chat_name: str, message: str, close_after: bool = False) -> dict:
    """채팅방에 메시지 발송."""
    result = {
        'success': False,
        'chat': None,
        'message': message,
        'error': None
    }

    # 1. 채팅방 열기
    chat_title = open_chat(chat_name)
    if not chat_title:
        result['error'] = f"'{chat_name}' 채팅방을 찾을 수 없습니다."
        return result

    result['chat'] = chat_title
    time.sleep(0.3)

    # 2. 메시지 전송 (키보드 입력 방식)
    # 채팅창이 활성화된 상태에서 바로 입력
    send_message_via_keyboard(message)

    result['success'] = True

    # 3. 필요시 창 닫기
    if close_after:
        close_chat()

    return result


def main():
    parser = argparse.ArgumentParser(description='KakaoTalk 메시지 발송')
    parser.add_argument('chat_name', help='채팅방 이름 (부분 일치)')
    parser.add_argument('message', help='보낼 메시지')
    parser.add_argument('--close', '-c', action='store_true', help='보내고 나서 창 닫기')
    parser.add_argument('--json', '-j', action='store_true', help='JSON 출력')
    parser.add_argument('--no-signature', action='store_true', help='서명 없이 보내기 (기본: "sent with claude code" 붙음)')

    args = parser.parse_args()

    # 서명 추가 (--no-signature가 없으면)
    message = args.message
    if not args.no_signature:
        message = args.message + SIGNATURE

    result = send_message(args.chat_name, message, args.close)

    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            print(f"✓ [{result['chat']}]에 메시지 전송 완료")
            print(f"  → {result['message']}")
        else:
            print(f"✗ 전송 실패: {result['error']}")
            sys.exit(1)


if __name__ == '__main__':
    main()
