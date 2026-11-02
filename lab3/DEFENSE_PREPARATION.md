# Lab 3 defense preparation / Подготовка к защите ЛР3

## 1. One-minute presentation in English

“I built a small neural-network library using NumPy, with manual backpropagation. Its abstract Layer interface defines forward, backward and parameter access. Linear stores weights and bias as Parameter objects, ReLU introduces nonlinearity, and Sequential composes layers, including nested models. MSELoss measures the average squared difference over both objects and outputs. SGD updates parameters using their accumulated gradients. The training function shuffles inputs and targets together, processes every mini-batch, and returns sample-weighted epoch losses. I trained a 784–32–10 model on the first 60,000 MNIST images and evaluated it on the remaining 10,000. The notebook shows baseline and trained accuracy, the loss curve, a confusion matrix and example predictions. Saving records both architecture and parameter values; reloading reproduces every test score exactly. The notebook contains the complete code and writes it into separate modules.”

## 1. Выступление на минуту на русском

«Я реализовал небольшую библиотеку нейронных сетей на NumPy с ручным обратным распространением. Абстрактный Layer задаёт прямой и обратный проходы и доступ к параметрам. Linear хранит веса и смещение в объектах Parameter, ReLU добавляет нелинейность, Sequential объединяет слои и поддерживает вложенные модели. MSELoss усредняет квадраты ошибок по объектам и выходам. SGD обновляет параметры по накопленным градиентам. Функция обучения одновременно перемешивает входы и ответы, обрабатывает все порции и возвращает ошибку эпох с учётом количества объектов. Я обучил модель 784–32–10 на первых 60 000 изображениях MNIST и оценил её на оставшихся 10 000. Блокнот показывает точность до и после, кривую ошибки, матрицу ошибок и примеры прогнозов. Сохраняются структура и значения параметров; загрузка точно воспроизводит все тестовые выходы. Полный код находится в блокноте и сохраняется в отдельные модули».

## 2. Demonstration plan / План демонстрации

From the repository root / Из корня проекта:

```powershell
.venv\Scripts\python -m jupyterlab
```

1. **EN:** Open `lab3/tutorial.ipynb` and explain the initial class diagram. **RU:** Откройте блокнот и объясните первоначальную диаграмму классов.
2. **EN:** Show the `%%writefile` cells containing the full implementation. They overwrite the module files shown in their headers. **RU:** Покажите ячейки с полным кодом. Они перезаписывают модули, указанные в заголовках.
3. **EN:** Run the small example: predictions `[9, 8]`, MSE 4, then a lower loss after one step. **RU:** Выполните маленький пример: прогнозы `[9, 8]`, MSE 4 и уменьшение ошибки после шага.
4. **EN:** Show numerical and analytical gradients and the pytest output. **RU:** Сравните численный и аналитический градиенты, покажите вывод pytest.
5. **EN:** Explain MNIST shapes and one-hot labels. Show measured accuracy before and after training. **RU:** Объясните формы MNIST и one-hot, покажите измеренную точность до и после обучения.
6. **EN:** Show the epoch-loss curve, test images and confusion matrix. Explain an off-diagonal cell. **RU:** Покажите кривую ошибки, изображения и матрицу ошибок. Объясните ячейку вне диагонали.
7. **EN:** Show the saved model and exact equality after reload. Finish with the final UML. **RU:** Покажите файл модели и точное совпадение после загрузки. Завершите итоговой UML.

**EN:** The saved notebook already contains executed outputs. A fresh **Restart Kernel and Run All Cells** reproduces the experiment; the first run downloads MNIST. For a shorter defense, demonstrate the small example and use the saved training results without claiming you just retrained it.

**RU:** В блокноте уже сохранены результаты. **Restart Kernel and Run All Cells** воспроизводит эксперимент; первый запуск скачивает MNIST. Для короткой защиты выполните маленький пример и покажите сохранённое обучение, не утверждая, что только что обучили модель заново.

## 3. OOP questions / Вопросы по ООП

### Where is encapsulation? / Где инкапсуляция?

**EN:** Each object owns related state and behavior: a Linear has weights, bias and the cached input; Parameter pairs values with gradients; Sequential manages ordered layers. Methods operate on this state. Underscore-prefixed caches are implementation details, although Python does not enforce strict private access.

