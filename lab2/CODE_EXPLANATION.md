# Lab 2 code explanation / Объяснение кода ЛР2

## 1. What to open / Что открыть

**EN:** [analysis.ipynb](analysis.ipynb) is the complete solution: code, executed results, four Matplotlib plots and bilingual explanations. Its sections follow tasks 1–10 in the assignment. The airport CSV comes from Lab 1: `X = elevation_ft`, `G = kind`.

**RU:** [analysis.ipynb](analysis.ipynb) — полное решение: код, результаты выполнения, четыре графика Matplotlib и пояснения на двух языках. Разделы соответствуют заданиям 1–10. Используется CSV аэропортов из ЛР1: `X = elevation_ft`, `G = kind`.

From the repository root / Из корня репозитория:

```powershell
.venv\Scripts\python -m pip install -r lab2\requirements.txt
.venv\Scripts\python -m jupyterlab
```

**EN:** Open the notebook and choose **Kernel → Restart Kernel and Run All Cells**. Run top to bottom: rerunning a random-selection cell alone advances the generator and changes its selection. The initial cell supports starting from the root or the lab directory. Saved plots and summaries are in `lab2/results/`.

**RU:** Откройте блокнот и выберите **Kernel → Restart Kernel and Run All Cells**. Выполняйте ячейки сверху вниз: повторный запуск отдельной ячейки случайной выборки продвигает генератор и меняет выбор. Первая ячейка поддерживает запуск из корня или каталога лабораторной. Графики и сводки сохраняются в `lab2/results/`.

## 2. Main variables / Основные переменные

| Name | English | Русский |
| --- | --- | --- |
| `df`, `original` | Baseline table and its verification copy. | Исходная таблица и копия для проверки её неизменности. |
| `rng` | A NumPy generator initialized with seed 42. | Генератор NumPy с начальным состоянием 42. |
| `hidden_indices`, `truth` | Positions and true heights hidden for evaluation. | Индексы и настоящие высоты, скрытые для проверки. |
| `damaged` | Copy with the selected heights removed. | Копия с удалёнными выбранными высотами. |
| `imputed` | Three independently filled copies. | Три независимо заполненные копии. |
| `with_duplicates` | Baseline plus 400 copied rows. | Исходные строки плюс 400 скопированных строк. |
| `and_mask`, `or_mask` | Boolean row selectors. | Булевы маски выбора строк. |
| `group_stats` | One summary per airport type. | Одна сводка на каждый тип аэропорта. |
| `enriched` | Original rows with group size, mean and delta. | Исходные строки с размером группы, средним и отклонением. |

## 3. Loading and cleaning / Загрузка и подготовка

```python
df = pd.read_csv(DATA, keep_default_na=False, na_values=["", "null", "NULL"])
df[X] = pd.to_numeric(df[X], errors="coerce")
df[G] = df[G].astype("string").str.strip().replace("", pd.NA).fillna("Неизвестно")
```

**EN:** `read_csv` recognizes empty fields and explicit null markers as missing. Disabling default NA markers preserves `NA`, the country code for Namibia, as text. Numeric conversion guarantees that statistics use numbers rather than strings. Missing heights remain missing, because zero is a real elevation. Group labels are trimmed and missing labels become `Неизвестно`. No decade column is needed for the airport variant.

**RU:** `read_csv` распознаёт пустые поля и явные маркеры null как пропуски. Отключение стандартных маркеров сохраняет `NA`, код Намибии, как текст. Преобразование гарантирует числовой тип высоты. Пропуски остаются пропусками: ноль — настоящая высота. У названий групп удаляются крайние пробелы, пустые названия заменяются на `Неизвестно`. Для аэропортов столбец десятилетия не нужен.

## 4. Controlled missing-value experiment / Эксперимент с пропусками

**EN:** Choose only indices whose original height is known. `rng.choice(..., replace=False)` selects each index at most once. Ten percent of 6,550 known heights means 655 removed values. `truth` keeps them in the same index order used to calculate errors. The original 1,450 missing heights have no known answers and are excluded from evaluation.

**RU:** Выбираются только строки с известной исходной высотой. `rng.choice(..., replace=False)` не выбирает одну строку дважды. Удаляются 655 значений — 10% от 6 550 известных высот. В `truth` сохраняется тот же порядок индексов, что используется при проверке. Для 1 450 исходных пропусков правильные ответы неизвестны, поэтому они не входят в метрики.

