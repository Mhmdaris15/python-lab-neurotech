"""Trainable arrays and accumulated gradients."""

import numpy as np


class Parameter:
    def __init__(self, value):
        array = np.asarray(value)
        dtype = array.dtype if np.issubdtype(array.dtype, np.floating) else np.float64
        self.value = np.array(array, dtype=dtype, copy=True)
        self.grad = np.zeros_like(self.value)


def matrix(value, name="input"):
    """Validate the batch-by-features convention without silently broadcasting."""
    array = np.asarray(value)
    if array.ndim != 2 or 0 in array.shape:
        raise ValueError(f"{name} must be a nonempty 2-D array; got {array.shape}.")
    if not np.issubdtype(array.dtype, np.number) or not np.isrealobj(array):
        raise ValueError(f"{name} must contain real numbers.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain finite numbers.")
    return array
