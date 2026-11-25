"""Representative retry control; research under review, full code/data proprietary.

Private adapters classify source failures. This module contains no live client,
credentials or endpoint configuration.
"""
from dataclasses import dataclass
from math import isfinite
from numbers import Real
from random import uniform
from time import sleep

from collection_contracts import Permanent, Retryable


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 4
    backoff_cap: float = 30
    max_inline_wait: float = 120

    def __post_init__(self):
        if type(self.attempts) is not int or self.attempts < 1:
            raise ValueError('attempts must be a positive integer')
        for value in (self.backoff_cap, self.max_inline_wait):
            if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value) or value <= 0:
                raise ValueError('Retry wait limits must be finite and positive')


def fetch_with_retry(source, job, cursor, policy, pause=sleep, jitter=uniform):
    """Retry a failed fetch at the same cursor; leave long waits for a later run.

    The private source maps timeouts, temporary server errors and throttling to
    Retryable. Invalid authentication/permissions are Permanent. Its shared rate
    budget must coordinate all workers using the same authorized identity.
    """
    backoff = min(1.0, policy.backoff_cap)
    for attempt in range(policy.attempts):
        try:
            return source.fetch(job, cursor)
        except Retryable as error:
            if attempt + 1 == policy.attempts:
                raise
            server_wait = error.retry_after
            if isinstance(server_wait, bool) or not isinstance(server_wait, Real) or not isfinite(server_wait) or server_wait < 0:
                raise Permanent('invalid_retry_after') from None
            random_wait = jitter(0, backoff)
            if isinstance(random_wait, bool) or not isinstance(random_wait, Real) or not isfinite(random_wait) or not 0 <= random_wait <= backoff:
                raise Permanent('invalid_retry_jitter') from None
            delay = max(server_wait, random_wait)
            if not isfinite(delay) or delay < 0 or delay > policy.max_inline_wait:
                raise  # Never shorten a server-directed cooldown to fit a cap.
            pause(delay)
            backoff = min(policy.backoff_cap, backoff * 2)
    raise AssertionError('Unreachable')

