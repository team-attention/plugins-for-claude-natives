"""Gmail API Batch Processor.

여러 API 요청을 일괄 처리하여 효율성을 높입니다.

Batch Request Guidelines:
- 최대 50개 요청을 하나의 배치로
- 각 요청은 개별적으로 성공/실패
- Rate limiting은 배치 전체가 아닌 개별 요청에 적용

Reference:
    https://developers.google.com/gmail/api/guides/batch
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from googleapiclient.discovery import Resource
from googleapiclient.http import BatchHttpRequest

from .quota_manager import QuotaManager, QuotaUnit, get_quota_manager
from .retry_handler import exponential_backoff

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """배치 처리 결과."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    results: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)


class BatchProcessor:
    """Gmail API 배치 처리기.

    여러 API 호출을 효율적으로 일괄 처리합니다.

    Usage:
        processor = BatchProcessor(gmail_service)

        # 메시지 일괄 조회
        message_ids = ["msg1", "msg2", "msg3"]
        results = processor.batch_get_messages(message_ids)

        # 라벨 일괄 수정
        modified = processor.batch_modify_labels(
            message_ids,
            add_labels=["STARRED"],
            remove_labels=["UNREAD"]
        )
    """

    MAX_BATCH_SIZE = 50  # Gmail API 최대 배치 크기
    DEFAULT_DELAY = 0.5  # 배치 간 기본 지연 (초)

    def __init__(
        self,
        service: Resource,
        quota_manager: Optional[QuotaManager] = None,
        user: str = "default",
        batch_size: int = MAX_BATCH_SIZE,
        delay_between_batches: float = DEFAULT_DELAY,
    ):
        """
        Args:
            service: Gmail API 서비스 객체
            quota_manager: 할당량 관리자 (없으면 기본 사용)
            user: 사용자 식별자 (할당량 추적용)
            batch_size: 배치당 최대 요청 수
            delay_between_batches: 배치 간 지연 (초)
        """
        self.service = service
        self.quota_manager = quota_manager or get_quota_manager()
        self.user = user
        self.batch_size = min(batch_size, self.MAX_BATCH_SIZE)
        self.delay = delay_between_batches

    # =========================================================================
    # Message Operations
    # =========================================================================

    def batch_get_messages(
        self,
        message_ids: list[str],
        format: str = "metadata",
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> BatchResult:
        """메시지 일괄 조회.

        Args:
            message_ids: 조회할 메시지 ID 목록
            format: 응답 형식 (minimal, full, raw, metadata)
            on_progress: 진행 상황 콜백 (current, total)

        Returns:
            BatchResult 객체
        """
        result = BatchResult(total=len(message_ids))

        for i in range(0, len(message_ids), self.batch_size):
            batch_ids = message_ids[i : i + self.batch_size]
            batch_results = []
            batch_errors = []

            def callback_factory(msg_id: str):
                def callback(request_id, response, exception):
                    if exception:
                        batch_errors.append({
                            "message_id": msg_id,
                            "error": str(exception),
                        })
                    else:
                        batch_results.append(response)

                return callback

            # 배치 요청 생성
            batch = self.service.new_batch_http_request()

            for msg_id in batch_ids:
                batch.add(
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg_id, format=format),
                    callback=callback_factory(msg_id),
                )

            # 할당량 확인 및 대기
            units = len(batch_ids) * QuotaUnit.MESSAGES_GET
            self.quota_manager.wait_for_quota(self.user, units)

            # 배치 실행
            batch.execute()
            self.quota_manager.record_usage(self.user, units)

            # 결과 수집
            result.results.extend(batch_results)
            result.errors.extend(batch_errors)
            result.succeeded += len(batch_results)
            result.failed += len(batch_errors)

            # 진행 상황 콜백
            if on_progress:
                on_progress(min(i + self.batch_size, len(message_ids)), len(message_ids))

            # 다음 배치 전 지연
            if i + self.batch_size < len(message_ids):
                time.sleep(self.delay)

        return result

    def batch_modify_labels(
        self,
        message_ids: list[str],
        add_labels: Optional[list[str]] = None,
        remove_labels: Optional[list[str]] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> BatchResult:
        """라벨 일괄 수정 (batchModify API 사용).

        Args:
            message_ids: 수정할 메시지 ID 목록
            add_labels: 추가할 라벨 ID
            remove_labels: 제거할 라벨 ID
            on_progress: 진행 상황 콜백

        Returns:
            BatchResult 객체
        """
        result = BatchResult(total=len(message_ids))

        for i in range(0, len(message_ids), self.batch_size):
            batch_ids = message_ids[i : i + self.batch_size]

            # 할당량 확인 및 대기
            units = QuotaUnit.MESSAGES_BATCH_MODIFY
            self.quota_manager.wait_for_quota(self.user, units)

            try:
                self.service.users().messages().batchModify(
                    userId="me",
                    body={
                        "ids": batch_ids,
                        "addLabelIds": add_labels or [],
                        "removeLabelIds": remove_labels or [],
                    },
                ).execute()

                self.quota_manager.record_usage(self.user, units)

                # batchModify는 성공 시 빈 응답 반환
                result.succeeded += len(batch_ids)
                result.results.extend([{"id": mid, "status": "modified"} for mid in batch_ids])

            except Exception as e:
                result.failed += len(batch_ids)
                result.errors.append({
                    "message_ids": batch_ids,
                    "error": str(e),
                })
                logger.error(f"Batch modify failed: {e}")

            # 진행 상황 콜백
            if on_progress:
                on_progress(min(i + self.batch_size, len(message_ids)), len(message_ids))

            # 다음 배치 전 지연
            if i + self.batch_size < len(message_ids):
                time.sleep(self.delay)

        return result

    def batch_trash_messages(
        self,
        message_ids: list[str],
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> BatchResult:
        """메시지 일괄 휴지통 이동.

        Args:
            message_ids: 휴지통으로 이동할 메시지 ID 목록
            on_progress: 진행 상황 콜백

        Returns:
            BatchResult 객체
        """
        result = BatchResult(total=len(message_ids))

        for i in range(0, len(message_ids), self.batch_size):
            batch_ids = message_ids[i : i + self.batch_size]
            batch_results = []
            batch_errors = []

            def callback_factory(msg_id: str):
                def callback(request_id, response, exception):
                    if exception:
                        batch_errors.append({
                            "message_id": msg_id,
                            "error": str(exception),
                        })
                    else:
                        batch_results.append({"id": msg_id, "status": "trashed"})

                return callback

            batch = self.service.new_batch_http_request()

            for msg_id in batch_ids:
                batch.add(
                    self.service.users().messages().trash(userId="me", id=msg_id),
                    callback=callback_factory(msg_id),
                )

            units = len(batch_ids) * QuotaUnit.MESSAGES_TRASH
            self.quota_manager.wait_for_quota(self.user, units)

            batch.execute()
            self.quota_manager.record_usage(self.user, units)

            result.results.extend(batch_results)
            result.errors.extend(batch_errors)
            result.succeeded += len(batch_results)
            result.failed += len(batch_errors)

            if on_progress:
                on_progress(min(i + self.batch_size, len(message_ids)), len(message_ids))

            if i + self.batch_size < len(message_ids):
                time.sleep(self.delay)

        return result

    def batch_delete_messages(
        self,
        message_ids: list[str],
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> BatchResult:
        """메시지 일괄 영구 삭제.

        주의: 이 작업은 되돌릴 수 없습니다!

        Args:
            message_ids: 삭제할 메시지 ID 목록
            on_progress: 진행 상황 콜백

        Returns:
            BatchResult 객체
        """
        result = BatchResult(total=len(message_ids))

        for i in range(0, len(message_ids), self.batch_size):
            batch_ids = message_ids[i : i + self.batch_size]
            batch_results = []
            batch_errors = []

            def callback_factory(msg_id: str):
                def callback(request_id, response, exception):
                    if exception:
                        batch_errors.append({
                            "message_id": msg_id,
                            "error": str(exception),
                        })
                    else:
                        batch_results.append({"id": msg_id, "status": "deleted"})

                return callback

            batch = self.service.new_batch_http_request()

            for msg_id in batch_ids:
                batch.add(
                    self.service.users().messages().delete(userId="me", id=msg_id),
                    callback=callback_factory(msg_id),
                )

            units = len(batch_ids) * QuotaUnit.MESSAGES_DELETE
            self.quota_manager.wait_for_quota(self.user, units)

            batch.execute()
            self.quota_manager.record_usage(self.user, units)

            result.results.extend(batch_results)
            result.errors.extend(batch_errors)
            result.succeeded += len(batch_results)
            result.failed += len(batch_errors)

            if on_progress:
                on_progress(min(i + self.batch_size, len(message_ids)), len(message_ids))

            if i + self.batch_size < len(message_ids):
                time.sleep(self.delay)

        return result

    # =========================================================================
    # Thread Operations
    # =========================================================================

    def batch_get_threads(
        self,
        thread_ids: list[str],
        format: str = "metadata",
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> BatchResult:
        """스레드 일괄 조회.

        Args:
            thread_ids: 조회할 스레드 ID 목록
            format: 응답 형식
            on_progress: 진행 상황 콜백

        Returns:
            BatchResult 객체
        """
        result = BatchResult(total=len(thread_ids))

        for i in range(0, len(thread_ids), self.batch_size):
            batch_ids = thread_ids[i : i + self.batch_size]
            batch_results = []
            batch_errors = []

            def callback_factory(thread_id: str):
                def callback(request_id, response, exception):
                    if exception:
                        batch_errors.append({
                            "thread_id": thread_id,
                            "error": str(exception),
                        })
                    else:
                        batch_results.append(response)

                return callback

            batch = self.service.new_batch_http_request()

            for thread_id in batch_ids:
                batch.add(
                    self.service.users()
                    .threads()
                    .get(userId="me", id=thread_id, format=format),
                    callback=callback_factory(thread_id),
                )

            units = len(batch_ids) * QuotaUnit.THREADS_GET
            self.quota_manager.wait_for_quota(self.user, units)

            batch.execute()
            self.quota_manager.record_usage(self.user, units)

            result.results.extend(batch_results)
            result.errors.extend(batch_errors)
            result.succeeded += len(batch_results)
            result.failed += len(batch_errors)

            if on_progress:
                on_progress(min(i + self.batch_size, len(thread_ids)), len(thread_ids))

            if i + self.batch_size < len(thread_ids):
                time.sleep(self.delay)

        return result

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def mark_all_as_read(
        self,
        query: str = "is:unread",
        max_messages: int = 500,
    ) -> BatchResult:
        """조건에 맞는 메시지 전체 읽음 처리.

        Args:
            query: 검색 쿼리 (기본: 읽지 않음)
            max_messages: 최대 처리 메시지 수

        Returns:
            BatchResult 객체
        """
        # 먼저 메시지 ID 목록 조회
        message_ids = []
        page_token = None

        while len(message_ids) < max_messages:
            result = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                    maxResults=min(100, max_messages - len(message_ids)),
                    pageToken=page_token,
                )
                .execute()
            )

            for msg in result.get("messages", []):
                message_ids.append(msg["id"])

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        if not message_ids:
            return BatchResult()

        return self.batch_modify_labels(
            message_ids,
            remove_labels=["UNREAD"],
        )

    def archive_all(
        self,
        query: str = "",
        max_messages: int = 500,
    ) -> BatchResult:
        """조건에 맞는 메시지 전체 보관처리.

        Args:
            query: 검색 쿼리
            max_messages: 최대 처리 메시지 수

        Returns:
            BatchResult 객체
        """
        # INBOX 라벨이 있는 메시지만 조회
        full_query = f"in:inbox {query}".strip()

        message_ids = []
        page_token = None

        while len(message_ids) < max_messages:
            result = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    q=full_query,
                    maxResults=min(100, max_messages - len(message_ids)),
                    pageToken=page_token,
                )
                .execute()
            )

            for msg in result.get("messages", []):
                message_ids.append(msg["id"])

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        if not message_ids:
            return BatchResult()

        return self.batch_modify_labels(
            message_ids,
            remove_labels=["INBOX"],
        )


if __name__ == "__main__":
    # 모듈 테스트 (실제 API 없이)
    print("BatchProcessor module loaded successfully")

    # BatchResult 테스트
    result = BatchResult(total=10, succeeded=8, failed=2)
    result.results = [{"id": f"msg{i}"} for i in range(8)]
    result.errors = [{"message_id": "msg8", "error": "Not found"}, {"message_id": "msg9", "error": "Rate limited"}]

    print(f"Total: {result.total}")
    print(f"Succeeded: {result.succeeded}")
    print(f"Failed: {result.failed}")
    print(f"Success rate: {result.succeeded / result.total * 100:.1f}%")
