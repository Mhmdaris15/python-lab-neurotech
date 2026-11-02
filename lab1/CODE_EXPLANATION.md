# Code walkthrough / Разбор кода

This guide explains [`main.py`](main.py) for the lab defense (защита). It covers the shared design and both assigned variants:

- Airports: `airports-csv | title | clean | words-all | top10 | mark | boost`
- Artworks: `artworks-csv | title | clean | words-all | ranked | mark | none`

Этот документ объясняет файл [`main.py`](main.py) для защиты лабораторной. Здесь разобраны общая архитектура и оба назначенных варианта:

- Аэропорты: `airports-csv | title | clean | words-all | top10 | mark | boost`
- Картины: `artworks-csv | title | clean | words-all | ranked | mark | none`

---

## 1. What the program does / Что делает программа

The program loads rows from a CSV file and provides a command loop. It can display records, search their **title** fields, apply filters, highlight matching words, save the last displayed results, and (for airports) rate records and use ratings to boost their order.

Программа загружает строки из CSV-файла и запускает цикл команд. Она показывает записи, ищет по полю **title**, применяет фильтры, подсвечивает найденные слова, сохраняет последнюю выдачу и (для аэропортов) позволяет оценивать записи, влияя оценкой на порядок результатов.

Run from the `lab1` directory:

```bash
python main.py                     # airports / аэропорты
python main.py --variant artworks # artworks / картины
```

Запускать команды нужно из каталога `lab1`. В первом случае запускается вариант аэропортов, во втором — картин.

---

## 2. Imports, constants, and variant configuration / Импорты, константы и настройки вариантов

### Imports / Импорты

- `argparse` reads `--variant` from the command line. / Читает параметр `--variant` командной строки.
- `csv` parses comma-separated files, including quoted values that contain commas. / Разбирает CSV, включая значения в кавычках с запятыми.
- `re` finds words for normalization and highlighting. / Находит слова при нормализации и подсветке.
- `shlex` splits an entered command while respecting quotes, so `search "red painting"` is one command with one query argument. / Разбирает команду с учётом кавычек, поэтому `search "red painting"` получает один аргумент запроса.
- `time` measures search duration with a high-resolution performance clock. / Измеряет длительность поиска с помощью точного таймера.
- `unicodedata` decomposes accented Unicode characters. / Разбирает Unicode-символы с диакритическими знаками.
- `Path` represents filesystem paths and makes paths relative to the script or current directory. / Представляет пути к файлам и позволяет строить пути относительно скрипта или текущего каталога.
- `Any` is used for values converted to different Python types when filtering. / Используется как общий тип для значений разных типов, полученных при фильтрации.

`from __future__ import annotations` postpones evaluation of type annotations. The annotations describe expected values and improve readability; they do not perform runtime validation.

`from __future__ import annotations` откладывает вычисление аннотаций типов. Аннотации показывают ожидаемые типы и делают код понятнее, но сами по себе не проверяют значения во время работы.

### `ROOT` and `VARIANTS` / `ROOT` и `VARIANTS`

`ROOT = Path(__file__).resolve().parent` finds the directory containing `main.py`. This lets default dataset paths work regardless of the shell's current directory.

`ROOT = Path(__file__).resolve().parent` получает каталог, в котором лежит `main.py`. Благодаря этому стандартные пути к данным не зависят от текущего каталога терминала.

`VARIANTS` is a dictionary of configurations. Each variant contains a CSV path, a rating mode, and a result limit:

- `airports`: airport CSV, `boost` ratings, maximum 10 displayed matches.
- `artworks`: artwork CSV, no ratings, no result limit (`None`).

`VARIANTS` — словарь настроек. Для каждого варианта заданы CSV-файл, режим оценок и ограничение числа результатов:

- `airports`: CSV аэропортов, оценки влияют на порядок, максимум 10 результатов.
- `artworks`: CSV картин, оценки отключены, лимита нет (`None`).

---

## 3. Standalone helper functions / Вспомогательные функции

### `normalize(value: str) -> str`

This function implements the `clean` processing mode:

