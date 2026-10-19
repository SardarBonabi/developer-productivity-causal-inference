"""Representative embedding preparation; research under review.

Full research code and data remain proprietary. This public helper illustrates
numerical safeguards for cosine clustering, not the original model settings.
"""
import numpy as np


def normalize_embeddings(embeddings) -> np.ndarray:
    """Return finite unit-length rows without mutating the input.

    Scale each row before taking its norm to avoid overflow or underflow from
    squaring extreme values. Zero vectors have undefined cosine distance and
    must be resolved upstream rather than hidden behind an epsilon denominator.
    """
    values = np.asarray(embeddings)
    if values.ndim != 2 or 0 in values.shape:
        raise ValueError("Expected a nonempty two-dimensional embedding matrix")
    if values.dtype.kind not in "iuf":
        raise ValueError("Embeddings must contain real numeric values")
    with np.errstate(over="ignore", invalid="ignore"):
        values = values.astype(np.float64, copy=True)
    if not np.isfinite(values).all():
        raise ValueError("Embeddings must be finite and representable as float64")
    scale = np.max(np.abs(values), axis=1, keepdims=True)
    if (scale == 0).any():
        raise ValueError("Zero embeddings cannot be used for cosine clustering")
    scaled = values / scale
    return scaled / np.linalg.norm(scaled, axis=1, keepdims=True)
