#!/usr/bin/env python3
"""
KakaoTalk 메시지 발송

Usage:
    python kakao_send.py "채팅방이름" "메시지"
    python kakao_send.py "구봉" "안녕하세요!"
    python kakao_send.py "구봉" "밥 먹었어?" --close            # 보내고 창 닫기
    python kakao_send.py "구봉" "밥 먹었어?" --no-signature      # 서명 없이 보내기
    python kakao_send.py "구봉" "" --file /path/to/photo.jpg   # 파일만 첨부
    python kakao_send.py "구봉" "사진 봐봐" --file ~/a.png       # 파일 + 텍스트 (2개 메시지)
"""

SIGNATURE = "\n\nsent with claude code"

import argparse
import os
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


def set_clipboard_file(path: str):
    """클립보드에 POSIX 파일 참조를 올림 (Cmd+V 시 KakaoTalk 이 첨부로 처리)."""
    # AppleScript 문자열 안에 들어가는 경로의 백슬래시·따옴표 이스케이프
    escaped = path.replace("\\", "\\\\").replace('"', '\\"')
    run_applescript(f'set the clipboard to (POSIX file "{escaped}")')


def paste_file(path: str):
    """파일 참조를 클립보드에 올리고 Cmd+V 로 첨부 입력."""
    set_clipboard_file(path)
    # KakaoTalk 이 파일 참조를 인식하기까지 약간의 지연이 필요할 수 있어 살짝 대기
    time.sleep(0.2)
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


def send_file_via_keyboard(file_path: str):
    """파일 첨부 전송. 파일 참조를 붙여넣은 뒤 Enter 로 전송."""
    paste_file(file_path)
    # KakaoTalk 이 첨부 미리보기/확인 UI 를 띄우는 데 시간이 걸리므로 충분히 대기
    time.sleep(0.8)

    # Enter 로 전송 (필요 시 확인 다이얼로그도 같은 키로 통과)
    key_code(36)
    time.sleep(0.5)


def close_chat():
    """현재 채팅창 닫기."""
    key_code(53)  # Escape
    time.sleep(0.2)


def send_message(chat_name: str, message: str, close_after: bool = False, file_path=None) -> dict:
    """채팅방에 메시지/파일 발송.

    file_path 와 message 가 모두 주어지면, 파일을 먼저 보낸 뒤 텍스트를 별도 메시지로 보낸다.
    KakaoTalk 클립보드 핸들러가 텍스트와 파일 참조를 동시에 paste 할 수 없기 때문.
    """
    result = {
        'success': False,
        'chat': None,
        'message': message,
        'file': file_path,
        'error': None
    }

    # 1. 채팅방 열기
    chat_title = open_chat(chat_name)
    if not chat_title:
        result['error'] = f"'{chat_name}' 채팅방을 찾을 수 없습니다."
        return result

    result['chat'] = chat_title
    time.sleep(0.3)

    # 2. 파일 첨부 (있으면 먼저)
    if file_path:
        send_file_via_keyboard(file_path)

    # 3. 텍스트 메시지 (있으면 뒤따라)
    if message:
        send_message_via_keyboard(message)

    result['success'] = True

    # 4. 필요시 창 닫기
    if close_after:
        close_chat()

    return result


def main():
    parser = argparse.ArgumentParser(description='KakaoTalk 메시지 발송')
    parser.add_argument('chat_name', help='채팅방 이름 (부분 일치)')
    parser.add_argument('message', help='보낼 메시지 (--file 만 사용할 땐 빈 문자열 "" 가능)')
    parser.add_argument('--close', '-c', action='store_true', help='보내고 나서 창 닫기')
    parser.add_argument('--json', '-j', action='store_true', help='JSON 출력')
    parser.add_argument('--no-signature', action='store_true', help='서명 없이 보내기 (기본: "sent with claude code" 붙음)')
    parser.add_argument('--file', '-f', dest='file', metavar='PATH',
                        help='첨부할 파일 경로. message 와 함께 주면 파일 먼저, 텍스트가 뒤따른 별도 메시지로 전송됨.')

    args = parser.parse_args()

    # --file 처리: 절대경로 정규화 + 존재/파일 검증
    file_path = None
    if args.file:
        file_path = os.path.abspath(os.path.expanduser(args.file))
        if not os.path.exists(file_path):
            print(f"✗ 파일이 존재하지 않습니다: {file_path}")
            sys.exit(1)
        if not os.path.isfile(file_path):
            print(f"✗ 파일이 아닙니다 (디렉토리 등): {file_path}")
            sys.exit(1)

    # 서명 정책:
    # - 텍스트가 비어있으면 (파일만 보내는 경우 포함) 서명 추가 안 함.
    #   → 파일 첨부 직후 "sent with claude code" 만 따로 가는 건 어색하므로.
    # - 텍스트가 있으면 기존 동작대로 --no-signature 가 없을 때만 서명 추가.
    message = args.message
    if message and not args.no_signature:
        message = message + SIGNATURE

    if not message and not file_path:
        print("✗ 보낼 내용이 없습니다 (메시지 또는 --file 중 하나는 필요).")
        sys.exit(1)

    result = send_message(args.chat_name, message, args.close, file_path=file_path)

    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            print(f"✓ [{result['chat']}]에 전송 완료")
            if result.get('file'):
                print(f"  📎 {result['file']}")
            if result['message']:
                print(f"  → {result['message']}")
        else:
            print(f"✗ 전송 실패: {result['error']}")
            sys.exit(1)


if __name__ == '__main__':
    main()