**EN:** Compute the global mean, global median and per-type medians from `damaged`, after removal. `groupby(G)[X].transform("median")` broadcasts the appropriate group median back to every original row. Its fallback is the remaining global median. Each method gets an independent copy. Filling also resolves original missing values, but metrics use only `hidden_indices`.

**RU:** Общее среднее, общая медиана и медианы типов считаются по `damaged` после удаления. `groupby(G)[X].transform("median")` возвращает каждой строке медиану её группы. Резервное значение — общая медиана оставшихся данных. Каждый способ работает со своей копией. Заполняются также исходные пропуски, но метрики считаются только на `hidden_indices`.

```python
difference = restored.loc[hidden_indices, X].to_numpy() - truth.to_numpy()
mae = np.mean(np.abs(difference))
mse = np.mean(difference ** 2)
```

**EN:** MAE averages absolute errors in feet; MSE averages squared errors in square feet. A 100-foot error contributes 100 to the absolute-error sum and 10,000 to the squared-error sum. The saved results show that the group median wins MAE, while the global mean wins MSE.

**RU:** MAE усредняет абсолютные ошибки в футах, MSE — квадраты ошибок в квадратных футах. Ошибка 100 футов даёт вклад 100 в сумму модулей и 10 000 в сумму квадратов. В сохранённом эксперименте медиана группы лучше по MAE, а общее среднее — по MSE.

## 5. Duplicate experiment / Эксперимент с повторами

**EN:** A separate baseline copy receives 5% extra rows through `pd.concat`. `drop_duplicates()` compares all columns; `subset="id"` compares identities; `subset="country"` keeps only one row per country value. All use the default `keep="first"`. They are independent operations on the same augmented table.

**RU:** В отдельную копию добавляются 5% строк через `pd.concat`. `drop_duplicates()` сравнивает все столбцы, `subset="id"` — идентификаторы, `subset="country"` — страны и оставляет одну строку на значение страны. Везде действует `keep="first"`. Способы независимо применяются к одной таблице с добавленными повторами.

**EN:** The baseline has unique IDs and no exact duplicate rows. Therefore the first two methods recover 8,000 rows and the original mean. Deduplication by country leaves 193 rows and removes legitimate airports. The notebook displays different IDs sharing one country to demonstrate this loss.

**RU:** В исходной таблице id уникальны, полных повторов нет. Поэтому первые два способа возвращают 8 000 строк и исходное среднее. Удаление по стране оставляет 193 строки и теряет настоящие аэропорты. Блокнот показывает разные id с общей страной, чтобы продемонстрировать потерю данных.

## 6. Manual statistics / Статистика вручную

**EN:** Drop missing heights, sort the remaining values, then use loops and arithmetic. The range is last minus first. The mean is a loop sum divided by N. For even N, the median is the mean of positions `N//2 - 1` and `N//2`. Variance is the sum of squared deviations divided by N; standard deviation is its square root. Ready-made functions are used only in the comparison columns.

**RU:** Убираем пропуски, сортируем значения и используем циклы и арифметику. Размах — последнее значение минус первое. Среднее — сумма в цикле, делённая на N. При чётном N медиана — среднее элементов `N//2 - 1` и `N//2`. Дисперсия — сумма квадратов отклонений, делённая на N; стандартное отклонение — её корень. Готовые функции используются только в столбцах сравнения.

**EN:** NumPy and pandas use `ddof=0` in this comparison. pandas normally uses `ddof=1` for variance and standard deviation. `assert_allclose` accepts tiny floating-point rounding differences while detecting a wrong formula.

**RU:** При сравнении NumPy и pandas используют `ddof=0`. Обычно pandas считает дисперсию и стандартное отклонение с `ddof=1`. `assert_allclose` допускает небольшую погрешность чисел с плавающей точкой, но обнаруживает неверную формулу.

## 7. Boolean filters and top five / Булевы фильтры и пять максимумов

```python
in_group = df[G].isin(["small_airport", "medium_airport"])
above = df[X].gt(500).fillna(False)
and_mask = in_group & above
or_mask = in_group | above
only_or = df.loc[or_mask & ~and_mask]
```

