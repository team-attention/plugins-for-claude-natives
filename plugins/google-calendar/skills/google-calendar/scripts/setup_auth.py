#!/usr/bin/env python3
"""Google Calendar OAuth 인증 설정.

최초 1회 실행하여 계정별 refresh token을 저장.
이후에는 저장된 token으로 자동 인증됨.

Usage:
    uv run python setup_auth.py --account work
    uv run python setup_auth.py --account personal
"""

import argparse
import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

from calendar_client import CalendarClient, save_calendar_config


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def select_calendars_interactive(client: CalendarClient) -> list[dict]:
    """사용자에게 캘린더 선택 받기.

    Args:
        client: 인증된 CalendarClient 인스턴스

    Returns:
        선택된 캘린더 설정 리스트
    """
    calendars = client.list_calendars()

    print("\n📋 사용 가능한 캘린더:")
    for i, cal in enumerate(calendars, 1):
        primary = " (기본)" if cal.get("primary") else ""
        role = cal.get("access_role", "unknown")
        print(f"  [{i:2}] {cal['summary']}{primary}  ({role})")

    print("\n조회할 캘린더 번호를 입력하세요 (쉼표 구분, 예: 1,2,3)")
    print("Enter를 누르면 모든 캘린더 선택")

    selection = input("> ").strip()

    if not selection:
        # 전체 선택
        return [
            {"id": c["id"], "alias": c["summary"], "enabled": True}
            for c in calendars
        ]

    try:
        indices = [int(x.strip()) - 1 for x in selection.split(",")]
        return [
            {"id": calendars[i]["id"], "alias": calendars[i]["summary"], "enabled": True}
            for i in indices
            if 0 <= i < len(calendars)
        ]
    except ValueError:
        print("⚠️  잘못된 입력입니다. 모든 캘린더를 선택합니다.")
        return [
            {"id": c["id"], "alias": c["summary"], "enabled": True}
            for c in calendars
        ]


def setup_auth(account_name: str, base_path: Path) -> None:
    """OAuth 인증 플로우 실행 및 토큰 저장.

    Args:
        account_name: 계정 식별자 (예: 'work', 'personal')
        base_path: skill 루트 경로
    """
    credentials_path = base_path / "references" / "credentials.json"
    token_path = base_path / "accounts" / f"{account_name}.json"

    if not credentials_path.exists():
        print(f"❌ OAuth Client ID 파일이 없습니다: {credentials_path}")
        print()
        print("설정 방법:")
        print("1. https://console.cloud.google.com 접속")
        print("2. 프로젝트 생성 또는 선택")
        print("3. 'API 및 서비스' > '사용자 인증 정보'")
        print("4. 'OAuth 2.0 클라이언트 ID' 생성 (Desktop 유형)")
        print("5. JSON 다운로드 → references/credentials.json 저장")
        return

    # 기존 토큰 확인
    if token_path.exists():
        print(f"⚠️  계정 '{account_name}'의 토큰이 이미 존재합니다.")
        response = input("덮어쓰시겠습니까? [y/N]: ")
        if response.lower() != "y":
            print("취소됨")
            return

    print(f"🔐 '{account_name}' 계정 인증을 시작합니다...")
    print("브라우저가 열리면 Google 계정으로 로그인하세요.")
    print()

    # OAuth 플로우 실행
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        SCOPES,
    )

    # 로컬 서버로 콜백 받기
    creds = flow.run_local_server(port=0)

    # 토큰 저장
    token_path.parent.mkdir(parents=True, exist_ok=True)
    with open(token_path, "w") as f:
        json.dump(json.loads(creds.to_json()), f, indent=2)

    print()
    print(f"✅ 인증 완료! 토큰 저장됨: {token_path}")
    print(f"   계정: {account_name}")

    # 캘린더 선택
    print("\n📅 캘린더 설정을 진행합니다...")
    try:
        client = CalendarClient(account_name, base_path)
        selected_calendars = select_calendars_interactive(client)

        if selected_calendars:
            config = {"calendars": selected_calendars}
            config_path = save_calendar_config(account_name, config, base_path)
            print(f"\n✅ 캘린더 설정 저장됨: {config_path}")
            print(f"   선택된 캘린더: {len(selected_calendars)}개")
            for cal in selected_calendars:
                print(f"     - {cal['alias']}")
        else:
            print("⚠️  선택된 캘린더가 없습니다. 기본 캘린더(primary)만 사용됩니다.")
    except Exception as e:
        print(f"⚠️  캘린더 설정 중 오류 발생: {e}")
        print("   나중에 manage_config.py로 설정할 수 있습니다.")


def list_accounts(base_path: Path) -> None:
    """등록된 계정 목록 출력."""
    accounts_dir = base_path / "accounts"

    if not accounts_dir.exists():
        print("등록된 계정이 없습니다.")
        return

    accounts = [f.stem for f in accounts_dir.glob("*.json")]

    if not accounts:
        print("등록된 계정이 없습니다.")
        return

    print("📋 등록된 계정:")
    for account in accounts:
        print(f"   - {account}")


def main():
    parser = argparse.ArgumentParser(
        description="Google Calendar OAuth 인증 설정"
    )
    parser.add_argument(
        "--account",
        "-a",
        help="계정 식별자 (예: work, personal)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="등록된 계정 목록 출력",
    )

    args = parser.parse_args()
    base_path = Path(__file__).parent.parent

    if args.list:
        list_accounts(base_path)
        return

    if not args.account:
        parser.print_help()
        print()
        print("예시:")
        print("  uv run python setup_auth.py --account work")
        print("  uv run python setup_auth.py --account personal")
        print("  uv run python setup_auth.py --list")
        return

    setup_auth(args.account, base_path)


if __name__ == "__main__":
    main()