1. `value.casefold()` performs Unicode-aware case-insensitive conversion.
2. `unicodedata.normalize("NFKD", ...)` decomposes accented letters into a base letter and a combining mark where possible.
3. The generator expression removes combining marks, so `é` compares like `e`.
4. `re.findall(r"\w+", ...)` extracts word-like sequences; punctuation becomes a separator.
5. Joining with spaces returns a normalized string, such as `"The Red-Bird!"` → `"the red bird"`.

The query and title both pass through this function before comparison, which is essential: both sides must use the same normalization rules.

Эта функция реализует режим обработки `clean`:

1. `value.casefold()` выполняет Unicode-преобразование для поиска без учёта регистра.
2. `unicodedata.normalize("NFKD", ...)` по возможности разделяет букву с диакритикой на базовую букву и комбинируемый знак.
3. Генератор удаляет комбинируемые знаки, поэтому `é` сравнивается как `e`.
4. `re.findall(r"\w+", ...)` извлекает последовательности символов слова; пунктуация становится разделителем.
5. Соединение пробелами возвращает нормализованную строку: например, `"The Red-Bird!"` → `"the red bird"`.

И запрос, и заголовок обрабатываются этой функцией. Это важно: правила нормализации для обеих сторон должны совпадать.

### `read_csv(path: Path) -> list[dict[str, str]]`

Opens a CSV file as UTF-8 (accepting an optional UTF-8 byte-order mark) and uses `csv.DictReader`. The result is a list of dictionaries: each row maps column names such as `id` and `title` to cell text. CSV values initially remain strings; filtering converts them when needed.

Открывает CSV в UTF-8 (допускает необязательную BOM-метку) и использует `csv.DictReader`. Результат — список словарей: каждая строка сопоставляет имена столбцов, например `id` и `title`, со значениями ячеек. После чтения значения остаются строками; фильтрация преобразует их при необходимости.

`newline=""` is the recommended mode for Python's CSV parser; it lets the CSV module handle line endings itself.

Параметр `newline=""` рекомендован для CSV-парсера Python: окончания строк обрабатывает сам модуль `csv`.

### `value_for_filter(raw: str) -> Any`

Trims surrounding whitespace, converts `true` or `false` (case-insensitively) to a Boolean, and otherwise tries to convert the text to `float`. If numeric conversion fails, it returns the original trimmed text. This allows one filter system to compare Boolean, numeric, and string columns.

Удаляет пробелы по краям, преобразует `true` и `false` (без учёта регистра) в Boolean, затем пытается преобразовать значение в `float`. Если это невозможно, возвращает исходный текст без пробелов по краям. Так одна система фильтров может сравнивать логические, числовые и строковые столбцы.

### `apply_filters(record, filters) -> bool`

Checks every filter attached to a record. A filter is a tuple `(field, operator, expected_value)`. All filters must pass, so they are combined with logical **AND**.

Проверяет все фильтры для одной записи. Фильтр — кортеж `(поле, оператор, ожидаемое_значение)`. Запись должна пройти каждый фильтр: условия соединяются логическим **И**.

The function first checks that the field exists and rejects an empty cell. It then converts the actual and expected values with `value_for_filter` and applies one operator:

- `eq` / `ne`: equal / not equal.
- `lt`, `le`, `gt`, `ge`: numeric comparisons; nonnumeric operands raise an error.
- `contains`: case-insensitive substring search on the original cell text.

Сначала функция проверяет наличие поля и отклоняет пустую ячейку. Затем преобразует значение записи и значение фильтра через `value_for_filter` и применяет оператор:

- `eq` / `ne`: равно / не равно.
- `lt`, `le`, `gt`, `ge`: числовые сравнения; при нечисловых значениях возникает ошибка.
- `contains`: поиск подстроки без учёта регистра в исходном тексте ячейки.

If one condition fails, it returns `False` immediately. If all pass, it returns `True`. / Если одно условие не выполнено, функция сразу возвращает `False`. Если выполнены все — `True`.

### `highlight(text, query_tokens) -> str`

Scans words in the original title with a regular expression. For each word, it normalizes that word and checks whether it is in the query token set. Matching original text is wrapped in `[[` and `]]`; all text between matches is copied unchanged. Highlighting preserves the title's original spelling and capitalization.

