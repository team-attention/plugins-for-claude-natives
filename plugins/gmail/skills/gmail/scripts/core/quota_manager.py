"""Gmail API Quota Management.

Gmail API 할당량 관리를 위한 모듈.

Quota Units (Gmail API Reference):
- messages.list: 5 units
- messages.get: 5 units
- messages.send: 100 units
- messages.modify: 5 units
- messages.batchModify: 50 units
- threads.list: 5 units
- threads.get: 10 units

Rate Limits:
- Per-user: 250 quota units per second
- Daily: 1,000,000,000 units (workspace), varies for consumer

Reference:
    https://developers.google.com/workspace/gmail/api/reference/quota
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Optional


class QuotaUnit(IntEnum):
    """API 메서드별 할당량 단위."""

    # Messages
    MESSAGES_LIST = 5
    MESSAGES_GET = 5
    MESSAGES_SEND = 100
    MESSAGES_MODIFY = 5
    MESSAGES_BATCH_MODIFY = 50
    MESSAGES_DELETE = 10
    MESSAGES_TRASH = 5
    MESSAGES_UNTRASH = 5

    # Threads
    THREADS_LIST = 5
    THREADS_GET = 10
    THREADS_MODIFY = 5
    THREADS_TRASH = 5

    # Labels
    LABELS_LIST = 1
    LABELS_GET = 1
    LABELS_CREATE = 5
    LABELS_UPDATE = 5
    LABELS_DELETE = 5

    # Drafts
    DRAFTS_LIST = 5
    DRAFTS_GET = 5
    DRAFTS_CREATE = 10
    DRAFTS_SEND = 100
    DRAFTS_DELETE = 10

    # Profile
    PROFILE_GET = 5

    # Attachments
    ATTACHMENTS_GET = 5


@dataclass
class QuotaUsage:
    """사용자별 할당량 사용 현황."""

    units_used: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    daily_units: int = 0
    daily_reset: datetime = field(default_factory=datetime.now)


class QuotaManager:
    """Gmail API 할당량 관리자.

    Per-user rate limiting (250 units/second)과
    일일 할당량을 추적하고 관리합니다.

    Usage:
        quota = QuotaManager()

        # 실행 전 확인
        if quota.can_execute("user@gmail.com", QuotaUnit.MESSAGES_LIST):
            # API 호출
            result = api.list_messages()
            quota.record_usage("user@gmail.com", QuotaUnit.MESSAGES_LIST)

        # 또는 자동 대기
        quota.wait_for_quota("user@gmail.com", QuotaUnit.MESSAGES_GET)
        result = api.get_message(id)
        quota.record_usage("user@gmail.com", QuotaUnit.MESSAGES_GET)
    """

    # Gmail API limits
    USER_RATE_LIMIT = 250  # units per second
    DAILY_LIMIT = 1_000_000_000  # units per day (workspace)
    CONSUMER_DAILY_LIMIT = 1_000_000  # Conservative estimate for consumer accounts

    def __init__(
        self,
        rate_limit: int = USER_RATE_LIMIT,
        daily_limit: Optional[int] = None,
        is_workspace: bool = True,
    ):
        """
        Args:
            rate_limit: 초당 최대 할당량 (기본값: 250)
            daily_limit: 일일 최대 할당량 (None이면 자동 설정)
            is_workspace: Workspace 계정 여부
        """
        self.rate_limit = rate_limit
        self.daily_limit = (
            daily_limit
            or (self.DAILY_LIMIT if is_workspace else self.CONSUMER_DAILY_LIMIT)
        )
        self._usage: dict[str, QuotaUsage] = {}
        self._lock = threading.Lock()

    def can_execute(self, user: str, units: int) -> bool:
        """API 호출 가능 여부 확인.

        Args:
            user: 사용자 식별자 (이메일 또는 계정명)
            units: 필요한 할당량 단위

        Returns:
            실행 가능하면 True
        """
        with self._lock:
            self._reset_if_needed(user)
            usage = self._get_or_create_usage(user)
            return usage.units_used + units <= self.rate_limit

    def record_usage(self, user: str, units: int) -> None:
        """사용량 기록.

        Args:
            user: 사용자 식별자
            units: 사용한 할당량 단위
        """
        with self._lock:
            self._reset_if_needed(user)
            usage = self._get_or_create_usage(user)
            usage.units_used += units
            usage.daily_units += units

    def wait_for_quota(
        self,
        user: str,
        units: int,
        timeout: float = 30.0,
    ) -> bool:
        """할당량 확보까지 대기.

        Args:
            user: 사용자 식별자
            units: 필요한 할당량 단위
            timeout: 최대 대기 시간 (초)

        Returns:
            할당량 확보 성공 여부

        Raises:
            TimeoutError: 타임아웃 시
        """
        start = time.time()

        while not self.can_execute(user, units):
            if time.time() - start > timeout:
                raise TimeoutError(
                    f"할당량 확보 타임아웃 ({timeout}초). "
                    f"사용자: {user}, 필요 단위: {units}"
                )
            time.sleep(0.1)
            with self._lock:
                self._reset_if_needed(user)

        return True

    def get_usage(self, user: str) -> dict:
        """사용자 할당량 현황 조회.

        Args:
            user: 사용자 식별자

        Returns:
            현재 사용량 정보
        """
        with self._lock:
            self._reset_if_needed(user)
            usage = self._get_or_create_usage(user)
            return {
                "user": user,
                "units_used": usage.units_used,
                "rate_limit": self.rate_limit,
                "rate_available": self.rate_limit - usage.units_used,
                "daily_units": usage.daily_units,
                "daily_limit": self.daily_limit,
                "daily_available": self.daily_limit - usage.daily_units,
            }

    def get_remaining_rate(self, user: str) -> int:
        """현재 초에 남은 rate limit.

        Args:
            user: 사용자 식별자

        Returns:
            남은 할당량 단위 수
        """
        with self._lock:
            self._reset_if_needed(user)
            usage = self._get_or_create_usage(user)
            return max(0, self.rate_limit - usage.units_used)

    def is_daily_limit_reached(self, user: str) -> bool:
        """일일 할당량 도달 여부.

        Args:
            user: 사용자 식별자

        Returns:
            일일 한도 도달 시 True
        """
        with self._lock:
            usage = self._get_or_create_usage(user)
            return usage.daily_units >= self.daily_limit

    def reset_user(self, user: str) -> None:
        """사용자 할당량 리셋 (테스트용).

        Args:
            user: 사용자 식별자
        """
        with self._lock:
            if user in self._usage:
                del self._usage[user]

    def _get_or_create_usage(self, user: str) -> QuotaUsage:
        """사용자 usage 객체 반환 (없으면 생성)."""
        if user not in self._usage:
            self._usage[user] = QuotaUsage()
        return self._usage[user]

    def _reset_if_needed(self, user: str) -> None:
        """초당/일일 리셋 확인 및 수행."""
        if user not in self._usage:
            return

        usage = self._usage[user]
        now = datetime.now()

        # 초당 리셋
        if now - usage.last_reset > timedelta(seconds=1):
            usage.units_used = 0
            usage.last_reset = now

        # 일일 리셋 (자정 기준)
        if now.date() > usage.daily_reset.date():
            usage.daily_units = 0
            usage.daily_reset = now


# 싱글톤 인스턴스
_default_manager: Optional[QuotaManager] = None


def get_quota_manager(
    rate_limit: int = QuotaManager.USER_RATE_LIMIT,
    is_workspace: bool = True,
) -> QuotaManager:
    """기본 QuotaManager 인스턴스 반환.

    Args:
        rate_limit: 초당 최대 할당량
        is_workspace: Workspace 계정 여부

    Returns:
        QuotaManager 싱글톤 인스턴스
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = QuotaManager(
            rate_limit=rate_limit,
            is_workspace=is_workspace,
        )
    return _default_manager


if __name__ == "__main__":
    # 테스트
    manager = QuotaManager()

    user = "test@gmail.com"
    print(f"Initial usage: {manager.get_usage(user)}")

    # 사용량 기록
    manager.record_usage(user, QuotaUnit.MESSAGES_LIST)
    print(f"After list: {manager.get_usage(user)}")

    manager.record_usage(user, QuotaUnit.MESSAGES_GET)
    print(f"After get: {manager.get_usage(user)}")

    # 실행 가능 여부
    print(f"Can execute 250? {manager.can_execute(user, 250)}")
    print(f"Remaining rate: {manager.get_remaining_rate(user)}")

    # 대기 테스트
    print("Waiting for quota...")
    time.sleep(1.1)  # 1초 후 리셋됨
    print(f"After 1s: {manager.get_usage(user)}")
