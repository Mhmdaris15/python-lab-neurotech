"""Mini-batch training with reproducible shuffling and sample-weighted losses."""

import numpy as np

from .parameter import matrix


def train(
    model,
    x,
    target,
    criterion,
    optimizer,
    epochs,
    batch_size,
    *,
    seed=42,
    verbose=False,
):
    x = matrix(x)
    target = matrix(target, "target")
    if len(x) != len(target):
        raise ValueError("Inputs and targets must have the same number of objects.")
    for name, value in [("epochs", epochs), ("batch_size", batch_size)]:
        if (
            not isinstance(value, (int, np.integer))
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError(f"{name} must be a positive integer.")
    rng = np.random.default_rng(seed)
    history = []
    for epoch in range(epochs):
        indices = rng.permutation(len(x))
        total_loss = 0.0
        for start in range(0, len(x), batch_size):
            batch = indices[start : start + batch_size]
            optimizer.zero_grad()
            prediction = model(x[batch])
            loss = criterion(prediction, target[batch])
            model.backward(criterion.backward())
            optimizer.step()
            total_loss += loss * len(batch)
        history.append(total_loss / len(x))
        if verbose:
            print(
                f"Epoch {epoch + 1:02d}/{epochs}: MSE = {history[-1]:.6f}", flush=True
            )
    return history
