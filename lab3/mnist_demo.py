"""Train the NumPy library on the official MNIST train/test split.

Run from the repository root: python -m lab3.mnist_demo
scikit-learn is used only to download the data; all model code is local NumPy.
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import fetch_openml
from threadpoolctl import threadpool_limits

try:
    from .minitorch import SGD, Linear, MSELoss, ReLU, Sequential, train
except ImportError:
    from minitorch import SGD, Linear, MSELoss, ReLU, Sequential, train


def predict(model, x, batch_size=512):
    """Bound evaluation memory; this function never updates parameters."""
    return np.concatenate(
        [model(x[i : i + batch_size]) for i in range(0, len(x), batch_size)]
    )


def run(epochs=10, batch_size=128, lr=0.05, seed=42, output=None):
    directory = Path(__file__).resolve().parent
    output = directory / "results" if output is None else Path(output)
    output.mkdir(parents=True, exist_ok=True)
    print(
        "Loading MNIST through fetch_openml (first run downloads and caches it)...",
        flush=True,
    )
    x, labels = fetch_openml(
        "mnist_784",
        version=1,
        as_frame=False,
        return_X_y=True,
        data_home=str(directory / ".cache"),
        parser="liac-arff",
    )
    x = x.astype(np.float32) / 255.0
    labels = labels.astype(int)
    if x.shape != (70000, 784) or labels.shape != (70000,):
        raise ValueError("Expected the complete 70,000-image MNIST dataset.")
    x_train, x_test = x[:60000], x[60000:]
    labels_train, labels_test = labels[:60000], labels[60000:]
    y_train = np.eye(10, dtype=np.float32)[labels_train]
    rng = np.random.default_rng(seed)
    model = Sequential(
        Linear(784, 32, rng=rng, dtype=np.float32),
        ReLU(),
        Linear(32, 10, rng=rng, dtype=np.float32),
    )
    criterion = MSELoss()
    optimizer = SGD(model.parameters(), lr=lr)
    before_accuracy = float(
        np.mean(predict(model, x_test).argmax(axis=1) == labels_test)
    )
    print(f"Test accuracy before training: {before_accuracy:.4%}", flush=True)
    history = train(
        model,
        x_train,
        y_train,
        criterion,
        optimizer,
        epochs,
        batch_size,
        seed=seed,
        verbose=True,
    )
    scores = predict(model, x_test)
    predicted = scores.argmax(axis=1)
    after_accuracy = float(np.mean(predicted == labels_test))
    test_mse = criterion(scores, np.eye(10, dtype=np.float32)[labels_test])
    model.save(output / "model.npz")
    restored = Sequential.load(output / "model.npz")
    restored_scores = predict(restored, x_test)
    np.testing.assert_array_equal(restored_scores, scores)
    confusion = np.zeros((10, 10), dtype=int)
    np.add.at(confusion, (labels_test, predicted), 1)
    per_digit_accuracy = np.diag(confusion) / confusion.sum(axis=1)
    metrics = {
        "dataset": "mnist_784",
        "version": 1,
        "seed": seed,
        "train_samples": len(x_train),
        "test_samples": len(x_test),
        "architecture": [784, 32, 10],
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "parameter_count": sum(p.value.size for p in model.parameters()),
        "accuracy_before": before_accuracy,
        "accuracy_after": after_accuracy,
        "test_mse": test_mse,
        "history": history,
        "per_digit_accuracy": per_digit_accuracy.tolist(),
        "confusion_matrix": confusion.tolist(),
        "restored_predictions_identical": True,
        "restore_max_absolute_difference": float(
            np.max(np.abs(restored_scores - scores))
        ),
    }
    (output / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(1, epochs + 1), history, marker="o")
    ax.set(
        xlabel="Epoch / Эпоха",
        ylabel="Training MSE / Ошибка обучения",
        title="MNIST: sample-weighted batch loss / Ошибка с учётом размера порций",
    )
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output / "training_loss.png", dpi=150)
    plt.close(fig)
    # Fixed first test images: the examples are not selected for correctness.
    fig, axes = plt.subplots(3, 4, figsize=(9, 7))
    for i, ax in enumerate(axes.flat):
        ax.imshow(x_test[i].reshape(28, 28), cmap="gray", vmin=0, vmax=1)
        ax.set_title(
            f"True / Ответ: {labels_test[i]}\nPredicted / Прогноз: {predicted[i]}",
            color="darkgreen" if labels_test[i] == predicted[i] else "darkred",
            fontsize=10,
        )
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(output / "predictions.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 6))
    chart = ax.imshow(confusion, cmap="Blues")
    ax.set(
        xlabel="Predicted digit / Прогноз",
        ylabel="True digit / Ответ",
        title="MNIST test confusion matrix / Матрица ошибок",
        xticks=range(10),
        yticks=range(10),
    )
    fig.colorbar(chart, ax=ax, label="Images / Изображения")
    fig.tight_layout()
    fig.savefig(output / "confusion_matrix.png", dpi=150)
    plt.close(fig)
    print(f"Test accuracy after training: {after_accuracy:.4%}", flush=True)
    print(f"Restored predictions match exactly. Results: {output}", flush=True)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    # Small matrices can be much slower when BLAS starts many worker threads.
    with threadpool_limits(limits=1):
        run(args.epochs, args.batch_size, args.lr, args.seed, args.output)


if __name__ == "__main__":
    main()
