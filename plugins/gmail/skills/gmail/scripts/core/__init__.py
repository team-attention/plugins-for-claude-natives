"""Gmail Core Components.

Rate limiting, caching, retry logic, and batch processing for Gmail API.
"""

from .quota_manager import QuotaManager, QuotaUnit
from .retry_handler import exponential_backoff, RetryConfig
from .cache_manager import EmailCache
from .batch_processor import BatchProcessor

__all__ = [
    "QuotaManager",
    "QuotaUnit",
    "exponential_backoff",
    "RetryConfig",
    "EmailCache",
    "BatchProcessor",
]
