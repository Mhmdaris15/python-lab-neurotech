# Lab 3 code explanation / Объяснение кода ЛР3

## 1. Start with the notebook / Начните с блокнота

**EN:** [tutorial.ipynb](tutorial.ipynb) contains the full implementation in executable code cells and a structured explanation in English and Russian. Its `%%writefile` cells save the displayed implementation into `minitorch/*.py`, satisfying the requirement for separate modules. They overwrite these module files. After editing implementation cells, restart the kernel and run all cells to avoid stale imported classes.

**RU:** [tutorial.ipynb](tutorial.ipynb) содержит полную реализацию в исполняемых ячейках и последовательное объяснение на английском и русском. Ячейки `%%writefile` сохраняют показанную реализацию в `minitorch/*.py`, выполняя требование разделения на модули. Они перезаписывают эти файлы. После изменения реализации перезапустите ядро и выполните все ячейки, чтобы не использовать старые импортированные классы.

From the repository root / Из корня репозитория:

```powershell
.venv\Scripts\python -m pip install -r lab2\requirements.txt -r lab3\requirements.txt
.venv\Scripts\python -m jupyterlab
```

**EN:** Open `lab3/tutorial.ipynb`; select **Kernel → Restart Kernel and Run All Cells**. The first MNIST run needs internet; subsequent runs use `lab3/.cache/`. A separate script offers the same training experiment: `.venv\Scripts\python -m lab3.mnist_demo`. Results are written to `lab3/results/`.

**RU:** Откройте `lab3/tutorial.ipynb` и выберите **Kernel → Restart Kernel and Run All Cells**. Для первого скачивания MNIST нужен интернет; затем используется `lab3/.cache/`. Отдельный скрипт запускает тот же эксперимент: `.venv\Scripts\python -m lab3.mnist_demo`. Результаты сохраняются в `lab3/results/`.

## 2. Notebook map / Структура блокнота

| Section / Раздел | English | Русский |
| --- | --- | --- |
| 1 | Shapes, class responsibilities and initial UML. | Формы массивов, ответственность классов и первоначальная UML. |
| 2 | Parameter arrays and input validation. | Массивы параметров и проверка входа. |
| 3 | Abstract layer, Linear, ReLU and derivatives. | Абстрактный слой, Linear, ReLU и производные. |
| 4 | Nested Sequential and serialization. | Вложенный Sequential и сохранение. |
| 5–7 | MSE, SGD and the training loop. | MSE, SGD и цикл обучения. |
| 8–9 | Worked example and numerical gradient checks. | Пример с ручной проверкой и численные градиенты. |
| 10–12 | MNIST preparation, baseline and training. | Подготовка MNIST, исходная точность и обучение. |
| 13–14 | Test metrics, predictions and save/load equality. | Тестовые метрики, прогнозы и равенство после загрузки. |
| 15–16 | Final UML, defense checklist and limitations. | Итоговая UML, подготовка к защите и ограничения. |

## 3. Module responsibilities / Ответственность модулей

| File | English | Русский |
| --- | --- | --- |
| `parameter.py` | `Parameter` stores values and gradients; `matrix` validates data. | `Parameter` хранит значения и градиенты, `matrix` проверяет данные. |
| `layers.py` | Abstract `Layer`, affine `Linear`, nonlinear `ReLU`. | Абстрактный `Layer`, аффинный `Linear`, нелинейный `ReLU`. |
| `sequential.py` | Composition, recursive parameters, architecture and array persistence. | Композиция, рекурсивные параметры, сохранение структуры и массивов. |
| `losses.py` | Scalar MSE and its prediction derivative. | Скалярная MSE и производная по предсказаниям. |
| `optim.py` | SGD update and zeroing accumulated gradients. | Обновление SGD и обнуление накопленных градиентов. |
| `training.py` | Shuffling, mini-batches and weighted epoch history. | Перемешивание, порции и взвешенная история ошибки эпох. |
| `__init__.py` | Exports the public API. | Экспортирует интерфейс библиотеки. |