**RU:** Объект объединяет связанное состояние и поведение: Linear хранит веса, смещение и кэш входа; Parameter связывает значения и градиенты; Sequential управляет порядком слоёв. Методы работают с этим состоянием. Кэши с подчёркиванием — детали реализации, хотя Python не запрещает доступ к ним строго.

### Where are inheritance and polymorphism? / Где наследование и полиморфизм?

**EN:** Linear, ReLU and Sequential inherit Layer. The same `layer(x)`, `layer.backward(g)` and `layer.parameters()` calls perform different operations depending on the actual layer type. The container does not need a branch for every layer type during forward or backward.

**RU:** Linear, ReLU и Sequential наследуют Layer. Одинаковые вызовы `layer(x)`, `layer.backward(g)` и `layer.parameters()` выполняют разные действия в зависимости от типа слоя. При прямом и обратном проходах контейнеру не нужны отдельные ветви для каждого типа.

### What is composition? / Что такое композиция?

**EN:** Sequential contains layer objects, and Linear contains two Parameter objects. A Sequential may itself be a child layer, creating nested models. Inheritance expresses “is a layer”; composition expresses “contains layers.”

**RU:** Sequential содержит объекты слоёв, Linear — два объекта Parameter. Sequential сам может быть дочерним слоем, образуя вложенные модели. Наследование выражает «является слоем», композиция — «содержит слои».

### Why make Layer abstract? / Зачем абстрактный Layer?

**EN:** It specifies the required interface and prevents instantiation without implementations of forward and backward. Common calling behavior and empty parameter access are implemented once in the base class.

**RU:** Он задаёт обязательный интерфейс и запрещает создание объекта без реализаций forward и backward. Общий механизм вызова и пустой список параметров реализованы один раз в базовом классе.

### What does self mean? / Что означает self?

**EN:** It refers to the current object instance. `self.weight` is the weight Parameter belonging to this specific Linear layer, not a global weight array.

**RU:** Это ссылка на текущий экземпляр. `self.weight` — объект Parameter конкретного Linear, а не глобальная матрица весов.

### Why return Parameter objects rather than copies? / Почему возвращаются Parameter, а не копии?

**EN:** The optimizer must update the same arrays used by forward. A copied Parameter would disconnect optimization from the model. The tests check object identity using `is`, including inside nested containers.

**RU:** Оптимизатор должен обновлять те же массивы, что использует forward. Копия Parameter отделила бы оптимизацию от модели. Тесты проверяют идентичность через `is`, в том числе во вложенных контейнерах.

## 4. Mathematics and backpropagation / Математика и обратное распространение

### What shapes are used in the first MNIST layer? / Какие формы у первого слоя MNIST?

**EN:** For a full batch: X is `(128, 784)`, W is `(784, 32)`, b is `(32,)`, and Y is `(128, 32)`. Bias broadcasts across 128 rows. The final layer returns `(128, 10)`.

**RU:** Для полной порции: X — `(128, 784)`, W — `(784, 32)`, b — `(32,)`, Y — `(128, 32)`. Смещение распространяется по 128 строкам. Последний слой возвращает `(128, 10)`.

### Why random initialization? / Зачем случайная инициализация?

**EN:** Different hidden units need different initial weights to break symmetry. Both trainable arrays use small random values near zero, as required. One seeded generator provides reproducible draws to successive layers.

**RU:** Разным скрытым нейронам нужны разные начальные веса, чтобы нарушить симметрию. Оба обучаемых массива получают малые случайные значения около нуля, как требует задание. Один генератор с seed воспроизводимо выдаёт значения последовательным слоям.

### What is a gradient? / Что такое градиент?

**EN:** It contains partial derivatives of the loss with respect to a parameter array. It indicates local steepest increase, so gradient descent subtracts a scaled gradient. A single step is not guaranteed to reduce loss if the learning rate is too large.

**RU:** Это частные производные ошибки по элементам массива параметра. Градиент указывает локальное направление наискорейшего роста, поэтому градиентный спуск вычитает его с коэффициентом. При слишком большой скорости отдельный шаг не обязан уменьшать ошибку.

### Why backward in reverse order? / Почему обратный проход идёт в обратном порядке?

**EN:** The chain rule requires the derivative from a layer's output before computing the derivative at its input. The loss first supplies a prediction gradient; each layer transforms it and passes it toward the input.

