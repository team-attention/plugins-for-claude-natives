#!/usr/bin/env python3
"""Google Calendar 이벤트 조회 CLI.

Subagent에서 호출하여 특정 계정의 이벤트를 JSON으로 반환.

Usage:
    # ADC(Application Default Credentials) 사용 - 가장 간단
    uv run python fetch_events.py --adc --days 7

    # 특정 계정 조회
    uv run python fetch_events.py --account work --days 7

    # 모든 계정 조회 (통합)
    uv run python fetch_events.py --all --days 7

    # 캘린더 목록 조회
    uv run python fetch_events.py --adc --list-calendars
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from calendar_client import (
    CalendarClient,
    ADCCalendarClient,
    fetch_all_events,
    get_all_accounts,
    config_exists,
)


def format_event_for_display(event: dict, tz: ZoneInfo = None) -> str:
    """이벤트를 사람이 읽기 좋은 형식으로 변환."""
    if tz is None:
        tz = ZoneInfo("Asia/Seoul")

    start = event["start"]
    end = event["end"]
    account = event["account"]
    summary = event["summary"]
    calendar_alias = event.get("calendar_alias", "")

    # 시간 파싱
    if event.get("all_day"):
        time_str = "종일"
    else:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00")).astimezone(tz)
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00")).astimezone(tz)
        time_str = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"

    # 계정별 아이콘
    icon = "🔵" if account == "work" else "🟢"

    # 캘린더 별칭이 있으면 표시
    cal_info = f" [{calendar_alias}]" if calendar_alias else f" ({account})"

    return f"[{time_str}] {icon} {summary}{cal_info}"


def main():
    parser = argparse.ArgumentParser(
        description="Google Calendar 이벤트 조회"
    )
    parser.add_argument(
        "--account",
        "-a",
        help="계정 식별자 (예: work, personal)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="모든 계정의 이벤트 조회",
    )
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=7,
        help="조회할 기간 (일, 기본값: 7)",
    )
    parser.add_argument(
        "--list-calendars",
        action="store_true",
        help="캘린더 목록 조회",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="JSON 형식으로 출력",
    )
    parser.add_argument(
        "--pretty",
        "-p",
        action="store_true",
        help="사람이 읽기 좋은 형식으로 출력",
    )
    parser.add_argument(
        "--adc",
        action="store_true",
        help="Application Default Credentials 사용 (gcloud auth application-default login)",
    )

    args = parser.parse_args()
    base_path = Path(__file__).parent.parent

    # ADC 모드
    if args.adc:
        try:
            client = ADCCalendarClient(account_name="gcloud")

            # 캘린더 목록
            if args.list_calendars:
                calendars = client.list_calendars()
                if args.json or not args.pretty:
                    print(json.dumps(calendars, ensure_ascii=False, indent=2))
                else:
                    print("📋 ADC 계정의 캘린더:\n")
                    for cal in calendars:
                        primary = " (기본)" if cal["primary"] else ""
                        print(f"  - {cal['summary']}{primary}")
                        print(f"    ID: {cal['id']}")
                return

            # 이벤트 조회
            events = client.get_events(days=args.days)

            if args.json or not args.pretty:
                print(json.dumps(events, ensure_ascii=False, indent=2))
            else:
                print(f"📅 ADC 계정 - 향후 {args.days}일간 일정\n")

                # 날짜별 그룹화
                events_by_date = {}
                for event in events:
                    start = event["start"]
                    if "T" in start:
                        date = start.split("T")[0]
                    else:
                        date = start
                    events_by_date.setdefault(date, []).append(event)

                for date in sorted(events_by_date.keys()):
                    dt = datetime.fromisoformat(date)
                    print(f"### {dt.strftime('%Y-%m-%d (%a)')}")
                    for event in events_by_date[date]:
                        print(f"  {format_event_for_display(event)}")
                    print()

                print(f"📊 총 {len(events)}개 일정")

        except Exception as e:
            print(f"❌ ADC 오류: {e}", file=sys.stderr)
            print("gcloud auth application-default login 실행 필요", file=sys.stderr)
            sys.exit(1)
        return

    # 계정 목록 확인
    accounts = get_all_accounts(base_path)
    if not accounts:
        print("❌ 등록된 계정이 없습니다.", file=sys.stderr)
        print("먼저 setup_auth.py로 계정을 등록하세요:", file=sys.stderr)
        print("  uv run python setup_auth.py --account work", file=sys.stderr)
        sys.exit(1)

    # 모든 계정 조회
    if args.all:
        result = fetch_all_events(days=args.days, base_path=base_path)

        if args.json or not args.pretty:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"📅 향후 {args.days}일간 일정\n")

            # 날짜별 그룹화
            events_by_date = {}
            for event in result["events"]:
                start = event["start"]
                if "T" in start:
                    date = start.split("T")[0]
                else:
                    date = start
                events_by_date.setdefault(date, []).append(event)

            for date in sorted(events_by_date.keys()):
                dt = datetime.fromisoformat(date)
                print(f"### {dt.strftime('%Y-%m-%d (%a)')}")
                for event in events_by_date[date]:
                    print(f"  {format_event_for_display(event)}")
                print()

            # 요약
            print(f"📊 총 {result['total']}개 일정")
            for account in result["accounts"]:
                count = len([e for e in result["events"] if e["account"] == account])
                print(f"   - {account}: {count}개")

            if result["conflicts"]:
                print(f"\n⚠️  {len(result['conflicts'])}건 충돌:")
                for conflict in result["conflicts"]:
                    e1, e2 = conflict["event1"], conflict["event2"]
                    print(f"   - {e1['summary']} ({e1['account']}) ↔ {e2['summary']} ({e2['account']})")

            if result["errors"]:
                print("\n❌ 오류:")
                for account, error in result["errors"].items():
                    print(f"   - {account}: {error}")

        return

    # 특정 계정 조회
    if not args.account:
        parser.print_help()
        print()
        print(f"등록된 계정: {', '.join(accounts)}")
        return

    if args.account not in accounts:
        print(f"❌ 계정 '{args.account}'이 등록되지 않았습니다.", file=sys.stderr)
        print(f"등록된 계정: {', '.join(accounts)}", file=sys.stderr)
        sys.exit(1)

    try:
        client = CalendarClient(args.account, base_path)

        # 캘린더 목록
        if args.list_calendars:
            calendars = client.list_calendars()
            if args.json:
                print(json.dumps(calendars, ensure_ascii=False, indent=2))
            else:
                print(f"📋 '{args.account}' 계정의 캘린더:\n")
                for cal in calendars:
                    primary = " (기본)" if cal["primary"] else ""
                    print(f"  - {cal['summary']}{primary}")
                    print(f"    ID: {cal['id']}")
            return

        # 이벤트 조회: 설정 파일 있으면 설정 기반, 없으면 primary만
        has_config = config_exists(args.account, base_path)
        if has_config:
            events = client.get_events_from_config(days=args.days)
        else:
            events = client.get_events(days=args.days)

        if args.json or not args.pretty:
            print(json.dumps(events, ensure_ascii=False, indent=2))
        else:
            config_status = "(설정 파일 사용)" if has_config else "(primary 캘린더만)"
            print(f"📅 '{args.account}' 계정 - 향후 {args.days}일간 일정 {config_status}\n")

            # 날짜별 그룹화
            events_by_date = {}
            for event in events:
                start = event["start"]
                if "T" in start:
                    date = start.split("T")[0]
                else:
                    date = start
                events_by_date.setdefault(date, []).append(event)

            for date in sorted(events_by_date.keys()):
                dt = datetime.fromisoformat(date)
                print(f"### {dt.strftime('%Y-%m-%d (%a)')}")
                for event in events_by_date[date]:
                    print(f"  {format_event_for_display(event)}")
                print()

            print(f"📊 총 {len(events)}개 일정")

    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
