# Lab 2 defense preparation / Подготовка к защите ЛР2

## 1. One-minute presentation / Выступление на минуту

**EN:** “I analyzed the same 8,000-airport catalog as in Lab 1. The numeric variable is elevation in feet, and the grouping variable is airport type. I used NumPy, pandas and Matplotlib in a Jupyter notebook, with seed 42 for reproducibility. I hid 655 known heights and compared mean, median and group-median imputation using MAE and MSE on only those hidden values. I separately added 400 duplicate rows and compared three deduplication keys. I calculated statistics manually and verified them against NumPy and pandas with population variance. I compared AND and OR filters and demonstrated that filtering and taking the top five do not generally commute. Finally, I summarized groups, attached group means to each object, plotted deviations, and compared quantiles and boxplots. The original table remains unchanged.”

**RU:** «Я исследовал тот же каталог из 8 000 аэропортов, что в ЛР1. Числовая переменная — высота в футах, группировка — тип аэропорта. Работа выполнена в Jupyter с NumPy, pandas и Matplotlib; seed 42 обеспечивает воспроизводимость. Я скрыл 655 известных высот и сравнил заполнение средним, медианой и медианой группы по MAE и MSE только на скрытых значениях. Отдельно добавил 400 повторов и сравнил три ключа удаления. Статистики посчитал вручную и проверил NumPy и pandas с делением дисперсии на N. Сравнил фильтры И и ИЛИ и показал, что фильтрация и выбор пяти максимумов в общем случае не перестановочны. Затем построил сводки групп, добавил к объектам средние групп, изобразил отклонения и сравнил квантили и boxplot. Исходная таблица не изменяется».

## 2. Demonstration / Демонстрация

1. **EN:** Start JupyterLab from the root with `.venv\Scripts\python -m jupyterlab`; open `lab2/analysis.ipynb`. **RU:** Запустите JupyterLab из корня и откройте блокнот.
2. **EN:** Restart the kernel and run all cells. Show 8,000 rows and 1,450 original missing heights. **RU:** Перезапустите ядро, выполните всё, покажите 8 000 строк и 1 450 исходных пропусков высоты.
3. **EN:** Show the 655 hidden values, metrics table, and the two different metric winners. **RU:** Покажите 655 скрытых значений, таблицу ошибок и разных победителей по метрикам.
4. **EN:** Show counts 8,000 → 8,400 → 8,000 for exact/ID deduplication, versus 193 by country. **RU:** Покажите изменение количества строк и потерю объектов при удалении по стране.
5. **EN:** Explain one manual formula, then show filter counts and both top-five tables. **RU:** Объясните одну ручную формулу, затем фильтры и обе таблицы пяти максимумов.
6. **EN:** Show the four plots, group-enriched rows and the unchanged-baseline assertion. **RU:** Покажите четыре графика, обогащённые строки и проверку неизменности исходной таблицы.

## 3. Questions and answers / Вопросы и ответы

### Why seed 42? / Зачем seed 42?

**EN:** It initializes the pseudorandom generator. The same seed, data and command order reproduce the selections. The number 42 itself has no special statistical property.

**RU:** Он задаёт начальное состояние псевдослучайного генератора. Одинаковые seed, данные и порядок команд воспроизводят выборки. Само число 42 не имеет особого статистического свойства.

### Why not hide 800 heights? / Почему скрывается не 800 высот?

**EN:** We hide 10% of rows with a known X, not 10% of all rows. There are 6,550 observed heights, so 655 can be hidden and evaluated against their true values.

**RU:** Скрываются 10% строк с известным X, а не 10% всех строк. Известных высот 6 550, поэтому скрываются 655 значений с доступными правильными ответами.

### What prevents data leakage? / Что предотвращает утечку данных?

**EN:** The filling statistics are calculated after removal. Saved true values are used only when computing errors, never when choosing replacement values.

**RU:** Статистики заполнения считаются после удаления. Сохранённые настоящие значения используются только при подсчёте ошибок, а не при выборе замены.