## 4. Parameter and Layer / Параметр и слой

**EN:** A `Parameter` represents an entire array, not one scalar. `value` is a private copy of the supplied numbers; floating dtypes are retained and integer input is converted to float64. `grad = np.zeros_like(value)` has exactly the same shape and dtype. Returning these same objects from `parameters()` lets an optimizer modify the state used by the model.

**RU:** `Parameter` представляет целый массив, а не одно число. `value` — отдельная копия переданных значений; вещественный тип сохраняется, целые числа преобразуются в float64. `grad = np.zeros_like(value)` имеет ту же форму и тип. Возврат тех же объектов из `parameters()` позволяет оптимизатору изменять состояние, которое использует модель.

**EN:** `Layer` is abstract because `forward` and `backward` define obligations for subclasses. `__call__(x)` forwards to `forward(x)`. `parameters()` defaults to an empty list. NumPy is the only numerical dependency of this package; no PyTorch or automatic differentiation is involved.

**RU:** `Layer` абстрактный: методы `forward` и `backward` задают обязательства наследников. `__call__(x)` вызывает `forward(x)`. По умолчанию `parameters()` возвращает пустой список. Единственная вычислительная зависимость этого пакета — NumPy; PyTorch и автоматическое дифференцирование не используются.

## 5. Linear: shapes and chain rule / Linear: формы и цепное правило

| Array / Массив | Shape / Форма |
| --- | --- |
| Input `X` / Вход | `(n, in_features)` |
| Weights `W` / Веса | `(in_features, out_features)` |
| Bias `b` / Смещение | `(out_features,)` |
| Output `Y`, incoming gradient `G` / Выход, входящий градиент | `(n, out_features)` |
| Input gradient / Градиент входа | `(n, in_features)` |

```python
Y = X @ W + b
weight.grad += X.T @ G
bias.grad += G.sum(axis=0)
input_gradient = G @ W.T
```

**EN:** Matrix multiplication combines features with the corresponding weights. Bias broadcasts across all rows. Backward requires the saved input from the latest forward pass. `X.T @ G` collects every object's contribution to every weight; summing over rows collects bias contributions. `G @ W.T` expresses how the loss changes with the input, allowing the previous layer to continue backpropagation.

**RU:** Матричное умножение объединяет признаки с соответствующими весами. Смещение распространяется по всем строкам. Для обратного прохода нужен сохранённый вход последнего прямого прохода. `X.T @ G` собирает вклады объектов в каждый вес; сумма по строкам собирает вклады в смещение. `G @ W.T` выражает изменение ошибки по входу и позволяет продолжить обратное распространение через предыдущий слой.

**EN:** Both weights and bias start as small random numbers near zero. Weights use standard deviation `min(0.1, sqrt(2/in_features))`, biases use `0.01`. The constructor accepts an optional RNG and dtype. Passing one seeded RNG to all model layers makes initialization reproducible without giving every layer identical initial random streams.

**RU:** Веса и смещение начинаются с малых случайных чисел около нуля. Стандартное отклонение весов — `min(0.1, sqrt(2/in_features))`, смещений — `0.01`. Конструктор принимает генератор и тип чисел. Один генератор с seed, переданный всем слоям, обеспечивает воспроизводимость без повторения одинакового потока случайных значений для каждого слоя.

## 6. ReLU and Sequential / ReLU и Sequential

**EN:** ReLU returns `maximum(0, X)` and saves `X > 0`. Its backward pass multiplies by that mask, choosing derivative zero at X=0. It has no parameters. Nonlinearity prevents a stack of affine maps from collapsing into one affine map.

**RU:** ReLU возвращает `maximum(0, X)` и сохраняет маску `X > 0`. Обратный проход умножает на маску; при X=0 выбирается производная ноль. Параметров нет. Нелинейность не позволяет последовательности аффинных преобразований свестись к одному аффинному преобразованию.

