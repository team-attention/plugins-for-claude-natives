#!/usr/bin/env python3
"""Google Calendar 설정 관리 CLI.

캘린더 선택 설정을 조회, 수정, 재구성할 수 있는 CLI 도구.

Usage:
    # 현재 설정 확인 (Google Calendar와 비교)
    uv run python manage_config.py --account personal --list

    # Google Calendar와 동기화 (변경 시 재선택)
    uv run python manage_config.py --account personal --sync

    # 특정 캘린더 활성화
    uv run python manage_config.py --account personal --enable "calendar_id"

    # 특정 캘린더 비활성화
    uv run python manage_config.py --account personal --disable "calendar_id"

    # 캘린더 설정 재구성 (interactive)
    uv run python manage_config.py --account personal --reconfigure

    # 기본 캘린더 설정 (일정 생성 시 사용)
    uv run python manage_config.py --account personal --set-primary "calendar_id"
"""

import argparse
from pathlib import Path
from typing import NamedTuple

from calendar_client import (
    CalendarClient,
    load_calendar_config,
    save_calendar_config,
    config_exists,
    get_all_accounts,
    select_primary_calendar_interactive,
)


class ConfigDiff(NamedTuple):
    """Config와 Google Calendar 비교 결과."""
    new_calendars: list[dict]      # Google에만 있음
    deleted_calendars: list[dict]  # Config에만 있음
    renamed_calendars: list[dict]  # alias != summary
    unchanged_calendars: list[dict]  # 변경 없음

    @property
    def has_changes(self) -> bool:
        return bool(self.new_calendars or self.deleted_calendars or self.renamed_calendars)


def compare_config_with_google(
    config_calendars: list[dict],
    google_calendars: list[dict],
) -> ConfigDiff:
    """Config와 Google Calendar 목록 비교."""
    config_ids = {c["id"] for c in config_calendars}
    google_ids = {c["id"] for c in google_calendars}
    google_by_id = {c["id"]: c for c in google_calendars}
    config_by_id = {c["id"]: c for c in config_calendars}

    new_calendars = [google_by_id[cid] for cid in google_ids - config_ids]
    deleted_calendars = [config_by_id[cid] for cid in config_ids - google_ids]

    renamed_calendars = []
    unchanged_calendars = []
    for cid in config_ids & google_ids:
        config_cal = config_by_id[cid]
        google_cal = google_by_id[cid]
        if config_cal.get("alias") != google_cal["summary"]:
            renamed_calendars.append({
                "id": cid,
                "old_alias": config_cal.get("alias"),
                "new_alias": google_cal["summary"],
                "enabled": config_cal.get("enabled", True),
            })
        else:
            unchanged_calendars.append(config_cal)

    return ConfigDiff(
        new_calendars=new_calendars,
        deleted_calendars=deleted_calendars,
        renamed_calendars=renamed_calendars,
        unchanged_calendars=unchanged_calendars,
    )


def list_config(account_name: str, base_path: Path) -> None:
    """현재 캘린더 설정 출력 (Google Calendar와 비교)."""
    if not config_exists(account_name, base_path):
        print(f"⚠️  계정 '{account_name}'의 설정 파일이 없습니다.")
        print("   기본값(primary 캘린더)이 사용됩니다.")
        print("   --reconfigure 옵션으로 설정을 생성할 수 있습니다.")
        return

    config = load_calendar_config(account_name, base_path)
    config_calendars = config.get("calendars", [])

    # Google Calendar API 호출하여 비교
    try:
        client = CalendarClient(account_name, base_path)
        google_calendars = client.list_calendars()
        diff = compare_config_with_google(config_calendars, google_calendars)
    except Exception as e:
        print(f"⚠️  Google Calendar 조회 실패: {e}")
        print("   오프라인 모드로 config 파일만 표시합니다.\n")
        diff = None

    print(f"📋 '{account_name}' 계정의 캘린더 설정:\n")

    if not config_calendars:
        print("  설정된 캘린더가 없습니다.")
        return

    # 설정된 캘린더 표시
    for cal in config_calendars:
        status = "✅" if cal.get("enabled", True) else "❌"
        alias = cal.get("alias", cal["id"])
        primary_marker = " ⭐" if cal.get("primary") else ""

        # stale 여부 확인
        if diff and any(d["id"] == cal["id"] for d in diff.deleted_calendars):
            print(f"  ⚠️  {alias} (Google에서 삭제됨)")
        else:
            print(f"  {status} {alias}{primary_marker}")

    enabled_count = sum(1 for c in config_calendars if c.get("enabled", True))
    print(f"\n  총 {len(config_calendars)}개 캘린더 ({enabled_count}개 활성)")

    # 변경사항 표시
    if diff and diff.has_changes:
        print("\n[변경 감지]")
        for cal in diff.deleted_calendars:
            print(f"  ⚠️  {cal.get('alias', cal['id'])} → Google에서 삭제됨")
        for cal in diff.new_calendars:
            print(f"  🆕 {cal['summary']} → 새로 추가됨")
        for cal in diff.renamed_calendars:
            print(f"  📝 {cal['new_alias']} → 이름 변경됨 (이전: {cal['old_alias']})")
        print("\n  --sync 옵션으로 동기화하세요.")

    # alias 중복 검사
    aliases = [cal.get("alias", cal["id"]) for cal in config_calendars]
    seen, dups = set(), set()
    for a in aliases:
        if a in seen:
            dups.add(a)
        seen.add(a)
    if dups:
        print(f"\n⚠️  중복된 alias: {', '.join(dups)}")

    # primary가 없으면 경고 표시
    has_primary = any(cal.get("primary") for cal in config_calendars)
    if not has_primary:
        print("\n⚠️  기본 캘린더가 설정되어 있지 않습니다.")
        print(f"   일정 생성 시 캘린더를 지정해야 합니다.")
        print(f"   --set-primary 옵션으로 기본 캘린더를 설정하세요.")


