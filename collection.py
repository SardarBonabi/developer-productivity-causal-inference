"""Representative reconstruction of the archive's paginated collection workflow.

Research status and code availability
-------------------------------------
The research is currently under review. The full research code and data
are proprietary and are not distributed here. This file is a simplified
sample of the general workflow, not the complete research implementation
or a replication package.


No live endpoint, credentials, or storage implementation is included. Callbacks
make the acquisition, persistence, and checkpoint responsibilities explicit.
The production pipeline also used parallel collection and SQL/NoSQL storage.
"""
from dataclasses import dataclass
from time import sleep
from typing import Callable, Iterable


@dataclass(frozen=True)
class Page:
    records: list[dict]
    next_cursor: str | None


def collect_partition(
    start_cursor: str,
    fetch_page: Callable[[str], Page],
    persist_records: Callable[[Iterable[dict]], None],
    save_checkpoint: Callable[[str | None], None],
    max_attempts: int = 4,
) -> int:
    """Persist each page before advancing its restart checkpoint.

    fetch_page owns authentication, timeouts, and rate-limit response handling.
    persist_records must be idempotent: a crash between persistence and checkpoint
    may replay a page. Permanent API failures should not be translated to TimeoutError.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    cursor, processed = start_cursor, 0
    while cursor is not None:
        for attempt in range(max_attempts):
            try:
                page = fetch_page(cursor)
                break
            except TimeoutError:
                if attempt + 1 == max_attempts:
                    raise
                sleep(min(2 ** attempt, 30))
        persist_records(page.records)
        save_checkpoint(page.next_cursor)
        processed += len(page.records)
        cursor = page.next_cursor
    return processed