**EN:** `Sequential` inherits `Layer`, contains `Layer` objects and may contain another `Sequential`. Forward iterates in ordinary order; backward iterates over `reversed(self.layers)`. A list comprehension recursively flattens the parameters while preserving their object identity and order. An empty Sequential acts as the identity transformation.

**RU:** `Sequential` наследует `Layer`, содержит объекты `Layer` и может содержать другой `Sequential`. Прямой проход идёт в обычном порядке, обратный — по `reversed(self.layers)`. Списковое включение рекурсивно разворачивает параметры, сохраняя их порядок и идентичность объектов. Пустой Sequential действует как тождественное преобразование.

## 7. MSELoss / Функция потерь MSE

$$L=\frac{1}{nk}\sum_{i=1}^{n}\sum_{j=1}^{k}(\hat Y_{ij}-Y_{ij})^2,$$

$$G_{\mathrm{prediction}}=\frac{2(\hat Y-Y)}{nk}.$$

**EN:** `forward` checks exact shape equality, caches the difference and returns a Python float. `backward` divides by `difference.size`, which equals n×k. Dividing by n again in Linear would make the gradients too small. Shape checks prevent broadcasting a `(n, 1)` target against `(n, 10)` predictions and silently computing an unintended loss.

**RU:** `forward` проверяет точное совпадение форм, сохраняет разность и возвращает float Python. `backward` делит на `difference.size`, то есть n×k. Повторное деление на n внутри Linear сделало бы градиенты слишком малыми. Проверка форм предотвращает незаметное распространение ответа `(n, 1)` на прогнозы `(n, 10)` и расчёт другой ошибки.

## 8. SGD and training / SGD и обучение

```python
optimizer.zero_grad()
prediction = model(x_batch)
loss = criterion(prediction, target_batch)
model.backward(criterion.backward())
optimizer.step()
```

**EN:** Backward accumulates into `grad` with `+=`; zeroing before a new batch prevents mixing gradients unintentionally. `step` subtracts `lr * grad` from values and does not clear gradients. Positive finite learning rate is validated. Repeated parameter references are updated once by SGD.

**RU:** Обратный проход накапливает `grad` через `+=`; обнуление перед новой порцией предотвращает случайное смешивание градиентов. `step` вычитает `lr * grad` и не очищает градиенты. Проверяется положительная конечная скорость. Повторные ссылки на параметр обновляются SGD один раз.

**EN:** `train` checks nonempty two-dimensional data, matching object counts, positive integer epochs and batch size. One permutation indexes both inputs and targets. `range(0, N, batch_size)` includes the final incomplete batch. For 60,000 objects and batch size 128, each epoch has 469 batches; the last has 96 objects.

**RU:** `train` проверяет непустые двумерные данные, одинаковое число объектов, положительные целые эпохи и размер порции. Одна перестановка индексирует входы и ответы. `range(0, N, batch_size)` включает последнюю неполную порцию. При 60 000 объектах и размере 128 получается 469 порций, последняя содержит 96 объектов.

**EN:** Epoch history uses `sum(batch_loss * actual_batch_length) / N`. This averages per-object losses observed during training, at changing parameter values. It is not a separate full-dataset loss evaluated at the final weights. The test set is never passed into `train`.

**RU:** История эпох использует `sum(batch_loss * actual_batch_length) / N`. Усредняются ошибки объектов, измеренные в процессе обучения при меняющихся параметрах. Это не отдельный расчёт всей выборки на конечных весах. Тестовая выборка не передаётся в `train`.

## 9. MNIST and evaluation / MNIST и оценка

**EN:** `fetch_openml("mnist_784", version=1)` provides 70,000 flattened 28×28 images. We explicitly use its `liac-arff` parser to avoid numeric-category parsing issues with the installed pandas version. This changes parsing, not the dataset. The first 60,000 rows are training and the final 10,000 are test data. Divide float32 pixels by 255; construct training targets with `np.eye(10)[labels_train]`.