### How is the third method different? / Чем отличается третий способ?

**EN:** It fills each height with the median of its airport type. If a type has no remaining observed heights, the global observed median is the fallback. It uses group information without using the hidden answers.

**RU:** Высота заполняется медианой своего типа аэропорта. Если в типе не осталось известных высот, берётся общая медиана оставшихся данных. Используется информация о группе, но не скрытые ответы.

### Why do MAE and MSE prefer different methods? / Почему MAE и MSE выбирают разные способы?

**EN:** MAE weights errors linearly, whereas MSE squares them and emphasizes large mistakes. Here group median has MAE about 981.19 feet; global mean has the best MSE, about 2,595,470.66 square feet. The metrics have different units and are not directly comparable numerically.

**RU:** MAE учитывает ошибки линейно, MSE возводит их в квадрат и усиливает большие промахи. Здесь MAE медианы группы около 981,19 фута; лучшая MSE у общего среднего — около 2 595 470,66 квадратного фута. Метрики имеют разные единицы и не сравниваются напрямую по числу.

### Does median always beat mean? / Медиана всегда лучше среднего?

**EN:** No. A median minimizes absolute error for a constant estimate on a given sample; a mean minimizes squared error. In this experiment the estimates and evaluation values come from different subsets, so the observed ranking must be measured.

**RU:** Нет. Медиана минимизирует абсолютную ошибку постоянной оценки на данной выборке, среднее — квадратичную. Здесь оценки и проверочные значения получены из разных подвыборок, поэтому порядок методов определяется экспериментом.

### Why are the experiments independent? / Почему эксперименты независимы?

**EN:** Missing-value filling could change the means in the duplicate experiment. Separate copies isolate each operation and preserve the baseline used for all later tasks.

**RU:** Заполнение пропусков могло бы изменить средние в эксперименте с повторами. Отдельные копии изолируют операции и сохраняют исходную таблицу для следующих заданий.

### Why can adding exact copies change the mean? / Почему точные копии могут изменить среднее?

**EN:** The selected 5% need not have the same mean as the full dataset. Copying them gives their heights extra weight. The observed mean changes from about 1,302.38 to 1,301.26 feet.

**RU:** Среднее выбранных 5% не обязано совпадать с общим. Копирование увеличивает вес этих высот. Здесь среднее меняется примерно с 1 302,38 до 1 301,26 фута.

### Is country a good duplicate key? / Страна — хороший ключ дубликатов?

**EN:** No. Different airports share a country. Keeping one row per country leaves 193 rows and destroys legitimate data. A duplicate key should reflect object identity or the intended business rule.

**RU:** Нет. Разные аэропорты могут находиться в одной стране. Одна строка на страну оставляет 193 строки и удаляет настоящие объекты. Ключ должен отражать идентичность объекта или нужное правило предметной области.

### Why ddof=0? / Почему ddof=0?

**EN:** The assignment defines variance as the average squared deviation, dividing by N. `ddof=0` implements that. pandas defaults to N−1, which is the usual sample-variance correction.

**RU:** По заданию дисперсия — средний квадрат отклонений с делением на N. Это `ddof=0`. pandas по умолчанию делит на N−1, используя обычную поправку выборочной дисперсии.

### How do AND and OR differ? / Чем отличаются И и ИЛИ?

**EN:** AND requires both membership in the two chosen types and height above 500 feet. OR requires either condition. Here they select 2,456 and 5,814 rows; 3,358 rows occur only in OR.

**RU:** И требует одновременно подходящий тип и высоту выше 500 футов. ИЛИ требует хотя бы одно условие. Здесь получаются 2 456 и 5 814 строк; только в ИЛИ находятся 3 358 строк.

### Can a missing height pass OR? / Может ли пропуск высоты пройти ИЛИ?

**EN:** Yes, through the group condition. It never passes the height condition itself. Missing does not mean either zero or a height above the threshold.

