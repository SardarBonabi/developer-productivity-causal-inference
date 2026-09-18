"""Selected extraction logic, refactored for readability and separation of concerns.

Research under review; full code/data proprietary. Inputs are semantic fields
from private page/API adapters, not live response bodies. Selectors, requests,
identity mappings and cohort rules are intentionally absent.
"""
from hashlib import sha256
import json
import re

from collection_contracts import Permanent
from collection_transforms import ACTIVITIES, normalize_page


def record_key(*parts: str) -> str:
    """Stable key from already de-identified dimensions, independent of row order.

    Hashing is for deterministic key construction, not a substitute for the
    private identity-protection policy. Never pass raw usernames or credentials.
    """
    return sha256(json.dumps(parts, ensure_ascii=True).encode()).hexdigest()


def parse_display_count(value: str, prefix: str = '') -> int:
    """Parse a selected numeric label after the private adapter identifies it.

    A removal label may use prefix='−'; the stored value is a magnitude. Missing
    elements, unrecognized formats, and arbitrary negative numbers are rejected.
    """
    text = value.strip()
    if prefix and text.startswith(prefix):
        text = text[len(prefix):]
    if not re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)', text):
        raise Permanent('invalid_display_count')
    return int(text.replace(',', ''))


def weekly_record(developer_key: str, week: str, public_counts: dict,
                  private_count: int | None, coverage_complete: bool):
    """Keep public categories and aggregate private activity separate.

    The parser must reconcile summary and detail blocks before calling this
    function, so the same event is not counted in both. No missing category is
    silently treated as zero. No private repository content is requested here.
    """
    row = {'record_key': record_key(developer_key, week),
           'developer_key': developer_key, 'week': week,
           'coverage_complete': coverage_complete, 'private_contributions': private_count}
    for activity in ACTIVITIES:
        row[activity] = public_counts.get(activity)
    normalize_page('weekly_activity', (row,))
    return row


def language_records(repository_key: str, observed_at: str, language_bytes: dict):
    """Expand one repository's language composition to a consistent long format.

    An empty language dictionary yields no language rows; the enclosing page
    checkpoint still records successful collection. It is not a failed request.
    """
    rows = tuple({'record_key': record_key(repository_key, observed_at, language),
                  'repository_key': repository_key, 'observed_at': observed_at,
                  'language': language, 'bytes': byte_count}
                 for language, byte_count in language_bytes.items())
    normalize_page('languages', rows)
    return rows


def participation_records(developer_key: str, week: str, events):
    """Deduplicate event references before aggregating developer-project activity.

    The private parser supplies (event_key, repository_key, activity_type).
    A repeated reference to an event is not another contribution; conflicting
    references are a validation failure. Event-based counts do not replace the
    complete weekly totals where only partial detail is visible.
    """
    seen, counts = {}, {}
    for event_key, repository_key, activity_type in events:
        if not all(isinstance(x, str) and x.strip()
                   for x in (event_key, repository_key, activity_type)):
            raise Permanent('invalid_event_reference')
        pair = (repository_key, activity_type)
        if event_key in seen:
            if seen[event_key] != pair:
                raise Permanent('conflicting_event_reference')
            continue
        seen[event_key] = pair
        counts[pair] = counts.get(pair, 0) + 1
    rows = tuple({'record_key': record_key(developer_key, repository_key, week, activity),
                  'developer_key': developer_key, 'repository_key': repository_key,
                  'week': week, 'activity_type': activity, 'count': count}
                 for (repository_key, activity), count in counts.items())
    normalize_page('participation', rows)
    return rows


def pull_request_record(pull_key: str, repository_key: str, developer_key: str,
                        observed_at: str, status: str, labels: dict):
    """Capture a pull's observed status and structural counts, without its content.

    Status is normalized by the private adapter. 'Closed' is not assumed merged.
    Outcome maturity and point-in-time predictor rules belong to feature assembly.
    """
    try:
        counts = {name: parse_display_count(labels[name], prefix)
                  for name, prefix in (('additions', '+'), ('deletions', '−'),
                                       ('commits', ''), ('changed_files', ''), ('comments', ''))}
    except (KeyError, AttributeError):
        raise Permanent('missing_pull_detail') from None
    row = {'record_key': record_key(pull_key, observed_at), 'pull_key': pull_key,
           'repository_key': repository_key, 'developer_key': developer_key,
           'observed_at': observed_at, 'status': status, **counts}
    normalize_page('pull_requests', (row,))
    return row
