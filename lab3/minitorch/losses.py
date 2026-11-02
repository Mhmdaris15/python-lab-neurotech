"""Mean squared error, averaged over both objects and output coordinates."""

import numpy as np

from .parameter import matrix


class MSELoss:
    def __init__(self):
        self._difference = None

    def forward(self, prediction, target):
        prediction = matrix(prediction, "prediction")
        target = matrix(target, "target")
        if prediction.shape != target.shape:
            raise ValueError("Prediction and target shapes must match exactly.")
        self._difference = prediction - target
        return float(np.mean(self._difference**2))

    def __call__(self, prediction, target):
        return self.forward(prediction, target)

    def backward(self):
        if self._difference is None:
            raise RuntimeError("Call loss.forward before loss.backward.")
        return 2 * self._difference / self._difference.size
