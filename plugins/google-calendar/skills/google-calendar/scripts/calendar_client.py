"""Google Calendar API 클라이언트.

여러 Google 계정의 캘린더를 조회하기 위한 클라이언트.
저장된 refresh token을 사용하여 매번 인증 없이 API 호출.

Environment Variables:
    GOOGLE_CALENDAR_SKILL_PATH: Skill 루트 경로 (기본값: 이 파일의 부모의 부모)
    GOOGLE_CALENDAR_TIMEOUT: API 요청 타임아웃 초 (기본값: 30)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import google.auth
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import httplib2

# 환경변수에서 설정 로드
DEFAULT_TIMEOUT = int(os.environ.get("GOOGLE_CALENDAR_TIMEOUT", "30"))


class CalendarClient:
    """단일 Google 계정의 캘린더 클라이언트."""

    SCOPES = ["https://www.googleapis.com/auth/calendar"]  # 읽기/쓰기 권한

    def __init__(
        self,
        account_name: str,
        base_path: Optional[Path] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Args:
            account_name: 계정 식별자 (예: 'work', 'personal')
            base_path: skill 루트 경로 (환경변수 GOOGLE_CALENDAR_SKILL_PATH 또는 기본값)
            timeout: API 요청 타임아웃 (초)
        """
        self.account_name = account_name
        self.timeout = timeout

        # 경로 우선순위: 인자 > 환경변수 > 기본값
        if base_path:
            self.base_path = base_path
        elif os.environ.get("GOOGLE_CALENDAR_SKILL_PATH"):
            self.base_path = Path(os.environ["GOOGLE_CALENDAR_SKILL_PATH"])
        else:
            self.base_path = Path(__file__).parent.parent

        self.creds = self._load_credentials()

    def _load_credentials(self):
        """저장된 refresh token으로 credentials 로드 및 갱신."""
        token_path = self.base_path / f"accounts/{self.account_name}.json"

        if not token_path.exists():
            raise FileNotFoundError(
                f"계정 '{self.account_name}'의 토큰이 없습니다. "
                f"먼저 setup_auth.py --account {self.account_name} 실행 필요"
            )

        with open(token_path) as f:
            token_data = json.load(f)

        # ADC 형식인지 확인 (client_id가 있으면 ADC)
        if "client_id" in token_data and "type" not in token_data:
            # gcloud ADC 형식 - quota project 포함
            creds = Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=self.SCOPES,
            )
            # quota project 설정 (있을 때만)
            quota_project = token_data.get("quota_project_id")
            if quota_project:
                creds = creds.with_quota_project(quota_project)
        else:
            # 일반 OAuth 토큰 형식
            creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)

        # 만료 시 자동 갱신
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # 갱신된 토큰 저장
            with open(token_path, "w") as f:
                json.dump(json.loads(creds.to_json()), f, indent=2)

        return creds

    def get_events(
        self,
        days: int = 7,
        calendar_id: str = "primary",
        max_results: int = 100,
    ) -> list[dict]:
        """향후 N일간 이벤트 조회.

        Args:
            days: 조회할 기간 (일)
            calendar_id: 캘린더 ID (기본값: primary)
            max_results: 최대 결과 수

        Returns:
            이벤트 목록 (dict 리스트)
        """
        # credentials로 서비스 빌드
        service = build("calendar", "v3", credentials=self.creds)

        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=days)).isoformat() + "Z"

        events = []
        page_token = None

        while True:
            result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                    maxResults=max_results,
                    pageToken=page_token,
                )
                .execute()
            )

            for event in result.get("items", []):
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))

                events.append(
                    {
                        "account": self.account_name,
                        "id": event.get("id"),
                        "summary": event.get("summary", "(제목 없음)"),
                        "start": start,
                        "end": end,
                        "all_day": "date" in event["start"],
                        "location": event.get("location"),
                        "description": event.get("description"),
                        "attendees": [
                            a.get("email") for a in event.get("attendees", [])
                        ],
                        "status": event.get("status"),
                        "html_link": event.get("htmlLink"),
                    }
                )

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return events

    def list_calendars(self) -> list[dict]:
        """사용 가능한 모든 캘린더 목록 조회."""
        service = build("calendar", "v3", credentials=self.creds)

        calendars = []
        page_token = None

        while True:
            result = (
                service.calendarList().list(pageToken=page_token).execute()
            )

            for cal in result.get("items", []):
                calendars.append(
                    {
                        "id": cal.get("id"),
                        "summary": cal.get("summary"),
                        "primary": cal.get("primary", False),
                        "access_role": cal.get("accessRole"),
                    }
                )

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return calendars

    def create_event(
        self,
        summary: str,
        start: str,
        end: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        calendar_id: str = "primary",
        timezone: str = "Asia/Seoul",
    ) -> dict:
        """새 이벤트 생성.

        Args:
            summary: 일정 제목
            start: 시작 시간 (ISO format: 2024-01-15T09:00:00 또는 2024-01-15)
            end: 종료 시간 (ISO format)
            description: 일정 설명
            location: 장소
            attendees: 참석자 이메일 목록
            calendar_id: 캘린더 ID (기본값: primary)
            timezone: 타임존 (기본값: Asia/Seoul)

        Returns:
            생성된 이벤트 정보
        """
        service = build("calendar", "v3", credentials=self.creds)

        # 종일 일정인지 확인 (T가 없으면 종일)
        is_all_day = "T" not in start

        event = {
            "summary": summary,
        }

        if is_all_day:
            event["start"] = {"date": start}
            event["end"] = {"date": end}
        else:
            event["start"] = {"dateTime": start, "timeZone": timezone}
            event["end"] = {"dateTime": end, "timeZone": timezone}

        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        result = service.events().insert(calendarId=calendar_id, body=event).execute()

        return {
            "id": result.get("id"),
            "summary": result.get("summary"),
            "start": result["start"].get("dateTime", result["start"].get("date")),
            "end": result["end"].get("dateTime", result["end"].get("date")),
            "html_link": result.get("htmlLink"),
            "status": "created",
        }

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
        timezone: str = "Asia/Seoul",
    ) -> dict:
        """기존 이벤트 수정.

        Args:
            event_id: 수정할 이벤트 ID
            summary: 새 제목 (None이면 유지)
            start: 새 시작 시간 (None이면 유지)
            end: 새 종료 시간 (None이면 유지)
            description: 새 설명 (None이면 유지)
            location: 새 장소 (None이면 유지)
            calendar_id: 캘린더 ID
            timezone: 타임존

        Returns:
            수정된 이벤트 정보
        """
        service = build("calendar", "v3", credentials=self.creds)

        # 기존 이벤트 조회
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        # 변경할 필드만 업데이트
        if summary is not None:
            event["summary"] = summary
        if description is not None:
            event["description"] = description
        if location is not None:
            event["location"] = location

        if start is not None:
            is_all_day = "T" not in start
            if is_all_day:
                event["start"] = {"date": start}
            else:
                event["start"] = {"dateTime": start, "timeZone": timezone}

        if end is not None:
            is_all_day = "T" not in end
            if is_all_day:
                event["end"] = {"date": end}
            else:
                event["end"] = {"dateTime": end, "timeZone": timezone}

        result = (
            service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event)
            .execute()
        )

        return {
            "id": result.get("id"),
            "summary": result.get("summary"),
            "start": result["start"].get("dateTime", result["start"].get("date")),
            "end": result["end"].get("dateTime", result["end"].get("date")),
            "html_link": result.get("htmlLink"),
            "status": "updated",
        }

    def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> dict:
        """이벤트 삭제.

        Args:
            event_id: 삭제할 이벤트 ID
            calendar_id: 캘린더 ID

        Returns:
            삭제 결과
        """
        service = build("calendar", "v3", credentials=self.creds)

        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

        return {
            "id": event_id,
            "status": "deleted",
        }