Находит слова в исходном заголовке регулярным выражением. Каждое слово нормализуется и проверяется на вхождение в множество слов запроса. Совпавший фрагмент исходного текста заключается в `[[` и `]]`, остальной текст копируется без изменений. Подсветка сохраняет исходное написание и регистр заголовка.

### `render_record(record, query_tokens=None) -> str`

Builds a printable card. The first line contains `[id] title`; the remaining lines show every other field. Empty values are displayed as an em dash (`—`). If query tokens are provided, the title is passed through `highlight` first.

Создаёт текст карточки. В первой строке выводятся `[id] title`, затем — остальные поля. Пустые значения отображаются длинным тире (`—`). Если переданы слова запроса, заголовок сначала обрабатывается функцией `highlight`.

---

## 4. The `CatalogSearchApp` class / Класс `CatalogSearchApp`

The class groups the state of one interactive session with the operations that use that state. This is the OOP part of the program: the object owns its records, filters, ratings, and latest results, instead of keeping those values as unrelated local variables in a large function.

Класс объединяет состояние одного интерактивного сеанса и операции, которые это состояние используют. Это объектно-ориентированная часть программы: объект владеет записями, фильтрами, оценками и последней выдачей, а не хранит эти значения как несвязанные локальные переменные внутри одной большой функции.

### `__init__(self, variant_name)`

The constructor selects configuration from `VARIANTS` and initializes the session:

- `self.variant`: settings for the chosen dataset.
- `self.records`: loaded rows.
- `self.filters`: active filter tuples.
- `self.ratings`: mapping from record ID to integer rating.
- `self.last_results`: records in the most recently displayed search results.

Конструктор выбирает настройки из `VARIANTS` и инициализирует сеанс:

- `self.variant`: настройки выбранного набора данных.
- `self.records`: загруженные строки.
- `self.filters`: активные кортежи фильтров.
- `self.ratings`: соответствие ID записи целочисленной оценке.
- `self.last_results`: записи из последней показанной поисковой выдачи.

`self` means “this particular app object.” Both variants use the same class, but separate app objects have separate state.

`self` означает «этот конкретный объект приложения». Оба варианта используют один класс, но у каждого объекта своё состояние.

### `run(self) -> None`

Starts the interactive loop. It reads a line, parses it with `shlex.split`, skips blank input, and passes parsed words to `execute`. `EOFError` (for example, Ctrl+D/Ctrl+Z) exits cleanly. Parsing errors and expected command/file errors are printed, and the loop continues.

Запускает интерактивный цикл. Он считывает строку, разбирает её через `shlex.split`, пропускает пустой ввод и передаёт разобранные слова в `execute`. `EOFError` (например, Ctrl+D/Ctrl+Z) завершает работу корректно. Ошибки разбора, команд и файлов выводятся пользователю, после чего цикл продолжается.

### `execute(self, parts) -> bool`

Dispatches one parsed command to the matching method. For example, `search "red bird"` becomes `parts == ["search", "red bird"]` and calls `self.search("red bird")`. It returns `False` only for the `exit` command; `run` uses that value to stop the loop.

Направляет одну разобранную команду в соответствующий метод. Например, `search "red bird"` превращается в `parts == ["search", "red bird"]` и вызывает `self.search("red bird")`. Только команда `exit` приводит к возврату `False`; `run` использует это значение для остановки цикла.

### `show_help()`

This is a `@staticmethod` because it does not read or modify object state. It prints the command syntax. A static method belongs to the class namespace but does not receive `self`.

Это `@staticmethod`, потому что метод не читает и не меняет состояние объекта. Он выводит синтаксис команд. Статический метод принадлежит пространству имён класса, но не получает `self`.

### `load(self, filename)`

Uses the variant's default CSV when `filename` is `None`; otherwise it uses the supplied path. Relative paths are interpreted from the current working directory. After successful loading it clears filters, ratings, and prior results, as required when a new dataset is loaded.

Использует CSV из настроек варианта, если `filename` равен `None`; иначе использует переданный путь. Относительные пути разрешаются относительно текущего каталога. После успешной загрузки очищаются фильтры, оценки и предыдущая выдача, как требуется при загрузке нового набора данных.

### `show_records(self)`

