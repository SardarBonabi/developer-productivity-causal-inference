"""Representative manifest guards; research under review, full code/data proprietary.

Private cohort construction and partition sizing remain outside this sample.
"""
from collection_contracts import Job


def checked_partitions(jobs, project: str, snapshot: str, stage: str):
    """Yield scoped jobs once; reject duplicates rather than counting them twice.

    Validation is streaming: earlier jobs may already be committed when a later
    invalid job is encountered. Restart using existing checkpoints after fixing
    the manifest. The key set uses memory proportional to partition count.
    """
    seen = set()
    for job in jobs:
        if not isinstance(job, Job) or (job.project, job.snapshot, job.stage) != (project, snapshot, stage):
            raise ValueError('Manifest scope mismatch')
        if job.key in seen:
            raise ValueError('Duplicate manifest partition')
        seen.add(job.key)
        yield job
