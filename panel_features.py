"""Condensed research feature examples; no private data or file paths.

Research status and code availability
-------------------------------------
The research is currently under review. The full research code and data
are proprietary and are not distributed here. This file is a simplified
sample of the general workflow, not the complete research implementation
or a replication package.


first_language_use illustrates chronological language-detection logic.
Same-time repositories are pooled to avoid arbitrary row-order attribution.
weekly_activity is a representative consolidation of the activity workflow.
"""
import pandas as pd

from feature_validation import validate_feature_input


def first_language_use(repositories: pd.DataFrame, language_columns: list[str]):
    """Return first-use counts per developer and repository-creation timestamp.

    Requires full available history, not only the estimation window. Language
    columns hold nonnegative usage amounts. Observed first use is a learning proxy.
    """
    validate_feature_input(repositories, ["developer", "created_at"], language_columns)
    data = repositories.copy()
    data["created_at"] = pd.to_datetime(data["created_at"], utc=True)
    if data[["developer", "created_at"] + language_columns].isna().any().any():
        raise ValueError("Missing identity, time, or language measurement")
    used = data[language_columns].gt(0)
    used["developer"] = data["developer"]
    used["created_at"] = data["created_at"]
    history = used.groupby(["developer", "created_at"], sort=True, observed=True).max()
    cumulative = history.groupby(level="developer", observed=True).cumsum()
    first = history & cumulative.eq(1)
    return first.sum(axis=1).rename("new_languages").reset_index()


def weekly_activity(activity: pd.DataFrame):
    """Aggregate already classified counts; callers supply study-aligned weeks.

    Input contains one or more complete activity records per developer/week.
    Missing observation weeks must be reconciled with collection coverage before
    any zero filling; this excerpt does not assume missing records mean inactivity.
    """
    production = ["repositories_created", "commits", "pull_requests"]
    sharing = ["reviews", "issues", "discussions"]
    columns = production + sharing
    validate_feature_input(activity, ["developer", "week"], columns)
    weekly = activity.groupby(["developer", "week"], observed=True)[columns].sum()
    return weekly.assign(
        code_development=weekly[production].sum(axis=1),
        knowledge_sharing=weekly[sharing].sum(axis=1),
    ).reset_index()