def enable_calendar(account_name: str, calendar_id: str, base_path: Path) -> None:
    """특정 캘린더 활성화."""
    config = load_calendar_config(account_name, base_path)
    calendars = config.get("calendars", [])

    found = False
    for cal in calendars:
        if cal["id"] == calendar_id or cal.get("alias") == calendar_id:
            cal["enabled"] = True
            found = True
            print(f"✅ '{cal.get('alias', cal['id'])}' 캘린더 활성화됨")
            break

    if not found:
        print(f"❌ 캘린더를 찾을 수 없습니다: {calendar_id}")
        print("   --list 옵션으로 등록된 캘린더를 확인하세요.")
        return

    save_calendar_config(account_name, config, base_path)


def disable_calendar(account_name: str, calendar_id: str, base_path: Path) -> None:
    """특정 캘린더 비활성화."""
    config = load_calendar_config(account_name, base_path)
    calendars = config.get("calendars", [])

    found = False
    for cal in calendars:
        if cal["id"] == calendar_id or cal.get("alias") == calendar_id:
            cal["enabled"] = False
            found = True
            print(f"❌ '{cal.get('alias', cal['id'])}' 캘린더 비활성화됨")
            break

    if not found:
        print(f"❌ 캘린더를 찾을 수 없습니다: {calendar_id}")
        print("   --list 옵션으로 등록된 캘린더를 확인하세요.")
        return

    save_calendar_config(account_name, config, base_path)


def _select_calendars_interactive(calendars: list[dict]) -> list[dict]:
    """사용자에게 캘린더 선택 받기 (공통 로직).

    Args:
        calendars: Google Calendar 목록

    Returns:
        선택된 캘린더 설정 리스트
    """
    print("\n조회할 캘린더 번호를 입력하세요 (쉼표 구분, 예: 1,2,3)")
    print("Enter를 누르면 모든 캘린더 선택")

    selection = input("> ").strip()

    if not selection:
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


def _save_and_print_result(
    account_name: str, selected: list[dict], base_path: Path, action: str = "저장"
) -> None:
    """선택 결과 저장 및 출력 (공통 로직)."""
    if selected:
        config = {"calendars": selected}
        config_path = save_calendar_config(account_name, config, base_path)
        print(f"\n✅ 캘린더 설정 {action}됨: {config_path}")
        print(f"   선택된 캘린더: {len(selected)}개")
        for cal in selected:
            print(f"     - {cal['alias']}")
    else:
        print("⚠️  선택된 캘린더가 없습니다.")


