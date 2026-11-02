"""Behavioral and numerical checks for the educational neural-network library."""

import numpy as np
import pytest


def api():
    # Import inside tests so an absent implementation is an explicit red phase.
    from lab3 import minitorch

    return minitorch


def test_linear_forward_and_nested_parameter_identity():
    nn = api()
    layer = nn.Linear(2, 1, rng=np.random.default_rng(1))
    layer.weight.value[:] = [[2], [3]]
    layer.bias.value[:] = [1]
    np.testing.assert_allclose(layer([[1, 2], [-1, 3]]), [[9], [8]])
    model = nn.Sequential(nn.Sequential(layer, nn.ReLU()), nn.Linear(1, 2))
    assert model.parameters()[0] is layer.weight
    assert model.parameters()[1] is layer.bias
    assert len(model.parameters()) == 4
    assert nn.ReLU().parameters() == []
    assert np.any(layer.bias.value != 0)


def test_gradients_match_finite_differences_and_accumulate():
    nn = api()
    rng = np.random.default_rng(42)
    model = nn.Sequential(nn.Linear(2, 3, rng=rng), nn.ReLU(), nn.Linear(3, 2, rng=rng))
    x = np.array([[0.7, -0.3], [1.2, 0.8]])
    target = np.array([[0.3, -0.5], [0.8, 0.2]])
    criterion = nn.MSELoss()
    criterion(model(x), target)
    dx = model.backward(criterion.backward())
    gradients = [p.grad.copy() for p in model.parameters()]
    eps = 1e-6
    for parameter, analytical in zip(model.parameters(), gradients):
        numerical = np.zeros_like(parameter.value)
        for index in np.ndindex(parameter.value.shape):
            old = parameter.value[index]
            parameter.value[index] = old + eps
            plus = criterion(model(x), target)
            parameter.value[index] = old - eps
            minus = criterion(model(x), target)
            parameter.value[index] = old
            numerical[index] = (plus - minus) / (2 * eps)
        np.testing.assert_allclose(analytical, numerical, atol=1e-7, rtol=1e-5)
    numerical_dx = np.zeros_like(x)
    for index in np.ndindex(x.shape):
        old = x[index]
        x[index] = old + eps
        plus = criterion(model(x), target)
        x[index] = old - eps
        minus = criterion(model(x), target)
        x[index] = old
        numerical_dx[index] = (plus - minus) / (2 * eps)
    np.testing.assert_allclose(dx, numerical_dx, atol=1e-7)
    criterion(model(x), target)
    model.backward(criterion.backward())
    for parameter, gradient in zip(model.parameters(), gradients):
        np.testing.assert_allclose(parameter.grad, 2 * gradient)
    optimizer = nn.SGD(model.parameters(), lr=0.05)
    before = [p.value.copy() for p in model.parameters()]
    optimizer.step()
    for p, old, grad in zip(model.parameters(), before, gradients):
        np.testing.assert_allclose(p.value, old - 0.1 * grad)
    optimizer.zero_grad()
    assert all(np.all(p.grad == 0) for p in model.parameters())


def test_relu_and_mse_known_values():
    nn = api()
    relu = nn.ReLU()
    np.testing.assert_array_equal(relu([[-1, 0, 2]]), [[0, 0, 2]])
    np.testing.assert_array_equal(relu.backward([[3, 4, 5]]), [[0, 0, 5]])
    loss = nn.MSELoss()
    assert loss([[1, 2], [3, 4]], [[0, 0], [0, 0]]) == 7.5
    np.testing.assert_allclose(loss.backward(), [[0.5, 1], [1.5, 2]])


def test_invalid_shapes_and_backward_order():
    nn = api()
    with pytest.raises(TypeError):
        nn.Layer()
    for layer in [nn.Linear(2, 1), nn.ReLU(), nn.Sequential(nn.Linear(2, 1))]:
        with pytest.raises(RuntimeError):
            layer.backward(np.ones((2, 1)))
    with pytest.raises(RuntimeError):
        nn.MSELoss().backward()
    for x in [np.ones(2), np.ones((2, 3)), np.ones((0, 2))]:
        with pytest.raises(ValueError):
            nn.Linear(2, 1)(x)
    loss = nn.MSELoss()
    with pytest.raises(ValueError):
        loss(np.ones((2, 1)), np.ones((2, 2)))
    for lr in [0, -1, np.nan, np.inf]:
        with pytest.raises(ValueError):
            nn.SGD([], lr=lr)
    layer = nn.Linear(2, 1)
    layer(np.ones((2, 2)))
    with pytest.raises(ValueError):
        layer.backward(np.ones((2, 2)))


def test_nested_serialization_preserves_predictions(tmp_path):
    nn = api()
    model = nn.Sequential(nn.Sequential(nn.Linear(2, 4), nn.ReLU()), nn.Linear(4, 1))
    x = np.array([[1.0, 2.0], [-3.0, 1.0]])
    expected = model(x)
    path = tmp_path / "model.npz"
    model.save(path)
    restored = nn.Sequential.load(path)
    assert isinstance(restored.layers[0], nn.Sequential)
    np.testing.assert_array_equal(restored(x), expected)
    assert all(np.all(p.grad == 0) for p in restored.parameters())


def test_training_learns_and_keeps_short_last_batch():
    nn = api()
    x = np.arange(5, dtype=float).reshape(-1, 1) / 4
    y = 2 * x + 1
    model = nn.Sequential(nn.Linear(1, 1, rng=np.random.default_rng(0)))
    loss = nn.MSELoss()
    initial = loss(model(x), y)
    history = nn.train(model, x, y, loss, nn.SGD(model.parameters(), 0.1), 100, 2)
    assert len(history) == 100
    assert loss(model(x), y) < initial / 100
    # An identity model has no updates: uneven batches must reproduce full-data MSE.
    identity = nn.Sequential()
    expected = float(np.mean((x - y) ** 2))
    history = nn.train(identity, x, y, loss, nn.SGD([], 0.1), 1, 2)
    assert history == pytest.approx([expected])
    for epochs, batch_size in [(0, 2), (1, 0)]:
        with pytest.raises(ValueError):
            nn.train(model, x, y, loss, nn.SGD([], 0.1), epochs, batch_size)