**EN:** pandas masks use `&`, `|`, and `~` for elementwise AND, OR, and NOT. Python `and` and `or` do not combine whole Series this way. OR contains every AND row, plus rows satisfying just one condition. A missing height fails `above`, but may still satisfy OR through `in_group`.

**RU:** Маски pandas используют `&`, `|` и `~` для поэлементных И, ИЛИ и НЕ. Операторы Python `and` и `or` так не объединяют Series. В ИЛИ входят все строки И и строки, удовлетворяющие только одному условию. Пропуск высоты не проходит `above`, но может пройти ИЛИ по группе.

**EN:** `df.loc[and_mask].nlargest(5, X)` selects the five highest eligible rows. Reversing the operations selects among the global five only. The notebook prints both tables and compares ordered IDs. The methods differ on these data and are not interchangeable in general.

**RU:** `df.loc[and_mask].nlargest(5, X)` находит пять самых высоких подходящих строк. Обратный порядок выбирает только из пяти глобальных максимумов. Блокнот выводит обе таблицы и сравнивает порядок id. Здесь результаты различаются; в общем случае операции не взаимозаменяемы.

## 8. Group summaries and enrichment / Сводки групп и обогащение строк

**EN:** `size` counts all rows, while a count of X would exclude missing heights. `share` divides group size by 8,000. Mean and median skip missing X. Sorting counts descending and calling `invert_yaxis()` puts the largest horizontal bar on top.

**RU:** `size` считает все строки, а подсчёт X исключил бы пропуски высоты. `share` делит размер группы на 8 000. Среднее и медиана игнорируют пропуски X. Сортировка по убыванию количества и `invert_yaxis()` помещают крупнейшую горизонтальную полосу наверх.

```python
enriched = df.join(group_stats[["group_count", "group_mean"]], on=G, validate="many_to_one")
enriched["delta"] = enriched[X] - enriched["group_mean"]
```

**EN:** The join matches each airport type to exactly one summary row. `validate="many_to_one"` detects repeated group keys on the summary side, which otherwise could multiply rows. Assertions check the row count and index. Positive delta means above the group mean; it does not imply above the overall mean.

**RU:** Соединение сопоставляет тип каждого аэропорта ровно одной строке сводки. `validate="many_to_one"` обнаруживает повторные ключи в сводке, которые могли бы размножить строки. Проверяются число строк и индекс. Положительная delta означает превышение среднего своей группы, а не обязательно общего среднего.

**EN:** Both delta plots use the first 100 objects with observed heights. The scatter preserves source order. The line chart sorts those same objects by delta and uses new evenly spaced positions 1–100, ensuring a nondecreasing line.

**RU:** Оба графика delta используют первые 100 объектов с известной высотой. Точечный график сохраняет исходный порядок. Линейный сортирует те же объекты по delta и использует новые равноотстоящие номера 1–100, поэтому линия не убывает.

## 9. Quantiles, boxplots and saved results / Квантили, boxplot и результаты

**EN:** Quantiles are calculated at 0.25, 0.5 and 0.75. Q2 equals the median. The five boxplots use the groups with the largest row counts; missing heights are dropped inside each group. IQR is Q3−Q1, measuring central spread. Range also reflects extremes, so the two spread measures can disagree. The final assertion confirms `df` still equals `original`.

**RU:** Квантили считаются на уровнях 0,25, 0,5 и 0,75. Q2 равна медиане. Для boxplot выбираются пять групп с наибольшим числом строк; пропуски исключаются внутри групп. IQR = Q3−Q1 описывает центральный разброс. Размах учитывает также крайние значения, поэтому меры могут различаться. Последняя проверка подтверждает равенство `df` и `original`.

**EN:** `results/summary.json` contains measured statistics; CSV files hold imputation and group summaries. Four PNG files match the plots in the notebook. [REPORT.md](REPORT.md) interprets these results; [DEFENSE_PREPARATION.md](DEFENSE_PREPARATION.md) provides oral answers in both languages.

**RU:** `results/summary.json` содержит измеренные характеристики; CSV — метрики заполнения и сводки групп. Четыре PNG соответствуют графикам блокнота. [REPORT.md](REPORT.md) объясняет результаты, [DEFENSE_PREPARATION.md](DEFENSE_PREPARATION.md) содержит устные ответы на двух языках.