def reconfigure(account_name: str, base_path: Path) -> None:
    """캘린더 설정 재구성 (interactive)."""
    try:
        client = CalendarClient(account_name, base_path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return

    calendars = client.list_calendars()

    print(f"\n📋 '{account_name}' 계정에서 사용 가능한 캘린더:")
    for i, cal in enumerate(calendars, 1):
        primary = " (기본)" if cal.get("primary") else ""
        role = cal.get("access_role", "unknown")
        print(f"  [{i:2}] {cal['summary']}{primary}  ({role})")

    selected = _select_calendars_interactive(calendars)
    selected = select_primary_calendar_interactive(selected)
    _save_and_print_result(account_name, selected, base_path)


def sync_config(account_name: str, base_path: Path) -> None:
    """Google Calendar와 동기화 (변경 감지 시 interactive 재선택)."""
    print("🔄 Google Calendar와 동기화 중...")

    try:
        client = CalendarClient(account_name, base_path)
        google_calendars = client.list_calendars()
    except Exception as e:
        print(f"❌ Google Calendar 조회 실패: {e}")
        return

    # Config 로드
    if config_exists(account_name, base_path):
        config = load_calendar_config(account_name, base_path)
        config_calendars = config.get("calendars", [])
    else:
        config_calendars = []

    diff = compare_config_with_google(config_calendars, google_calendars)

    # 변경사항 없음
    if not diff.has_changes:
        print("✅ 변경사항이 없습니다. 설정이 최신 상태입니다.")
        return

    # 변경사항 표시
    print("\n[변경 감지]")
    for cal in diff.deleted_calendars:
        print(f"  ⚠️  {cal.get('alias', cal['id'])} → 제거됨")
    for cal in diff.new_calendars:
        print(f"  🆕 {cal['summary']} → 추가됨")
    for cal in diff.renamed_calendars:
        print(f"  📝 {cal['new_alias']} → 이름 변경됨 (이전: {cal['old_alias']})")

    # Interactive 재선택
    print(f"\n📋 사용 가능한 캘린더:")
    for i, cal in enumerate(google_calendars, 1):
        primary = " (기본)" if cal.get("primary") else ""
        role = cal.get("access_role", "unknown")

        # 새로 추가된 캘린더 표시
        is_new = any(c["id"] == cal["id"] for c in diff.new_calendars)
        new_marker = " 🆕" if is_new else ""

        print(f"  [{i:2}] {cal['summary']}{primary}  ({role}){new_marker}")

    selected = _select_calendars_interactive(google_calendars)
    selected = select_primary_calendar_interactive(selected)
    _save_and_print_result(account_name, selected, base_path, action="동기화")


def add_calendar(account_name: str, calendar_id: str, base_path: Path) -> None:
    """새 캘린더 추가 (alias는 Google에서 자동 조회)."""
    config = load_calendar_config(account_name, base_path)
    calendars = config.get("calendars", [])

    # 중복 확인
    for cal in calendars:
        if cal["id"] == calendar_id:
            print(f"⚠️  이미 등록된 캘린더입니다: {calendar_id}")
            return

    # Google Calendar에서 alias(summary) 조회
    try:
        client = CalendarClient(account_name, base_path)
        google_calendars = client.list_calendars()
        google_by_id = {c["id"]: c for c in google_calendars}

        if calendar_id in google_by_id:
            alias = google_by_id[calendar_id]["summary"]
        else:
            print(f"⚠️  Google Calendar에서 '{calendar_id}'를 찾을 수 없습니다.")
            print("   ID를 확인하세요. --list-calendars로 사용 가능한 캘린더를 확인할 수 있습니다.")
            return
    except Exception as e:
        print(f"❌ Google Calendar 조회 실패: {e}")
        return

    calendars.append({"id": calendar_id, "alias": alias, "enabled": True})
    config["calendars"] = calendars

    save_calendar_config(account_name, config, base_path)
    print(f"✅ 캘린더 추가됨: {alias}")


def remove_calendar(account_name: str, calendar_id: str, base_path: Path) -> None:
    """캘린더 완전 제거 (비활성화가 아닌 삭제)."""
    config = load_calendar_config(account_name, base_path)
    calendars = config.get("calendars", [])

    # 삭제 대상 찾기
    removed = None
    for cal in calendars:
        if cal["id"] == calendar_id or cal.get("alias") == calendar_id:
            removed = cal
            break

    if removed is None:
        print(f"❌ 캘린더를 찾을 수 없습니다: {calendar_id}")
        return

    # Primary 캘린더 삭제 시 경고
    was_primary = removed.get("primary", False)

    calendars = [c for c in calendars if c["id"] != removed["id"]]
    config["calendars"] = calendars
    save_calendar_config(account_name, config, base_path)

    alias = removed.get("alias", removed["id"])
    print(f"✅ 캘린더 제거됨: {alias}")

    if was_primary:
        print()
        print("⚠️  기본 캘린더가 삭제되었습니다.")
        print("   일정 생성 시 --calendar 옵션으로 캘린더를 지정하거나,")
        print(f"   --set-primary 옵션으로 새 기본 캘린더를 설정하세요.")


def set_primary_calendar(account_name: str, calendar_id: str, base_path: Path) -> None:
    """기본 캘린더 설정 (일정 생성 시 사용).

    Args:
        account_name: 계정 식별자
        calendar_id: 캘린더 ID 또는 alias
        base_path: skill 루트 경로
    """
    config = load_calendar_config(account_name, base_path)
    calendars = config.get("calendars", [])

    if not calendars:
        print(f"❌ 설정된 캘린더가 없습니다.")
        print("   --reconfigure 옵션으로 캘린더를 먼저 설정하세요.")
        return

    # Google Calendar에서 권한 조회
    google_roles = {}
    try:
        client = CalendarClient(account_name, base_path)
        for gc in client.list_calendars():
            google_roles[gc["id"]] = gc.get("access_role", "unknown")
    except Exception:
        pass  # 오프라인시 권한 검증 스킵

    found = False
    for cal in calendars:
        if cal["id"] == calendar_id or cal.get("alias") == calendar_id:
            # 권한 검증: reader/freeBusyReader면 경고
            role = google_roles.get(cal["id"], "unknown")
            if role in ("reader", "freeBusyReader"):
                print(f"⚠️  '{cal.get('alias', cal['id'])}' 캘린더는 읽기 전용({role})입니다.")
                print("   일정 생성이 실패할 수 있습니다.")

            # 기존 primary 제거
            for c in calendars:
                c.pop("primary", None)
            cal["primary"] = True
            found = True
            print(f"✅ '{cal.get('alias', cal['id'])}' 캘린더가 기본 캘린더로 설정되었습니다.")
            break

    if not found:
        print(f"❌ 캘린더를 찾을 수 없습니다: {calendar_id}")
        print("   --list 옵션으로 등록된 캘린더를 확인하세요.")
        return

    save_calendar_config(account_name, config, base_path)


def main():
    parser = argparse.ArgumentParser(description="Google Calendar 설정 관리")

    parser.add_argument(
        "--account",
        "-a",
        required=True,
        help="계정 식별자 (예: work, personal)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="현재 캘린더 설정 출력",
    )
    parser.add_argument(
        "--enable",
        metavar="CALENDAR_ID",
        help="특정 캘린더 활성화",
    )
    parser.add_argument(
        "--disable",
        metavar="CALENDAR_ID",
        help="특정 캘린더 비활성화",
    )
    parser.add_argument(
        "--reconfigure",
        action="store_true",
        help="캘린더 설정 재구성 (interactive)",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Google Calendar와 동기화 (변경 시 재선택)",
    )
    parser.add_argument(
        "--add",
        metavar="CALENDAR_ID",
        help="새 캘린더 추가",
    )
    parser.add_argument(
        "--remove",
        metavar="CALENDAR_ID",
        help="캘린더 완전 제거",
    )
    parser.add_argument(
        "--set-primary",
        metavar="CALENDAR_ID",
        help="기본 캘린더 설정 (일정 생성 시 사용)",
    )

    args = parser.parse_args()
    base_path = Path(__file__).parent.parent

    # 계정 존재 확인
    accounts = get_all_accounts(base_path)
    if args.account not in accounts:
        print(f"❌ 계정 '{args.account}'이 등록되지 않았습니다.")
        if accounts:
            print(f"   등록된 계정: {', '.join(accounts)}")
        else:
            print("   등록된 계정이 없습니다.")
            print("   setup_auth.py로 계정을 먼저 등록하세요.")
        return

    # 명령 실행
    if args.list:
        list_config(args.account, base_path)
    elif args.sync:
        sync_config(args.account, base_path)
    elif args.enable:
        enable_calendar(args.account, args.enable, base_path)
    elif args.disable:
        disable_calendar(args.account, args.disable, base_path)
    elif args.reconfigure:
        reconfigure(args.account, base_path)
    elif args.add:
        add_calendar(args.account, args.add, base_path)
    elif args.remove:
        remove_calendar(args.account, args.remove, base_path)
    elif getattr(args, "set_primary", None):
        set_primary_calendar(args.account, args.set_primary, base_path)
    else:
        parser.print_help()
        print()
        print("예시:")
        print(f"  uv run python manage_config.py --account {args.account} --list")
        print(f"  uv run python manage_config.py --account {args.account} --sync")
        print(f"  uv run python manage_config.py --account {args.account} --set-primary \"캘린더 이름\"")


if __name__ == "__main__":
    main()