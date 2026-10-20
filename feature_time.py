"""Representative time normalization; research under review, full code/data proprietary."""
from numbers import Number
import pandas as pd


def utc_creation_times(values: pd.Series) -> pd.Series:
    """Parse explicit dates/times; naive values are interpreted as UTC.

    Numeric epochs require a unit and must be converted upstream. Guessing their
    units can silently place modern records near 1970 and corrupt first-use order.
    """
    if values.isna().any() or values.map(lambda value: isinstance(value, Number)).any():
        raise ValueError("Supply observed dates or timestamps, not numeric epochs")
    result = pd.to_datetime(values, utc=True, format="mixed", errors="raise")
    if result.isna().any():
        raise ValueError("Creation time must not be missing")
    return result
