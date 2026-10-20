"""Representative activity aggregation; research under review, full code/data proprietary."""
import numpy as np


def checked_weekly_totals(activity, keys, columns):
    """Aggregate validated counts in float64, rejecting unrepresentable totals.

    Float arithmetic avoids fixed-width integer wraparound. Counts above 2**53
    may be approximate. Missing/negative source counts must be rejected upstream.
    """
    numeric = activity.copy()
    numeric[columns] = numeric[columns].astype("float64")
    with np.errstate(over="ignore", invalid="ignore"):
        totals = numeric.groupby(keys, observed=True)[columns].sum()
    ensure_finite_totals(totals)
    return totals


def ensure_finite_totals(frame):
    if not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError("Activity totals exceed the supported numeric range")