Prints a message if no records are loaded; otherwise prints the count and every record card, with no search or result limit.

Если данные не загружены, выводит сообщение. Иначе показывает количество записей и каждую карточку без поиска и ограничения числа результатов.

### `show_fields(self)`

Infers a display type for each column from the first nonempty value: `true`/`false` means Boolean, a value accepted by `float(...)` means numeric, otherwise string. It then prints the filter operators shown for that field.

Определяет отображаемый тип столбца по первому непустому значению: `true`/`false` означает логический тип, значение, принимаемое функцией `float(...)`, — числовой, иначе — строковый. Затем выводит поддерживаемые для поля операторы фильтра.

This is type inference for the `fields` display, not a permanent schema. Actual comparisons are still performed by `value_for_filter` and `apply_filters`.

Это определение типа для отображения команды `fields`, а не постоянная схема данных. Реальные сравнения выполняют `value_for_filter` и `apply_filters`.

### `handle_filter(self, args)`

Handles the four filter subcommands:

- `add`: checks that data is loaded and the field exists, then appends a tuple to `self.filters`.
- `list`: prints filters with numbering starting at 1.
- `remove`: converts the user's 1-based number to a Python 0-based index, validates it, then removes that filter.
- `clear`: empties the active filter list.

Обрабатывает четыре подкоманды фильтра:

- `add`: проверяет, что данные загружены и поле существует, затем добавляет кортеж в `self.filters`.
- `list`: выводит фильтры с нумерацией от 1.
- `remove`: переводит номер пользователя с нумерацией от 1 в индекс Python с нумерацией от 0, проверяет его и удаляет фильтр.
- `clear`: очищает список активных фильтров.

### `search(self, query)`

This is the main search operation:

1. It requires loaded records and starts a timer.
2. It normalizes the query and makes a `set` of its words. A set removes duplicates.
3. For each record, it first calls `apply_filters`; records that fail a filter are skipped.
4. It normalizes the title into `title_tokens`.
5. For a nonempty query, `query_tokens.issubset(set(title_tokens))` implements `words-all`: every distinct query word must occur in the title.
6. Relevance is the sum of the occurrence counts of the distinct query words in the title. With an empty query, relevance is zero.
7. It sorts by descending final score, then descending relevance, then title alphabetically. Airports use `relevance + rating * 0.5` as final score; artworks use relevance alone.
8. It applies the configured result limit: 10 for airports and no limit for artworks.
9. It stores the displayed records in `self.last_results`, prints each card and the airports scores, then prints elapsed time in milliseconds.

Это основная операция поиска:

1. Проверяет, что записи загружены, и запускает таймер.
2. Нормализует запрос и создаёт множество (`set`) его слов. Множество удаляет повторы.
3. Для каждой записи сначала вызывает `apply_filters`; записи, не прошедшие фильтр, пропускаются.
4. Нормализует заголовок в `title_tokens`.
5. Для непустого запроса выражение `query_tokens.issubset(set(title_tokens))` реализует `words-all`: каждое уникальное слово запроса должно быть в заголовке.
6. Релевантность — сумма числа вхождений уникальных слов запроса в заголовок. Для пустого запроса релевантность равна нулю.
7. Сортирует по убыванию итогового балла, затем релевантности, затем по алфавиту заголовка. Для аэропортов итоговый балл равен `релевантность + оценка * 0.5`; для картин учитывается только релевантность.
8. Применяет ограничение числа результатов: 10 для аэропортов и без ограничения для картин.
9. Сохраняет показанные записи в `self.last_results`, выводит карточки и баллы аэропортов, затем время поиска в миллисекундах.

Because ratings are used only after a record matches the query and filters, a rating cannot add a nonmatching record to the result set.

Поскольку оценки учитываются только после совпадения записи с запросом и фильтрами, оценка не может добавить в выдачу запись, которая не подходит под условия.

### `save(self, filename)`

Writes the records in `self.last_results` to a UTF-8 text file, rendering each card without search highlighting. It saves the last *displayed* results, not every match hidden by the top-10 limit.

Записывает `self.last_results` в текстовый файл UTF-8, формируя карточки без подсветки поиска. Сохраняется последняя *показанная* выдача, а не все совпадения, скрытые ограничением top-10.