**RU:** Да, по условию группы. Само условие высоты пропуск никогда не проходит. Пропуск не означает ни ноль, ни превышение границы.

### Why does operation order matter? / Почему важен порядок операций?

**EN:** Taking the global top five permanently discards other rows. Filtering afterward cannot recover eligible rows outside those five. Filtering first searches for the top five among all eligible objects. They coincide when the relevant global leaders already satisfy the filter; generally they need not coincide.

**RU:** Общий top-5 заранее отбрасывает остальные строки. Последующая фильтрация не вернёт подходящие объекты за его пределами. Фильтрация сначала ищет top-5 среди всех подходящих объектов. Результаты совпадают, когда нужные глобальные лидеры уже проходят фильтр, но в общем случае совпадение не гарантируется.

### Why size instead of count? / Почему size, а не count?

**EN:** Group size must include every row. Counting X excludes missing heights and undercounts airports. Missing-X counts are reported separately.

**RU:** Размер группы должен учитывать все строки. Подсчёт X исключает пропуски и занижает число аэропортов. Количество пропусков указывается отдельно.

### What does delta mean? / Что означает delta?

**EN:** `delta = airport_height - mean_height_of_its_type`. A positive value means the airport is above its type's mean; a negative value means below. Missing heights produce missing deltas.

**RU:** `delta = высота аэропорта - средняя высота его типа`. Положительное значение — выше среднего своего типа, отрицательное — ниже. Пропуск высоты даёт пропуск отклонения.

### How does the join avoid multiplying rows? / Как соединение избегает размножения строк?

**EN:** There is exactly one summary row per group. The join uses `validate="many_to_one"`, and assertions check the resulting row count and index.

**RU:** Каждой группе соответствует ровно одна строка сводки. Используется `validate="many_to_one"`; затем проверяются число строк и индекс результата.

### Why is the sorted line nondecreasing? / Почему отсортированная линия не убывает?

**EN:** The same 100 objects are sorted by delta, and their new positions are 1 through 100. We do not plot their old indices, which could move backward on the horizontal axis.

**RU:** Те же 100 объектов сортируются по delta и получают новые позиции от 1 до 100. Старые индексы не используются, иначе горизонтальная координата могла бы двигаться назад.

### What does a boxplot show? / Что показывает boxplot?

**EN:** The median, Q1–Q3, whiskers extending to observed values within 1.5 IQR, and points beyond them. A point outside the whiskers is not automatically an error. Negative airport elevations can be valid.

**RU:** Медиану, интервал Q1–Q3, усы до наблюдений в пределах 1,5 IQR и точки за усами. Точка за усами не обязательно ошибочна. Отрицательные высоты аэропортов могут быть настоящими.

## 4. Formulas to remember / Формулы для запоминания

| Quantity / Величина | Formula / Формула |
| --- | --- |
| MAE | `sum(abs(predicted - true)) / N` |
| MSE | `sum((predicted - true)**2) / N` |
| Mean / Среднее | `sum(x) / N` |
| Population variance / Дисперсия с делением на N | `sum((x - mean)**2) / N` |
| Standard deviation / Стандартное отклонение | `variance**0.5` |
| Range / Размах | `maximum - minimum` |
| IQR | `Q3 - Q1` |
| Delta / Отклонение | `X - group_mean` |

## 5. Twenty-second answer / Ответ на двадцать секунд

**EN:** “I used reproducible experiments to compare missing-value filling and duplicate removal, verified manual statistics, contrasted logical filters and operation order, and analyzed each airport relative to its type using group summaries, deviations and boxplots. Every experiment preserves the original data, and every reported number comes from the executed notebook.”

**RU:** «Я провёл воспроизводимые эксперименты с заполнением пропусков и удалением повторов, проверил ручную статистику, сравнил логические фильтры и порядок операций, затем исследовал аэропорты относительно их типов с помощью сводок, отклонений и boxplot. Эксперименты сохраняют исходные данные, а все числа получены выполнением блокнота».
