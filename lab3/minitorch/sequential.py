"""Nested sequential composition and explicit, pickle-free persistence."""

import json

import numpy as np

from .layers import Layer, Linear, ReLU
from .parameter import matrix


class Sequential(Layer):
    def __init__(self, *layers):
        if not all(isinstance(layer, Layer) for layer in layers):
            raise TypeError("Sequential accepts Layer objects only.")
        self.layers = list(layers)
        self._output_shape = None

    def forward(self, x):
        x = matrix(x)
        for layer in self.layers:
            x = layer(x)
        self._output_shape = x.shape
        return x

    def backward(self, gradient):
        if self._output_shape is None:
            raise RuntimeError("Call forward before backward.")
        gradient = matrix(gradient, "gradient")
        if gradient.shape != self._output_shape:
            raise ValueError("Gradient shape must match the model output.")
        for layer in reversed(self.layers):
            gradient = layer.backward(gradient)
        return gradient

    def parameters(self):
        return [parameter for layer in self.layers for parameter in layer.parameters()]

    def save(self, path):
        arrays = {}

        def describe(layer):
            if isinstance(layer, Sequential):
                return {
                    "type": "Sequential",
                    "layers": [describe(x) for x in layer.layers],
                }
            if isinstance(layer, Linear):
                key = f"linear_{len(arrays) // 2}"
                arrays[key + "_weight"] = layer.weight.value
                arrays[key + "_bias"] = layer.bias.value
                return {"type": "Linear", "key": key}
            if isinstance(layer, ReLU):
                return {"type": "ReLU"}
            raise ValueError(f"Unsupported layer: {type(layer).__name__}")

        structure = describe(self)
        arrays["metadata"] = np.array(json.dumps({"version": 1, "model": structure}))
        # File handle avoids np.savez silently appending an extension to the chosen path.
        with open(path, "wb") as stream:
            np.savez_compressed(stream, **arrays)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as archive:
            metadata = json.loads(str(archive["metadata"]))
            if metadata["version"] != 1:
                raise ValueError("Unsupported model format version.")

            def restore(node):
                kind = node["type"]
                if kind == "Sequential":
                    return cls(*(restore(child) for child in node["layers"]))
                if kind == "ReLU":
                    return ReLU()
                if kind == "Linear":
                    weight = archive[node["key"] + "_weight"]
                    bias = archive[node["key"] + "_bias"]
                    if weight.ndim != 2 or bias.shape != (weight.shape[1],):
                        raise ValueError("Invalid saved parameter shapes.")
                    layer = Linear(
                        *weight.shape, rng=np.random.default_rng(0), dtype=weight.dtype
                    )
                    layer.weight.value[:] = weight
                    layer.bias.value[:] = bias
                    return layer
                raise ValueError(f"Unknown saved layer type: {kind}")

            model = restore(metadata["model"])
            if not isinstance(model, cls):
                raise ValueError("The root of a saved model must be Sequential.")
            return model