### `rate(self, record_id, raw_rating)`

Rejects rating commands when the variant has no rating mode. Converts the rating to an integer, enforces the inclusive range 1–5, and requires the ID to be in `self.last_results`. It then stores/replaces the rating in `self.ratings`.

Отклоняет команду оценки, если для варианта оценки отключены. Преобразует значение в целое число, проверяет диапазон от 1 до 5 включительно и требует, чтобы ID был в `self.last_results`. Затем сохраняет или заменяет оценку в `self.ratings`.

### `show_ratings(self)`

Rejects the command if ratings are disabled. Otherwise it prints “No ratings” for an empty map, or prints each ID and rating in sorted ID order.

Отклоняет команду, если оценки отключены. Иначе выводит `No ratings` для пустого словаря или печатает ID и оценки, отсортированные по ID.

---

## 5. Entry point / Точка входа

### `main()`

Creates an `ArgumentParser`, offers `--variant` choices from the keys of `VARIANTS`, defaults to `airports`, creates `CatalogSearchApp`, and starts its `run()` method.

Создаёт `ArgumentParser`, предлагает варианты `--variant` из ключей `VARIANTS`, задаёт `airports` по умолчанию, создаёт объект `CatalogSearchApp` и запускает его метод `run()`.

### `if __name__ == "__main__":`

This guard calls `main()` only when `main.py` is run directly. If another Python file imports it, the interactive program does not start automatically.

Эта проверка вызывает `main()` только при непосредственном запуске `main.py`. Если другой Python-файл импортирует этот модуль, интерактивная программа автоматически не запускается.

---

## 6. Important Python ideas / Важные понятия Python

| Idea | In this program |
| --- | --- |
| Object / Объект | `CatalogSearchApp(...)` stores the state of one session. / Хранит состояние одного сеанса. |
| Attribute / Атрибут | `self.records`, `self.filters`, `self.ratings`, `self.last_results`. / Поля объекта. |
| Method / Метод | `search`, `load`, `rate`, etc. operate on `self`. / Операции объекта, работающие с `self`. |
| Pure-ish helper / Функция-помощник | `normalize`, `read_csv`, `render_record` receive arguments and return values without changing app state. / Получают аргументы и возвращают результат без изменения состояния приложения. |
| List / Список | Ordered collection of records or filters. / Упорядоченный набор записей или фильтров. |
| Dictionary / Словарь | A CSV row, configuration, or ID-to-rating mapping. / Строка CSV, конфигурация или соответствие ID-оценке. |
| Set / Множество | Unique query words and fast membership checks. / Уникальные слова запроса и быстрая проверка вхождения. |
| Tuple / Кортеж | One filter `(field, operator, value)`. / Один фильтр. |
| Exception / Исключение | Reports input, conversion, or file errors without crashing the loop. / Сообщает об ошибках ввода, преобразования или файла без падения цикла. |

---

## 7. Defense questions / Вопросы на защите

### Why use a class here? / Зачем здесь класс?

**EN:** The app has persistent state across commands. The class keeps that state together with the methods that update it, so `load`, `search`, and `rate` work with the same records, filters, and ratings.

**RU:** Приложение хранит состояние между командами. Класс объединяет это состояние с методами, которые его меняют, поэтому `load`, `search` и `rate` работают с одними и теми же записями, фильтрами и оценками.

### What does `self` mean? / Что означает `self`?

**EN:** `self` is the current `CatalogSearchApp` object. `self.records` is the records belonging to that session, not a global list shared by every app object.

**RU:** `self` — текущий объект `CatalogSearchApp`. `self.records` — записи именно этого сеанса, а не глобальный список, общий для всех объектов.

### How does `words-all` work? / Как работает `words-all`?

**EN:** The normalized query becomes a set of words. A title matches when that set is a subset of the title's word set. Therefore all distinct query words must occur in the title; their order does not matter.

**RU:** Нормализованный запрос превращается в множество слов. Заголовок подходит, когда это множество является подмножеством множества слов заголовка. Значит, в заголовке должны присутствовать все уникальные слова запроса; их порядок не важен.

### How is relevance different from the boost? / Чем релевантность отличается от boost?

