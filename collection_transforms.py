"""Allowlisted collection records; representative sample, proprietary research.

Research under review. No raw source payloads, names, contact fields or datasets
are distributed. Private parsers supply normalized fields and stable opaque keys.
"""
from datetime import date

from collection_contracts import Permanent, Record

ACTIVITIES = ('commits', 'repositories_created', 'pull_requests', 'reviews',
              'issues', 'discussions_started', 'discussions_answered')

# Explicit field selection prevents accidental propagation of whole API responses.
FIELDS = {
    'discovery': ('repository_key', 'developer_key'),
    'profiles': ('developer_key', 'cohort', 'account_created_at', 'public_repositories'),
    'weekly_activity': ('developer_key', 'week', 'coverage_complete', *ACTIVITIES,
                        'private_contributions'),
    'repositories': ('repository_key', 'developer_key', 'created_at', 'is_fork', 'stars'),
    'languages': ('repository_key', 'observed_at', 'language', 'bytes'),
    'participation': ('developer_key', 'repository_key', 'week', 'activity_type', 'count'),
    'pull_requests': ('pull_key', 'repository_key', 'developer_key', 'observed_at',
                      'status', 'additions', 'deletions', 'commits', 'changed_files', 'comments'),
}
COUNTS = {*ACTIVITIES, 'private_contributions', 'public_repositories', 'stars',
          'bytes', 'count', 'additions', 'deletions', 'changed_files', 'comments'}
DATES = {'week', 'account_created_at', 'created_at', 'observed_at'}


def normalize_page(stage, rows) -> tuple[Record, ...]:
    """Reject an incomplete page as a unit, leaving its restart position intact.

    Opaque record keys are created privately from stable source IDs and temporal
    grain, never list positions or mutable usernames. Historical snapshots keep
    distinct keys/versions. Unknown source fields are discarded, not persisted.
    """
    if stage not in FIELDS:
        raise Permanent('unknown_stage')
    records, seen = [], set()
    for row in rows:
        key = row.get('record_key')
        if not isinstance(key, str) or not key.strip() or key in seen:
            raise Permanent('invalid_or_duplicate_record_key')
        seen.add(key)
        try:
            values = {field: row[field] for field in FIELDS[stage]}
        except KeyError:
            raise Permanent('missing_required_field') from None
        for field, value in values.items():
            if field in COUNTS:
                if type(value) is not int or value < 0:
                    raise Permanent('invalid_count')
            elif field in DATES:
                try:
                    date.fromisoformat(value)  # Normalized ISO dates, no local timezone assumptions.
                except (TypeError, ValueError):
                    raise Permanent('invalid_date') from None
            elif field in {'coverage_complete', 'is_fork'}:
                if type(value) is not bool:
                    raise Permanent('invalid_boolean')
            elif not isinstance(value, str) or not value.strip():
                raise Permanent('invalid_text')
        if stage == 'weekly_activity' and not values['coverage_complete']:
            raise Permanent('incomplete_week')  # Missing collection is never zero activity.
        if stage == 'participation' and values['activity_type'] not in ACTIVITIES:
            raise Permanent('unknown_activity_type')
        if stage == 'pull_requests' and values['status'] not in {'open', 'closed', 'merged'}:
            raise Permanent('unknown_pull_status')
        records.append(Record(key, values))
    return tuple(records)
