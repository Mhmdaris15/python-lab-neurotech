"""Stochastic gradient descent operates on parameters, independently of layers."""

import numpy as np


class SGD:
    def __init__(self, parameters, lr):
        if not np.isfinite(lr) or lr <= 0:
            raise ValueError("Learning rate must be positive and finite.")
        # Identity-based de-duplication prevents stepping an alias twice.
        self.parameters = list({id(p): p for p in parameters}.values())
        self.lr = float(lr)

    def step(self):
        for parameter in self.parameters:
            parameter.value -= self.lr * parameter.grad

    def zero_grad(self):
        for parameter in self.parameters:
            parameter.grad.fill(0)