**EN:** Relevance measures query-word occurrences in the title. The airports boost adds half a point per rating star to create the final sorting score. The displayed relevance remains separate from the rating and final score.

**RU:** Релевантность измеряет число вхождений слов запроса в заголовок. Для аэропортов boost добавляет по половине балла за звезду оценки и формирует итоговый балл сортировки. Релевантность отдельно показывается от оценки и итогового балла.

### Why normalize both query and title? / Зачем нормализовать и запрос, и заголовок?

**EN:** It makes comparison consistent. For example, case and punctuation differences do not prevent a match, and combining accent marks are ignored.

**RU:** Это обеспечивает одинаковые правила сравнения. Различия в регистре и пунктуации не мешают совпадению, а комбинируемые диакритические знаки игнорируются.

### When are filters applied? / Когда применяются фильтры?

**EN:** Before the query match is added to the results, and before the result limit is applied. Every active filter must pass.

**RU:** До добавления совпадения в результаты и до ограничения их количества. Запись должна пройти все активные фильтры.

### What is stored in `last_results`? / Что хранится в `last_results`?

**EN:** The records actually displayed by the most recent search after sorting and limiting. `rate` uses this list to restrict ratings to visible results, and `save` writes it to a file.

**RU:** Записи, которые действительно показал последний поиск после сортировки и ограничения. `rate` использует этот список, чтобы разрешать оценку показанных результатов, а `save` записывает его в файл.

### What happens when a new file is loaded? / Что происходит при загрузке нового файла?

**EN:** The new records replace the old ones, and filters, ratings, and last results are cleared so state from the previous dataset cannot leak into the new one.

**RU:** Новые записи заменяют старые, а фильтры, оценки и последняя выдача очищаются, чтобы состояние прежнего набора данных не влияло на новый.

---

## 8. Details to be ready to explain / Детали, о которых стоит помнить

- The program searches **only `title`**, even though `show` displays all fields. This matches the assigned `title` field setting. / Поиск выполняется **только по `title`**, хотя `show` показывает все поля. Это соответствует варианту с полем `title`.
- Query words are stored in a set, so repeated query words count once for matching and relevance. / Слова запроса хранятся в множестве, поэтому повторы учитываются один раз и при совпадении, и при расчёте релевантности.
- The relevance score counts occurrences, not a normalized 0–1 similarity. / Релевантность считает вхождения, а не нормализованное сходство от 0 до 1.
- Ratings live only in memory; they are lost on program exit or a new load. / Оценки хранятся только в памяти и теряются при выходе или новой загрузке.
- A title with repeated query words can receive greater relevance. / Заголовок с повторяющимися словами запроса получает большую релевантность.
- `show_fields` infers types from sample data for display. The filter implementation itself converts values dynamically. / `show_fields` определяет типы по данным для отображения. Сама фильтрация преобразует значения динамически.

---

## 9. One-minute summary / Краткий ответ на минуту

**EN:** “The program is an interactive catalog search app. `CatalogSearchApp` owns the loaded records, active filters, ratings, and last results. CSV rows are dictionaries. Before matching, query words and titles are normalized with Unicode case folding, diacritic removal, and punctuation splitting. Search implements `words-all` over titles, computes relevance from word occurrences, applies filters, sorts results, and then uses a ten-result limit for airports. Airport ratings add `rating × 0.5` to the sorting score. The artworks variant has no ratings or result limit. Helper functions handle parsing, normalization, filtering, highlighting, and card rendering.”

**RU:** «Это интерактивная программа для поиска по каталогу. `CatalogSearchApp` хранит загруженные записи, активные фильтры, оценки и последнюю выдачу. Строки CSV представлены словарями. Перед сравнением запрос и заголовки нормализуются: регистр приводится к общему виду, диакритика удаляется, пунктуация разделяет слова. Поиск реализует `words-all` по заголовку, считает релевантность по количеству вхождений, применяет фильтры, сортирует результаты и ограничивает выдачу десятью записями для аэропортов. Оценка аэропорта добавляет `rating × 0.5` к баллу сортировки. Для картин оценки отключены и лимита нет. Вспомогательные функции выполняют разбор CSV, нормализацию, фильтрацию, подсветку и формирование карточек».