**RU:** `fetch_openml("mnist_784", version=1)` загружает 70 000 развёрнутых изображений 28×28. Явно используется парсер `liac-arff`, чтобы избежать проблемы числовых категорий в установленной версии pandas. Меняется разбор файла, а не датасет. Первые 60 000 строк обучающие, последние 10 000 тестовые. Пиксели float32 делятся на 255; ответы строятся через `np.eye(10)[labels_train]`.

**EN:** The architecture 784→32→ReLU→10 has 25,450 trainable values. MSE compares its ten scores to one-hot targets. `argmax(axis=1)` returns a predicted digit. Scores need not sum to one and are not probabilities. Accuracy measures correct digit decisions, while MSE measures numerical output-vector errors.

**RU:** Архитектура 784→32→ReLU→10 содержит 25 450 обучаемых чисел. MSE сравнивает десять оценок с one-hot ответами. `argmax(axis=1)` возвращает предсказанную цифру. Оценки не обязаны давать сумму один и не являются вероятностями. Accuracy измеряет правильность выбора цифры, MSE — числовую ошибку выходного вектора.

**EN:** Evaluation uses batches of 512 and never updates parameters. The confusion matrix uses true labels for rows and predictions for columns. Its diagonal counts correct predictions. Example images are the first twelve test images, without selection by correctness. Results and settings are recorded in `results/metrics.json`.

**RU:** Оценка выполняется порциями по 512 без обновления параметров. В матрице ошибок строки соответствуют настоящим цифрам, столбцы — прогнозам; диагональ считает правильные ответы. Примеры — первые двенадцать тестовых изображений без отбора по успешности. Результаты и настройки сохраняются в `results/metrics.json`.

## 10. Persistence and verification / Сохранение и проверка

**EN:** `Sequential.save` stores a versioned JSON architecture and numeric parameter arrays inside NPZ. Nested containers are preserved. `Sequential.load` uses `allow_pickle=False`, validates supported types and parameter shapes, rebuilds the model and copies saved arrays. It resets gradients and caches. The notebook compares every restored test score with `assert_array_equal`, using the same evaluation batch size.

**RU:** `Sequential.save` записывает структуру JSON с версией формата и числовые массивы параметров в NPZ. Вложенность сохраняется. `Sequential.load` использует `allow_pickle=False`, проверяет типы и формы, восстанавливает модель и копирует массивы. Градиенты и кэши сбрасываются. Блокнот сравнивает все восстановленные тестовые оценки через `assert_array_equal` с одинаковым размером порций.

```powershell
.venv\Scripts\python -m pytest -q
```

**EN:** The six tests cover known forward values and nested parameter identity, finite-difference gradients for all weights/biases/inputs, accumulation and SGD, ReLU/MSE values, invalid shapes and call order, nested save/load, successful regression learning and weighted short batches.

**RU:** Шесть тестов проверяют известные значения прямого прохода и идентичность вложенных параметров, численные производные всех весов/смещений/входов, накопление и SGD, значения ReLU/MSE, неверные формы и порядок вызовов, сохранение вложенности, обучение регрессии и вес короткой последней порции.

## 11. Scope / Границы реализации

**EN:** This is a sequential educational library. Each layer object caches one forward pass: use a distinct object at each model position and backpropagate before another forward overwrites its cache. Nested Sequential models are supported; graphs with the same layer reused multiple times are not. There is no GPU execution, convolution, general autodiff or optimizer checkpoint. Report the measured accuracy, not a guarantee for arbitrary settings or environments.

**RU:** Это учебная последовательная библиотека. Объект слоя хранит один прямой проход: используйте отдельный объект на каждой позиции и выполняйте обратный проход до перезаписи кэша следующим прямым проходом. Вложенные Sequential поддерживаются, графы с многократным использованием одного объекта слоя — нет. Нет GPU, свёрток, общего автодифференцирования и контрольной точки оптимизатора. Указывайте измеренную точность, а не гарантию для любых настроек и окружений.