class ADCCalendarClient:
    """Application Default Credentials를 사용하는 캘린더 클라이언트.

    gcloud auth application-default login으로 인증된 계정 사용.
    별도 토큰 파일 없이 바로 사용 가능.
    """

    SCOPES = ["https://www.googleapis.com/auth/calendar"]  # 읽기/쓰기 권한

    def __init__(self, account_name: str = "default", timeout: int = DEFAULT_TIMEOUT):
        """
        Args:
            account_name: 계정 식별자 (표시용)
            timeout: API 요청 타임아웃 (초)
        """
        self.account_name = account_name
        self.timeout = timeout
        self.creds, self.project = google.auth.default(scopes=self.SCOPES)

    def get_events(
        self,
        days: int = 7,
        calendar_id: str = "primary",
        max_results: int = 100,
    ) -> list[dict]:
        """향후 N일간 이벤트 조회."""
        http = httplib2.Http(timeout=self.timeout)
        http = google.auth.transport.requests.AuthorizedSession(self.creds)
        service = build("calendar", "v3", credentials=self.creds)

        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=days)).isoformat() + "Z"

        events = []
        page_token = None

        while True:
            result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                    maxResults=max_results,
                    pageToken=page_token,
                )
                .execute()
            )

            for event in result.get("items", []):
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))

                events.append(
                    {
                        "account": self.account_name,
                        "id": event.get("id"),
                        "summary": event.get("summary", "(제목 없음)"),
                        "start": start,
                        "end": end,
                        "all_day": "date" in event["start"],
                        "location": event.get("location"),
                        "description": event.get("description"),
                        "attendees": [
                            a.get("email") for a in event.get("attendees", [])
                        ],
                        "status": event.get("status"),
                        "html_link": event.get("htmlLink"),
                    }
                )

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return events

    def list_calendars(self) -> list[dict]:
        """사용 가능한 모든 캘린더 목록 조회."""
        service = build("calendar", "v3", credentials=self.creds)

        calendars = []
        page_token = None

        while True:
            result = service.calendarList().list(pageToken=page_token).execute()

            for cal in result.get("items", []):
                calendars.append(
                    {
                        "id": cal.get("id"),
                        "summary": cal.get("summary"),
                        "primary": cal.get("primary", False),
                        "access_role": cal.get("accessRole"),
                    }
                )

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return calendars

    def create_event(
        self,
        summary: str,
        start: str,
        end: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        calendar_id: str = "primary",
        timezone: str = "Asia/Seoul",
    ) -> dict:
        """새 이벤트 생성."""
        service = build("calendar", "v3", credentials=self.creds)

        is_all_day = "T" not in start
        event = {"summary": summary}

        if is_all_day:
            event["start"] = {"date": start}
            event["end"] = {"date": end}
        else:
            event["start"] = {"dateTime": start, "timeZone": timezone}
            event["end"] = {"dateTime": end, "timeZone": timezone}

        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        result = service.events().insert(calendarId=calendar_id, body=event).execute()

        return {
            "id": result.get("id"),
            "summary": result.get("summary"),
            "start": result["start"].get("dateTime", result["start"].get("date")),
            "end": result["end"].get("dateTime", result["end"].get("date")),
            "html_link": result.get("htmlLink"),
            "status": "created",
        }

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
        timezone: str = "Asia/Seoul",
    ) -> dict:
        """기존 이벤트 수정."""
        service = build("calendar", "v3", credentials=self.creds)

        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        if summary is not None:
            event["summary"] = summary
        if description is not None:
            event["description"] = description
        if location is not None:
            event["location"] = location

        if start is not None:
            is_all_day = "T" not in start
            if is_all_day:
                event["start"] = {"date": start}
            else:
                event["start"] = {"dateTime": start, "timeZone": timezone}

        if end is not None:
            is_all_day = "T" not in end
            if is_all_day:
                event["end"] = {"date": end}
            else:
                event["end"] = {"dateTime": end, "timeZone": timezone}

        result = (
            service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event)
            .execute()
        )

        return {
            "id": result.get("id"),
            "summary": result.get("summary"),
            "start": result["start"].get("dateTime", result["start"].get("date")),
            "end": result["end"].get("dateTime", result["end"].get("date")),
            "html_link": result.get("htmlLink"),
            "status": "updated",
        }

    def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> dict:
        """이벤트 삭제."""
        service = build("calendar", "v3", credentials=self.creds)

        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

        return {
            "id": event_id,
            "status": "deleted",
        }


