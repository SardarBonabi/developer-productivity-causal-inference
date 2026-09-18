"""Study-specific collection orchestration; representative workflow sample.

Research under review. Full research code and data remain proprietary. Private
source adapters, selection rules and execution configuration are not distributed.
"""
from typing import Iterable, Protocol

from collection_contracts import Job
from collection_runtime import WorkerResources, run_jobs

PROJECT = 'developer-productivity-causal-inference'
STAGES = ('discovery', 'profiles', 'weekly_activity', 'repositories', 'languages')


class Manifest(Protocol):
    def partitions(self, project: str, snapshot: str, stage: str) -> Iterable[Job]:
        """Resolve unique, non-overlapping jobs from committed upstream records.

        Implemented privately: discovery pagination, profile/country eligibility,
        immutable date windows, entity resolution, deduplicated references and
        partition sizing. A snapshot binds both the inputs and parser version.
        """
        ...


def collect_study(manifest: Manifest, resources: WorkerResources,
                  snapshot: str, workers: int = 4):
    """Run ordered stages; block downstream work if any partition is incomplete.

    Re-running the same manifest skips completed jobs and resumes interrupted
    ones. A fresh snapshot is required when inputs or extraction rules change.
    """
    summary = {}
    for stage in STAGES:
        completed = failed = written = total = 0

        def checked_jobs():
            for job in manifest.partitions(PROJECT, snapshot, stage):
                if (job.project, job.snapshot, job.stage) != (PROJECT, snapshot, stage):
                    raise ValueError('Manifest scope mismatch')
                yield job

        for outcome in run_jobs(checked_jobs(), resources, workers=workers):
            total += 1
            completed += outcome.status == 'complete'
            failed += outcome.status != 'complete'
            written += outcome.records_written
        summary[stage] = {'complete_partitions': completed, 'failed_partitions': failed,
                          'records_written_this_run': written}
        if failed or total == 0:
            # Empty manifests need explicit review; do not silently certify coverage.
            return {'status': 'incomplete', 'stages': summary}
    return {'status': 'complete', 'stages': summary}
