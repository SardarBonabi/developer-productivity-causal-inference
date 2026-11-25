"""Representative concurrent collection. Full research code/data are proprietary.

Research under review. No live clients, credentials or private job manifests.
"""
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from typing import Callable, ContextManager, Iterable

from collection_contracts import CollectionError, Job, Permanent, Source, Store
from collection_transforms import normalize_page
from collection_retry import RetryPolicy, fetch_with_retry



def collect_partition(job: Job, source: Source, store: Store,
                      policy: RetryPolicy = RetryPolicy()) -> int:
    """Validate and commit pages until explicit completion; return rows committed.

    A worker never marks a failed partition complete. Atomic persistence means
    a retry can restart from the last committed page without skipping records.
    """
    state, written = store.load(job), 0
    seen_cursors = set()
    while not state.complete:
        if state.cursor in seen_cursors:
            raise Permanent('pagination_cycle')
        seen_cursors.add(state.cursor)
        page = fetch_with_retry(source, job, state.cursor, policy)
        if page.complete != (page.next_cursor is None):
            raise Permanent('inconsistent_page_state')
        if not page.complete and page.next_cursor in seen_cursors:
            raise Permanent('pagination_cycle')
        records = normalize_page(job.stage, page.rows)
        state = store.commit_page(job, state, page, records)
        written += len(records)
    return written


@dataclass(frozen=True)
class Outcome:
    job: Job
    status: str
    records_written: int = 0


# Each context owns its client/session and database connection for one job.
WorkerResources = Callable[[Job], ContextManager[tuple[Source, Store]]]


def run_jobs(jobs: Iterable[Job], resources: WorkerResources,
             workers: int = 4) -> Iterable[Outcome]:
    """Bound pending futures to worker count rather than submit a whole cohort.

    Inputs are unique partitions from a private manifest. Outcomes are returned
    to the private scheduler for targeted recovery, never printed with payloads.
    """
    if workers < 1:
        raise ValueError('workers must be positive')

    def worker(job):
        try:
            with resources(job) as (source, store):
                return Outcome(job, 'complete', collect_partition(job, source, store))
        except CollectionError:
            return Outcome(job, 'needs_review')
        except Exception:
            # Suppress exception text: client and DB errors can contain secrets.
            return Outcome(job, 'internal_error')

    iterator = iter(jobs)
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix='collector') as pool:
        pending = set()
        exhausted = False
        while pending or not exhausted:
            while len(pending) < workers and not exhausted:
                try:
                    pending.add(pool.submit(worker, next(iterator)))
                except StopIteration:
                    exhausted = True
            if pending:
                finished, pending = wait(pending, return_when=FIRST_COMPLETED)
                for future in finished:
                    yield future.result()
