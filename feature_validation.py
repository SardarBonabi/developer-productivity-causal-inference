"""Validation for representative feature samples; research under review.

Full research code and data remain proprietary. These checks are public-sample
safeguards, not the confidential research inclusion rules.
"""
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_complex_dtype


def validate_feature_input(frame: pd.DataFrame, keys: list[str], values: list[str]) -> None:
    """Reject ambiguous schemas and invalid measurements before aggregation.

    Missing keys must not silently disappear in groupby. Missing, infinite or
    negative values are not evidence of inactivity or non-use. Numeric strings
    are deliberately rejected instead of being silently coerced.
    """
    if not frame.columns.is_unique:
        raise ValueError("Input column names must be unique")
    if not values or len(values) != len(set(values)) or set(keys).intersection(values):
        raise ValueError("Measurement columns must be nonempty, unique and separate from keys")
    if not set(keys + values).issubset(frame.columns):
        raise ValueError("Missing required columns")
    if frame[keys + values].isna().any().any():
        raise ValueError("Missing identity, time or measurement")
    for column in values:
        series = frame[column]
        if not is_numeric_dtype(series.dtype) or is_complex_dtype(series.dtype):
            raise ValueError("Measurements must be real numeric values")
        if not np.isfinite(series).all() or series.lt(0).any():
            raise ValueError("Measurements must be finite and nonnegative")