**RU:** Для цепного правила сначала нужна производная по выходу слоя, затем считается производная по входу. Функция потерь задаёт градиент предсказаний, каждый слой преобразует его и передаёт ближе к входу модели.

### Derive Linear's gradients / Выведите градиенты Linear

**EN:** With `Y = XW + b` and incoming `G = dL/dY`, the input gradient is `G @ W.T`, the weight gradient is `X.T @ G`, and the bias gradient is `G.sum(axis=0)`. Each product's dimensions match the array being differentiated.

**RU:** При `Y = XW + b` и входящем `G = dL/dY` градиент входа — `G @ W.T`, весов — `X.T @ G`, смещения — `G.sum(axis=0)`. Размер каждого результата совпадает с массивом, по которому берётся производная.

### Why does Linear cache X? / Зачем Linear сохраняет X?

**EN:** Its weight derivative uses the exact input from the corresponding forward pass. Backward cannot reconstruct that input from the output in general. The layer stores a copy so the caller cannot mutate the cached input accidentally.

**RU:** Производная весов использует именно вход соответствующего прямого прохода. В общем случае восстановить вход по выходу нельзя. Сохраняется копия, чтобы вызывающий код случайно не изменил кэш.

### Why ReLU? What happens at zero? / Зачем ReLU? Что происходит в нуле?

**EN:** It introduces nonlinearity and passes gradients only where the saved input is positive. At zero we choose derivative zero. Without nonlinearities, composing affine layers gives another affine transformation.

**RU:** Она добавляет нелинейность и пропускает градиенты только при положительном сохранённом входе. В нуле выбирается производная ноль. Без нелинейностей композиция аффинных слоёв остаётся аффинной.

### Derive MSE's gradient / Выведите градиент MSE

**EN:** MSE averages `(prediction - target)**2` over n objects and k outputs. The derivative of the square is twice the difference, so the prediction gradient is `2 * (prediction - target) / (n*k)`. We divide once, in the loss, rather than once per layer.

**RU:** MSE усредняет `(prediction - target)**2` по n объектам и k выходам. Производная квадрата — удвоенная разность, поэтому градиент равен `2 * (prediction - target) / (n*k)`. Деление выполняется один раз в функции потерь, а не в каждом слое.

### Why require identical target and prediction shapes? / Зачем одинаковые формы ответов и прогнозов?

**EN:** NumPy could broadcast different shapes and calculate a valid array for the wrong problem. Explicit equality makes a mismatched target a clear ValueError instead of a silent training error.

**RU:** NumPy может распространить разные формы и получить допустимый массив для другой задачи. Явная проверка превращает несоответствие в понятный ValueError вместо незаметной ошибки обучения.

### Why += and zero_grad? / Зачем += и zero_grad?

**EN:** Parameter gradients accumulate, allowing multiple contributions. To train each mini-batch independently, SGD clears them before the new forward/backward pass. `step()` updates values, while `zero_grad()` clears gradients; they have separate responsibilities.

**RU:** Градиенты параметров накапливаются, позволяя складывать несколько вкладов. Для независимого шага по порции SGD обнуляет их перед новым прямым и обратным проходом. `step()` обновляет значения, `zero_grad()` очищает градиенты; это разные обязанности.

### How did you check derivatives? / Как проверялись производные?

**EN:** Central finite differences perturb one parameter at a time by ±epsilon and estimate `(Lplus - Lminus)/(2*epsilon)`. The suite compares this estimate to analytical gradients for all weights, biases and inputs. It uses float64 and avoids the nondifferentiable ReLU point.

**RU:** Центральная разность меняет один параметр на ±epsilon и оценивает `(Lplus - Lminus)/(2*epsilon)`. Тесты сравнивают её с аналитическими градиентами всех весов, смещений и входов. Используется float64 и пример без попадания в недифференцируемую точку ReLU.

## 5. Training and MNIST / Обучение и MNIST

### Parameter versus hyperparameter? / Параметр и гиперпараметр?

**EN:** Weights and bias are learned parameters. Learning rate, batch size, number of epochs and hidden width are chosen hyperparameters. SGD changes parameters, not these settings.

**RU:** Веса и смещение — обучаемые параметры. Скорость, размер порции, число эпох и ширина скрытого слоя — выбираемые гиперпараметры. SGD изменяет параметры, а не эти настройки.