def get_all_accounts(base_path: Optional[Path] = None) -> list[str]:
    """등록된 모든 계정 이름 반환."""
    base_path = base_path or Path(__file__).parent.parent
    accounts_dir = base_path / "accounts"

    if not accounts_dir.exists():
        return []

    return [
        f.stem
        for f in accounts_dir.glob("*.json")
        if f.stem not in ("credentials",)
    ]


def fetch_all_events(days: int = 7, base_path: Optional[Path] = None) -> dict:
    """모든 계정의 이벤트를 조회하여 통합.

    Args:
        days: 조회할 기간 (일)
        base_path: skill 루트 경로

    Returns:
        {
            "accounts": ["work", "personal"],
            "events": [...],
            "errors": {"account_name": "error message"},
            "total": 10,
            "conflicts": [...]
        }
    """
    accounts = get_all_accounts(base_path)
    all_events = []
    errors = {}

    for account in accounts:
        try:
            client = CalendarClient(account, base_path)
            events = client.get_events(days=days)
            all_events.extend(events)
        except Exception as e:
            errors[account] = str(e)

    # 시간순 정렬
    all_events.sort(key=lambda x: x["start"])

    # 충돌 감지
    conflicts = detect_conflicts(all_events)

    return {
        "accounts": accounts,
        "events": all_events,
        "errors": errors,
        "total": len(all_events),
        "conflicts": conflicts,
    }


def detect_conflicts(events: list[dict]) -> list[dict]:
    """동일 시간대 이벤트 충돌 감지.

    Args:
        events: 시간순 정렬된 이벤트 목록

    Returns:
        충돌 이벤트 쌍 목록
    """
    conflicts = []

    for i, event1 in enumerate(events):
        if event1.get("all_day"):
            continue

        for event2 in events[i + 1 :]:
            if event2.get("all_day"):
                continue

            # 같은 계정이면 충돌 아님
            if event1["account"] == event2["account"]:
                continue

            # 시간 비교
            start1 = datetime.fromisoformat(event1["start"].replace("Z", "+00:00"))
            end1 = datetime.fromisoformat(event1["end"].replace("Z", "+00:00"))
            start2 = datetime.fromisoformat(event2["start"].replace("Z", "+00:00"))
            end2 = datetime.fromisoformat(event2["end"].replace("Z", "+00:00"))

            # event2 시작이 event1 끝 이후면 더 이상 비교 불필요
            if start2 >= end1:
                break

            # 겹침 확인
            if start1 < end2 and start2 < end1:
                conflicts.append(
                    {
                        "event1": {
                            "account": event1["account"],
                            "summary": event1["summary"],
                            "start": event1["start"],
                            "end": event1["end"],
                        },
                        "event2": {
                            "account": event2["account"],
                            "summary": event2["summary"],
                            "start": event2["start"],
                            "end": event2["end"],
                        },
                    }
                )

    return conflicts
