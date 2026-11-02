"""Layers implement their derivatives explicitly using the chain rule."""

from abc import ABC, abstractmethod

import numpy as np

from .parameter import Parameter, matrix


class Layer(ABC):
    @abstractmethod
    def forward(self, x):
        """Transform a two-dimensional batch."""

    @abstractmethod
    def backward(self, gradient):
        """Accumulate parameter gradients and return the input gradient."""

    def __call__(self, x):
        return self.forward(x)

    def parameters(self):
        return []


class Linear(Layer):
    def __init__(self, in_features, out_features, *, rng=None, dtype=np.float64):
        for size in (in_features, out_features):
            if (
                not isinstance(size, (int, np.integer))
                or isinstance(size, bool)
                or size <= 0
            ):
                raise ValueError("Feature counts must be positive integers.")
        if not np.issubdtype(np.dtype(dtype), np.floating):
            raise ValueError("Parameter dtype must be floating point.")
        rng = np.random.default_rng() if rng is None else rng
        self.in_features = int(in_features)
        self.out_features = int(out_features)
        # Small random values for BOTH trainable arrays, as required by the assignment.
        scale = min(0.1, (2.0 / in_features) ** 0.5)
        self.weight = Parameter(
            rng.normal(0, scale, (in_features, out_features)).astype(dtype)
        )
        self.bias = Parameter(rng.normal(0, 0.01, out_features).astype(dtype))
        self._input = None

    def forward(self, x):
        x = matrix(x)
        if x.shape[1] != self.in_features:
            raise ValueError(f"Expected {self.in_features} features, got {x.shape[1]}.")
        self._input = x.copy()
        return x @ self.weight.value + self.bias.value

    def backward(self, gradient):
        if self._input is None:
            raise RuntimeError("Call forward before backward.")
        gradient = matrix(gradient, "gradient")
        if gradient.shape != (len(self._input), self.out_features):
            raise ValueError("Gradient shape must match the layer output.")
        self.weight.grad += self._input.T @ gradient
        self.bias.grad += gradient.sum(axis=0)
        return gradient @ self.weight.value.T

    def parameters(self):
        return [self.weight, self.bias]


class ReLU(Layer):
    def __init__(self):
        self._positive = None

    def forward(self, x):
        x = matrix(x)
        self._positive = x > 0
        return np.maximum(0, x)

    def backward(self, gradient):
        if self._positive is None:
            raise RuntimeError("Call forward before backward.")
        gradient = matrix(gradient, "gradient")
        if gradient.shape != self._positive.shape:
            raise ValueError("Gradient shape must match the ReLU output.")
        return gradient * self._positive
