"""Gmail Local Cache Manager.

API 호출을 최소화하기 위한 로컬 캐시 레이어.

캐시 전략:
- 메시지 내용: 24시간 유효 (메시지는 불변)
- 메시지 메타데이터: 1시간 유효 (라벨 변경 가능)
- 메시지 목록: 5분 유효 (자주 변경됨)
- 라벨 목록: 1시간 유효

캐시 무효화:
- 메시지 수정 시 해당 메시지 캐시 무효화
- 발송 시 목록 캐시 무효화
- 라벨 변경 시 라벨 캐시 무효화

Reference:
    https://community.latenode.com/t/understanding-gmail-api-quota-restrictions-and-rate-limits/28113
"""

import hashlib
import json
import os
import shutil
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


@dataclass
class CacheConfig:
    """캐시 설정."""

    # TTL (Time-To-Live) 설정 (시간 단위)
    message_ttl_hours: int = 24  # 메시지 본문
    metadata_ttl_hours: int = 1  # 메타데이터
    list_ttl_minutes: int = 5  # 목록
    labels_ttl_hours: int = 1  # 라벨

    # 캐시 크기 제한
    max_messages_per_account: int = 1000
    max_cache_size_mb: int = 100


class EmailCache:
    """Gmail 이메일 로컬 캐시 관리자.

    API 호출을 줄이기 위해 메시지, 목록, 라벨을 로컬에 캐싱합니다.

    Usage:
        cache = EmailCache()

        # 메시지 캐싱
        cached = cache.get_message("work", "msg123")
        if cached is None:
            message = api.get_message("msg123")
            cache.set_message("work", "msg123", message)
        else:
            message = cached

        # 목록 캐싱
        query = "is:unread"
        cached_list = cache.get_list("work", query)
        if cached_list is None:
            messages = api.list_messages(query)
            cache.set_list("work", query, messages)
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        config: Optional[CacheConfig] = None,
    ):
        """
        Args:
            cache_dir: 캐시 디렉토리 (기본값: .cache/gmail)
            config: 캐시 설정
        """
        self.config = config or CacheConfig()

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        elif os.environ.get("GMAIL_CACHE_DIR"):
            self.cache_dir = Path(os.environ["GMAIL_CACHE_DIR"])
        else:
            self.cache_dir = Path(__file__).parent.parent.parent / ".cache" / "gmail"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    # =========================================================================
    # Message Cache
    # =========================================================================

    def get_message(
        self,
        account: str,
        message_id: str,
        metadata_only: bool = False,
    ) -> Optional[dict]:
        """캐시된 메시지 조회.

        Args:
            account: 계정 이름
            message_id: 메시지 ID
            metadata_only: 메타데이터만 조회 시 True

        Returns:
            캐시된 메시지 또는 None
        """
        cache_file = self._message_path(account, message_id)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                data = json.load(f)

            ttl_hours = (
                self.config.metadata_ttl_hours
                if metadata_only
                else self.config.message_ttl_hours
            )

            if self._is_fresh(data.get("cached_at"), ttl_hours):
                return data.get("message")

            # 만료된 캐시 삭제
            cache_file.unlink(missing_ok=True)
            return None
        except (json.JSONDecodeError, KeyError):
            cache_file.unlink(missing_ok=True)
            return None

    def set_message(
        self,
        account: str,
        message_id: str,
        message: dict,
    ) -> None:
        """메시지 캐시.

        Args:
            account: 계정 이름
            message_id: 메시지 ID
            message: 메시지 데이터
        """
        with self._lock:
            account_dir = self.cache_dir / account / "messages"
            account_dir.mkdir(parents=True, exist_ok=True)

            cache_file = self._message_path(account, message_id)
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "message": message,
            }

            with open(cache_file, "w") as f:
                json.dump(cache_data, f, ensure_ascii=False)

            # 캐시 크기 정리
            self._cleanup_if_needed(account)

    # =========================================================================
    # List Cache
    # =========================================================================

    def get_list(
        self,
        account: str,
        query: str,
        label_ids: Optional[list[str]] = None,
    ) -> Optional[list[dict]]:
        """캐시된 목록 조회.

        Args:
            account: 계정 이름
            query: 검색 쿼리
            label_ids: 라벨 필터

        Returns:
            캐시된 메시지 ID 목록 또는 None
        """
        cache_key = self._list_cache_key(query, label_ids)
        cache_file = self._list_path(account, cache_key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                data = json.load(f)

            ttl_minutes = self.config.list_ttl_minutes
            if self._is_fresh(data.get("cached_at"), ttl_minutes / 60):
                return data.get("messages")

            cache_file.unlink(missing_ok=True)
            return None
        except (json.JSONDecodeError, KeyError):
            cache_file.unlink(missing_ok=True)
            return None

    def set_list(
        self,
        account: str,
        query: str,
        messages: list[dict],
        label_ids: Optional[list[str]] = None,
    ) -> None:
        """목록 캐시.

        Args:
            account: 계정 이름
            query: 검색 쿼리
            messages: 메시지 목록
            label_ids: 라벨 필터
        """
        with self._lock:
            list_dir = self.cache_dir / account / "lists"
            list_dir.mkdir(parents=True, exist_ok=True)

            cache_key = self._list_cache_key(query, label_ids)
            cache_file = self._list_path(account, cache_key)

            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "query": query,
                "label_ids": label_ids,
                "messages": messages,
            }

            with open(cache_file, "w") as f:
                json.dump(cache_data, f, ensure_ascii=False)

    # =========================================================================
    # Labels Cache
    # =========================================================================

    def get_labels(self, account: str) -> Optional[list[dict]]:
        """캐시된 라벨 목록 조회.

        Args:
            account: 계정 이름

        Returns:
            캐시된 라벨 목록 또는 None
        """
        cache_file = self.cache_dir / account / "labels.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                data = json.load(f)

            if self._is_fresh(data.get("cached_at"), self.config.labels_ttl_hours):
                return data.get("labels")

            cache_file.unlink(missing_ok=True)
            return None
        except (json.JSONDecodeError, KeyError):
            cache_file.unlink(missing_ok=True)
            return None

    def set_labels(self, account: str, labels: list[dict]) -> None:
        """라벨 캐시.

        Args:
            account: 계정 이름
            labels: 라벨 목록
        """
        with self._lock:
            account_dir = self.cache_dir / account
            account_dir.mkdir(parents=True, exist_ok=True)

            cache_file = account_dir / "labels.json"
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "labels": labels,
            }

            with open(cache_file, "w") as f:
                json.dump(cache_data, f, ensure_ascii=False)

    # =========================================================================
    # Cache Invalidation
    # =========================================================================

    def invalidate_message(self, account: str, message_id: str) -> None:
        """메시지 캐시 무효화.

        Args:
            account: 계정 이름
            message_id: 메시지 ID
        """
        with self._lock:
            cache_file = self._message_path(account, message_id)
            cache_file.unlink(missing_ok=True)

    def invalidate_lists(self, account: str) -> None:
        """목록 캐시 전체 무효화.

        Args:
            account: 계정 이름
        """
        with self._lock:
            list_dir = self.cache_dir / account / "lists"
            if list_dir.exists():
                shutil.rmtree(list_dir, ignore_errors=True)

    def invalidate_labels(self, account: str) -> None:
        """라벨 캐시 무효화.

        Args:
            account: 계정 이름
        """
        with self._lock:
            cache_file = self.cache_dir / account / "labels.json"
            cache_file.unlink(missing_ok=True)

    def invalidate_account(self, account: str) -> None:
        """계정의 모든 캐시 무효화.

        Args:
            account: 계정 이름
        """
        with self._lock:
            account_dir = self.cache_dir / account
            if account_dir.exists():
                shutil.rmtree(account_dir, ignore_errors=True)

    def invalidate_all(self) -> None:
        """전체 캐시 무효화."""
        with self._lock:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir, ignore_errors=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Cache Statistics
    # =========================================================================

    def get_stats(self, account: Optional[str] = None) -> dict:
        """캐시 통계 조회.

        Args:
            account: 특정 계정만 조회 시 지정

        Returns:
            캐시 통계 정보
        """
        stats = {
            "cache_dir": str(self.cache_dir),
            "accounts": {},
            "total_size_bytes": 0,
            "total_messages": 0,
        }

        accounts = [account] if account else self._get_cached_accounts()

        for acc in accounts:
            acc_dir = self.cache_dir / acc
            if not acc_dir.exists():
                continue

            msg_dir = acc_dir / "messages"
            list_dir = acc_dir / "lists"

            msg_count = len(list(msg_dir.glob("*.json"))) if msg_dir.exists() else 0
            list_count = len(list(list_dir.glob("*.json"))) if list_dir.exists() else 0

            # 계정 디렉토리 크기 계산
            size = sum(
                f.stat().st_size
                for f in acc_dir.rglob("*")
                if f.is_file()
            )

            stats["accounts"][acc] = {
                "messages_cached": msg_count,
                "lists_cached": list_count,
                "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 2),
            }

            stats["total_size_bytes"] += size
            stats["total_messages"] += msg_count

        stats["total_size_mb"] = round(
            stats["total_size_bytes"] / (1024 * 1024), 2
        )

        return stats

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _message_path(self, account: str, message_id: str) -> Path:
        """메시지 캐시 파일 경로."""
        return self.cache_dir / account / "messages" / f"{message_id}.json"

    def _list_path(self, account: str, cache_key: str) -> Path:
        """목록 캐시 파일 경로."""
        return self.cache_dir / account / "lists" / f"{cache_key}.json"

    def _list_cache_key(
        self,
        query: str,
        label_ids: Optional[list[str]] = None,
    ) -> str:
        """목록 캐시 키 생성."""
        key_data = {"query": query, "labels": sorted(label_ids or [])}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()[:16]

    def _is_fresh(
        self,
        cached_at: Optional[str],
        max_age_hours: float,
    ) -> bool:
        """캐시 신선도 확인."""
        if not cached_at:
            return False

        try:
            cache_time = datetime.fromisoformat(cached_at)
            return datetime.now() - cache_time < timedelta(hours=max_age_hours)
        except ValueError:
            return False

    def _get_cached_accounts(self) -> list[str]:
        """캐시된 계정 목록."""
        if not self.cache_dir.exists():
            return []

        return [
            d.name
            for d in self.cache_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    def _cleanup_if_needed(self, account: str) -> None:
        """캐시 크기 제한 적용."""
        msg_dir = self.cache_dir / account / "messages"
        if not msg_dir.exists():
            return

        cache_files = sorted(
            msg_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
        )

        # 메시지 수 제한
        if len(cache_files) > self.config.max_messages_per_account:
            to_delete = len(cache_files) - self.config.max_messages_per_account
            for f in cache_files[:to_delete]:
                f.unlink(missing_ok=True)


# 싱글톤 인스턴스
_default_cache: Optional[EmailCache] = None


def get_cache(cache_dir: Optional[str] = None) -> EmailCache:
    """기본 캐시 인스턴스 반환.

    Args:
        cache_dir: 캐시 디렉토리

    Returns:
        EmailCache 싱글톤 인스턴스
    """
    global _default_cache
    if _default_cache is None:
        _default_cache = EmailCache(cache_dir)
    return _default_cache


if __name__ == "__main__":
    # 테스트
    import tempfile

    # 임시 디렉토리에서 테스트
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = EmailCache(cache_dir=tmpdir)

        # 메시지 캐싱 테스트
        test_message = {
            "id": "msg123",
            "subject": "Test Subject",
            "from": "test@example.com",
            "body": "Test body content",
        }

        cache.set_message("work", "msg123", test_message)
        cached = cache.get_message("work", "msg123")
        print(f"Cached message: {cached['subject']}")

        # 목록 캐싱 테스트
        test_list = [
            {"id": "msg1", "threadId": "thread1"},
            {"id": "msg2", "threadId": "thread2"},
        ]

        cache.set_list("work", "is:unread", test_list)
        cached_list = cache.get_list("work", "is:unread")
        print(f"Cached list: {len(cached_list)} messages")

        # 라벨 캐싱 테스트
        test_labels = [
            {"id": "INBOX", "name": "INBOX"},
            {"id": "SENT", "name": "SENT"},
        ]

        cache.set_labels("work", test_labels)
        cached_labels = cache.get_labels("work")
        print(f"Cached labels: {len(cached_labels)} labels")

        # 통계
        stats = cache.get_stats()
        print(f"\nCache stats: {json.dumps(stats, indent=2)}")

        # 무효화 테스트
        cache.invalidate_message("work", "msg123")
        cached = cache.get_message("work", "msg123")
        print(f"After invalidation: {cached}")
