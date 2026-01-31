#!/usr/bin/env python3
"""Gmail OAuth 인증 설정.

최초 1회 실행하여 계정별 refresh token을 저장.
이후에는 저장된 token으로 자동 인증됨.

Usage:
    uv run python setup_auth.py --account personal --email user@gmail.com
    uv run python setup_auth.py --account work --email work@company.com --description "회사 업무용"
    uv run python setup_auth.py --list
"""

import argparse
import json
from pathlib import Path

import yaml
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",  # 읽기/수정/삭제
    "https://www.googleapis.com/auth/gmail.send",    # 메일 발송
    "https://www.googleapis.com/auth/gmail.labels",  # 라벨 관리
]


def load_accounts_config(base_path: Path) -> dict:
    """accounts.yaml 로드."""
    config_path = base_path / "accounts.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {"accounts": {}}
    return {"accounts": {}}


def save_accounts_config(base_path: Path, config: dict) -> None:
    """accounts.yaml 저장."""
    config_path = base_path / "accounts.yaml"

    # YAML 헤더 코멘트
    header = """# Gmail 계정 설정
# 계정별로 이메일 주소와 설명을 관리합니다.
# 토큰 파일은 accounts/{name}.json에 별도 저장됩니다.

"""

    with open(config_path, "w") as f:
        f.write(header)
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def setup_auth(
    account_name: str,
    base_path: Path,
    email: str | None = None,
    description: str | None = None,
) -> None:
    """OAuth 인증 플로우 실행 및 토큰 저장.

    Args:
        account_name: 계정 식별자 (예: 'work', 'personal')
        base_path: skill 루트 경로
        email: 이메일 주소 (accounts.yaml에 저장)
        description: 계정 설명 (accounts.yaml에 저장)
    """
    credentials_path = base_path / "references" / "credentials.json"
    token_path = base_path / "accounts" / f"{account_name}.json"

    if not credentials_path.exists():
        print(f"❌ OAuth Client ID 파일이 없습니다: {credentials_path}")
        print()
        print("설정 방법:")
        print("1. https://console.cloud.google.com 접속")
        print("2. 프로젝트 생성 또는 선택")
        print("3. 'API 및 서비스' > 'Gmail API' 활성화")
        print("4. 'API 및 서비스' > '사용자 인증 정보'")
        print("5. 'OAuth 2.0 클라이언트 ID' 생성 (Desktop 유형)")
        print("6. JSON 다운로드 → references/credentials.json 저장")
        return

    if token_path.exists():
        print(f"⚠️  계정 '{account_name}'의 토큰이 이미 존재합니다.")
        response = input("덮어쓰시겠습니까? [y/N]: ")
        if response.lower() != "y":
            print("취소됨")
            return

    print(f"🔐 '{account_name}' 계정 인증을 시작합니다...")
    print("브라우저가 열리면 Google 계정으로 로그인하세요.")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        SCOPES,
    )

    creds = flow.run_local_server(port=0)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    with open(token_path, "w") as f:
        json.dump(json.loads(creds.to_json()), f, indent=2)

    # accounts.yaml 업데이트
    config = load_accounts_config(base_path)

    # 인증된 이메일 주소 가져오기 (제공되지 않은 경우)
    if not email:
        try:
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials

            temp_creds = Credentials.from_authorized_user_info(
                json.loads(creds.to_json()),
                SCOPES,
            )
            service = build("gmail", "v1", credentials=temp_creds)
            profile = service.users().getProfile(userId="me").execute()
            email = profile.get("emailAddress", "")
        except Exception:
            email = ""

    config["accounts"][account_name] = {
        "email": email,
        "description": description or "",
    }
    save_accounts_config(base_path, config)

    print()
    print(f"✅ 인증 완료!")
    print(f"   계정명: {account_name}")
    print(f"   이메일: {email}")
    print(f"   토큰: {token_path}")


def list_accounts(base_path: Path) -> None:
    """등록된 계정 목록 출력."""
    config = load_accounts_config(base_path)
    accounts_dir = base_path / "accounts"

    # accounts.yaml에서 계정 정보 읽기
    accounts_config = config.get("accounts", {})

    # 토큰 파일 존재 여부 확인
    token_files = set()
    if accounts_dir.exists():
        token_files = {f.stem for f in accounts_dir.glob("*.json")}

    if not accounts_config and not token_files:
        print("등록된 계정이 없습니다.")
        return

    print("📋 등록된 계정:")
    print()

    # accounts.yaml에 있는 계정 출력
    for name, info in accounts_config.items():
        email = info.get("email", "")
        description = info.get("description", "")
        has_token = "✅" if name in token_files else "❌"

        print(f"   {has_token} {name}")
        if email:
            print(f"      이메일: {email}")
        if description:
            print(f"      설명: {description}")
        print()

    # 토큰은 있지만 accounts.yaml에 없는 계정 경고
    orphan_tokens = token_files - set(accounts_config.keys())
    if orphan_tokens:
        print("⚠️  accounts.yaml에 없는 토큰:")
        for name in orphan_tokens:
            print(f"   - {name}.json")


def main():
    parser = argparse.ArgumentParser(description="Gmail OAuth 인증 설정")
    parser.add_argument(
        "--account",
        "-a",
        help="계정 식별자 (예: work, personal)",
    )
    parser.add_argument(
        "--email",
        "-e",
        help="이메일 주소 (자동 감지되지만 명시 가능)",
    )
    parser.add_argument(
        "--description",
        "-d",
        help="계정 설명 (예: '회사 업무용')",
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
        print("  uv run python setup_auth.py --account personal --description '개인 Gmail'")
        print("  uv run python setup_auth.py --account work --description '회사 업무용'")
        print("  uv run python setup_auth.py --list")
        return

    setup_auth(args.account, base_path, args.email, args.description)


if __name__ == "__main__":
    main()