### What is an epoch? / Что такое эпоха?

**EN:** One complete pass through the training set. We shuffle a common index permutation for both inputs and targets. Ten epochs process the training set ten times, with a new permutation each epoch.

**RU:** Один полный проход по обучающей выборке. Одна перестановка индексов одновременно перемешивает входы и ответы. За десять эпох выборка обрабатывается десять раз, каждый раз с новой перестановкой.

### How do you handle the final batch? / Что с последней порцией?

**EN:** It is included even if shorter. With 60,000 objects and batches of 128, the last batch has 96 objects. Epoch loss weights every batch mean by its actual size, then divides by 60,000.

**RU:** Она обрабатывается, даже если короче остальных. При 60 000 объектах и размере 128 в последней порции 96 объектов. Ошибка каждой порции умножается на фактический размер, сумма делится на 60 000.

### Why normalize and use one-hot? / Зачем нормализация и one-hot?

**EN:** Dividing pixels by 255 keeps inputs in a manageable `[0, 1]` range. One-hot turns a digit label into ten targets aligned with the ten outputs: only the correct class has value one.

**RU:** Деление пикселей на 255 переводит входы в удобный диапазон `[0, 1]`. One-hot превращает цифру в десять ответов, соответствующих выходам: единица стоит только у правильного класса.

### Why MSE for classification? / Почему MSE для классификации?

**EN:** It is explicitly required by the assignment and can learn to approximate one-hot targets. We use argmax for decisions. Other classification losses exist, but they are outside this implementation.

**RU:** MSE прямо требуется заданием и позволяет приближать one-hot ответы. Для выбора класса используется argmax. Другие функции потерь для классификации существуют, но не входят в эту реализацию.

### Are outputs probabilities? / Выходы — вероятности?

**EN:** No. There is no softmax. Outputs may be negative or fail to sum to one. Their relative ordering determines the predicted digit.

**RU:** Нет. Softmax отсутствует. Выходы могут быть отрицательными и не давать сумму один. Предсказание определяется их относительным порядком.

### Why not train on all 70,000 images? / Почему не обучаться на всех 70 000 изображений?

**EN:** We need an untouched test set to assess generalization. The last 10,000 images are never passed to train or used for parameter updates. The hyperparameters follow the assignment example rather than being selected using test accuracy.

**RU:** Нужна отдельная тестовая выборка для оценки обобщения. Последние 10 000 изображений не передаются в train и не обновляют параметры. Гиперпараметры взяты из примера задания, а не подобраны по тестовой точности.

### How many trainable numbers? / Сколько обучаемых чисел?

**EN:** `784*32 + 32 + 32*10 + 10 = 25,450`. ReLU and MSE have none. There are four Parameter objects: two weight matrices and two bias vectors.

**RU:** `784*32 + 32 + 32*10 + 10 = 25 450`. У ReLU и MSE параметров нет. Объектов Parameter четыре: две матрицы весов и два вектора смещений.

### Accuracy versus MSE? / Чем accuracy отличается от MSE?

**EN:** Accuracy counts correct argmax decisions. MSE measures the numerical discrepancy from one-hot vectors. Outputs can get closer to targets without changing argmax, so the metrics need not change together.

**RU:** Accuracy считает правильные решения argmax. MSE измеряет числовое отличие от one-hot векторов. Выходы могут приблизиться к ответам без смены argmax, поэтому метрики не обязаны меняться одновременно.

### How to read the confusion matrix? / Как читать матрицу ошибок?

**EN:** Entry `[a, b]` counts test images of digit a predicted as b. The diagonal is correct predictions. Summing a row gives the number of true examples of that digit; diagonal divided by row total gives per-digit accuracy.

**RU:** Ячейка `[a, b]` считает изображения цифры a, предсказанные как b. Диагональ — правильные ответы. Сумма строки — число настоящих примеров цифры; диагональный элемент, делённый на сумму строки, даёт точность для этой цифры.

## 6. Saving, errors and limits / Сохранение, ошибки и ограничения

### What is saved? / Что сохраняется?

**EN:** Versioned JSON describes the recursive architecture; NPZ stores weights and biases with their numeric dtypes. Loading reconstructs nested containers and parameter values. It does not restore forward caches, accumulated gradients or an optimizer session.

**RU:** JSON с версией описывает рекурсивную структуру, NPZ хранит веса и смещения с числовыми типами. Загрузка восстанавливает вложенные контейнеры и значения параметров. Кэши прямого прохода, накопленные градиенты и сеанс оптимизатора не восстанавливаются.

### How do you prove loading works? / Как доказать правильность загрузки?

**EN:** Compare every saved-model test score with the original model's score using the same batch size. The notebook asserts exact array equality over all 10,000 test images. A separate test checks nested Sequential structure and zero gradients after loading.

**RU:** Сравнить все тестовые выходы загруженной и исходной моделей с одинаковым размером порции. Блокнот проверяет точное равенство массивов для всех 10 000 изображений. Отдельный тест проверяет вложенный Sequential и нулевые градиенты после загрузки.

### Which errors are handled? / Какие ошибки обрабатываются?

**EN:** Non-2D, empty, nonnumeric and nonfinite input; incompatible feature and gradient sizes; different target/prediction shapes; backward before forward; invalid learning rate; invalid epoch or batch counts; unsupported saved-layer types and malformed saved parameter shapes.

**RU:** Недвумерный, пустой, нечисловой и неконечный вход; несовместимые признаки и градиенты; разные формы ответов и прогнозов; backward до forward; неправильная скорость; неверное число эпох или размер порции; неподдерживаемые типы сохранённых слоёв и неправильные формы параметров.

### Can the same layer instance appear twice? / Можно использовать один экземпляр слоя дважды?

**EN:** This implementation caches one forward pass per layer object, so use separate instances at different positions. Nested containers are supported, but repeated use of the same object in a computation graph would overwrite its cache. This is a documented boundary of the sequential library.

**RU:** Реализация хранит один прямой проход на объект слоя, поэтому на разных позициях используются отдельные экземпляры. Вложенные контейнеры поддерживаются, повторное использование одного объекта в графе перезапишет кэш. Это указанное ограничение последовательной библиотеки.

### Is scikit-learn implementing the network? / scikit-learn реализует сеть?

**EN:** No. It only downloads and parses MNIST through fetch_openml. Model computations, derivatives, updates, training and accuracy use our own code and NumPy. Matplotlib draws figures; threadpoolctl only controls numerical-library thread counts.

**RU:** Нет. Она только скачивает и разбирает MNIST через fetch_openml. Вычисления модели, производные, обновления, обучение и accuracy выполняются своим кодом и NumPy. Matplotlib рисует графики, threadpoolctl лишь ограничивает число потоков вычислительных библиотек.

## 7. Formula sheet / Краткие формулы

Measured facts / Измеренные результаты: **5.71% → 89.51%** test accuracy / тестовая точность;
**0.071865 → 0.025767** epoch MSE / MSE эпох; **25,450** trainable values / обучаемых чисел;
**60,000 / 10,000** train/test objects / обучение/тест; **0.0** maximum reload difference / максимальное отличие после загрузки.

| Operation / Операция | Formula / Формула |
| --- | --- |
| Linear forward | `X @ W + b` |
| Linear input gradient | `G @ W.T` |
| Linear weight gradient | `X.T @ G` |
| Linear bias gradient | `G.sum(axis=0)` |
| ReLU backward | `G * (X > 0)` |
| MSE | `mean((prediction - target)**2)` |
| MSE backward | `2 * (prediction - target) / (n*k)` |
| SGD | `value -= lr * grad` |
| Epoch loss / Ошибка эпохи | `sum(batch_loss * actual_batch_size) / N` |
| Accuracy / Точность | `mean(argmax(scores, axis=1) == labels)` |

## 8. Twenty-second answer / Ответ на двадцать секунд

**EN:** “My NumPy library separates layers, parameters, loss and optimization. It supports nested sequential models, manual backpropagation, mini-batch SGD and architecture-aware saving. I verified derivatives numerically and trained a model on MNIST, measuring accuracy on a separate test split and checking exact predictions after reload.”

**RU:** «Моя библиотека NumPy разделяет слои, параметры, ошибку и оптимизацию. Она поддерживает вложенные последовательные модели, ручное обратное распространение, SGD по порциям и сохранение структуры. Производные проверены численно; модель обучена на MNIST, точность измерена на отдельном тесте, прогнозы после загрузки точно совпадают».
