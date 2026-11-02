# Lab 1 defense preparation

This guide is for the airport variant only:

`airports-csv | title | clean | words-all | top10 | mark | boost`

Это пособие только для варианта с аэропортами:

`airports-csv | title | clean | words-all | top10 | mark | boost`

## 1. Short presentation in English

> My program is an interactive search tool for an airport catalog stored in a CSV file. It searches airport titles using the `words-all` method. Before matching, it case-folds text, removes diacritic marks, and treats punctuation as a word separator. Every distinct query word must occur in a title. Relevance is the number of occurrences of those words. The program applies filters before sorting and displays up to ten results. It highlights matched title words with double brackets. A user can rate a displayed airport from one to five; each rating point adds 0.5 to the sorting score. The program is implemented as a `CatalogSearchApp` class with separate helper functions for normalization, CSV reading, filtering, highlighting, and rendering.

## 1. Краткое выступление на русском

> Моя программа — интерактивный поиск по каталогу аэропортов, который хранится в CSV-файле. Поиск выполняется по названиям методом `words-all`. Перед сравнением программа приводит текст к общему регистру, удаляет диакритические знаки и считает пунктуацию разделителем слов. В названии должны присутствовать все уникальные слова запроса. Релевантность равна сумме вхождений этих слов. Программа применяет фильтры до сортировки и показывает не более десяти результатов. Совпавшие слова в названии выделяются двойными скобками. Пользователь может оценить показанный аэропорт от одного до пяти; каждый балл оценки добавляет 0,5 к баллу сортировки. Программа реализована классом `CatalogSearchApp`, а нормализация, чтение CSV, фильтрация, подсветка и формирование карточек вынесены во вспомогательные функции.

## 2. Demonstration flow / План демонстрации

Run these commands from the `lab1` directory. / Выполняйте команды из каталога `lab1`.

```text
python main.py
load
fields
search "airport"
```

The default variant is airports. `load` without a path loads the bundled airport dataset. `fields` lists its columns. Choose an ID actually shown in the search output before trying `rate`:

Вариант аэропортов используется по умолчанию. Команда `load` без пути загружает набор аэропортов из проекта. `fields` показывает столбцы. Перед командой `rate` возьмите ID, который действительно есть в показанной выдаче:

```text
rate <ID_FROM_RESULTS> 5
search "airport"
ratings
save results.txt
```

The second search shows the rating's effect on order and score. `show` prints every airport (8,000 records), so it may produce a lot of output. / Повторный поиск показывает влияние оценки на порядок и итоговый балл. `show` выводит все 8 000 аэропортов, поэтому команда может создать очень большой вывод.

## 3. Questions you may be asked / Возможные вопросы

### What does OOP mean in your implementation? / Где в программе ООП?

**EN:** `CatalogSearchApp` is the main object. It stores session state in attributes: the chosen variant, records, active filters, ratings, and last results. Its methods operate on that same state. The helper functions are separate because they transform data without needing access to the session object.

**RU:** Основной объект — `CatalogSearchApp`. Он хранит состояние сеанса в атрибутах: выбранный вариант, записи, активные фильтры, оценки и последнюю выдачу. Методы работают с этим же состоянием. Вспомогательные функции отделены, поскольку преобразуют данные и не нуждаются в доступе к объекту сеанса.

### What is `self`? / Что такое `self`?

**EN:** `self` refers to the current `CatalogSearchApp` instance. For example, `self.records` is the list of records owned by this particular application session.

**RU:** `self` ссылается на текущий экземпляр `CatalogSearchApp`. Например, `self.records` — список записей, принадлежащий именно этому сеансу приложения.

### How does `clean` work? / Как работает `clean`?

**EN:** `normalize` case-folds the text, applies Unicode NFKD decomposition, removes combining marks, extracts word sequences with a regular expression, and joins the words with spaces. The same function processes both query and title, so they can be compared consistently.

**RU:** `normalize` приводит текст к общему регистру, выполняет Unicode-разложение NFKD, удаляет комбинируемые знаки, извлекает слова регулярным выражением и соединяет их пробелами. Одна и та же функция применяется и к запросу, и к названию, чтобы сравнение было последовательным.

### How does `words-all` work? / Как работает `words-all`?

**EN:** The query is normalized and converted to a set. A record matches when the query-word set is a subset of the title-word set. Every distinct query word must be present, but the order of words does not matter.

**RU:** Запрос нормализуется и преобразуется в множество. Запись подходит, если множество слов запроса является подмножеством множества слов названия. Должны присутствовать все уникальные слова, но порядок слов не важен.

### How do you calculate relevance? / Как считается релевантность?

**EN:** For each distinct query word, the program counts how many times it appears in the normalized title, then adds those counts. Repeated words in the query count only once because the query is stored in a set.

**RU:** Для каждого уникального слова запроса программа считает количество его вхождений в нормализованном названии, затем складывает эти количества. Повторяющиеся слова в запросе считаются один раз, так как запрос хранится в множестве.

### How does the rating boost work? / Как работает boost рейтинга?

**EN:** The final sorting score is `relevance + 0.5 * rating`. A rating of 5 adds 2.5 points. An unrated record gets no boost. Ratings are applied only to records that already matched the query and filters.

**RU:** Итоговый балл сортировки равен `релевантность + 0,5 * оценка`. Оценка 5 добавляет 2,5 балла. Неоценённая запись не получает прибавки. Оценки учитываются только для записей, уже совпавших с запросом и прошедших фильтры.

### When are filters applied? / Когда применяются фильтры?

**EN:** The program applies all active filters to each record before matching and before the top-10 cut. Filters use AND logic: every condition must pass.

**RU:** Программа применяет все активные фильтры к каждой записи до поиска и до ограничения top-10. Условия соединяются логическим И: должны пройти все фильтры.

### What does `last_results` store? / Что хранит `last_results`?

**EN:** It stores the records actually displayed by the latest search, after sorting and limiting. The `rate` command uses it to restrict ratings to visible records, and `save` writes it to a text file.

**RU:** В нём хранятся записи, действительно показанные последним поиском после сортировки и ограничения. `rate` использует этот список, чтобы разрешать оценку только видимых записей, а `save` записывает его в текстовый файл.

### What happens when you load another file? / Что произойдёт при загрузке другого файла?

**EN:** The records are replaced, and filters, ratings, and last results are cleared. Ratings are kept only in memory and are also lost when the program exits.

**RU:** Записи заменяются, а фильтры, оценки и последняя выдача очищаются. Оценки хранятся только в памяти и также теряются при завершении программы.

### Why does `show` print so much? / Почему `show` выводит так много?

**EN:** `show` is defined to display the complete loaded catalog without filters or a result limit. The airport data contains 8,000 records. Search is the command intended for a smaller, filtered result list.

**RU:** По условию `show` выводит весь загруженный каталог без фильтров и ограничения количества. В наборе аэропортов 8 000 записей. Для меньшей отфильтрованной выдачи предназначена команда `search`.

## 4. Key methods / Основные методы

| Method | Defense explanation (EN) | Объяснение для защиты (RU) |
| --- | --- | --- |
| `__init__` | Selects a variant and initializes session state. | Выбирает вариант и инициализирует состояние сеанса. |
| `run` | Reads and parses commands in a loop; catches expected errors. | Считывает и разбирает команды в цикле; перехватывает ожидаемые ошибки. |
| `execute` | Dispatches a parsed command to the appropriate method. | Направляет разобранную команду в нужный метод. |
| `load` | Reads CSV and resets filters, ratings, and previous results. | Читает CSV и сбрасывает фильтры, оценки и прошлую выдачу. |
| `show_records` | Displays every loaded record. | Показывает все загруженные записи. |
| `show_fields` | Infers and prints a type and filter operators per column. | Определяет и выводит тип и операторы фильтра для каждого столбца. |
| `handle_filter` | Adds, lists, removes, or clears filter conditions. | Добавляет, показывает, удаляет или очищает условия фильтрации. |
| `search` | Filters, matches, ranks, limits, highlights, and displays results. | Фильтрует, ищет, ранжирует, ограничивает, подсвечивает и показывает результаты. |
| `save` | Writes the last displayed results to UTF-8 text. | Записывает последнюю показанную выдачу в UTF-8 файл. |
| `rate` / `show_ratings` | Stores and lists ratings when the variant supports them. | Сохраняет и показывает оценки, если вариант их поддерживает. |

Helper functions / Вспомогательные функции:

- `normalize`: cleans text consistently. / Одинаково нормализует текст.
- `read_csv`: turns CSV rows into dictionaries. / Преобразует строки CSV в словари.
- `value_for_filter` and `apply_filters`: convert and compare filter values. / Преобразуют значения и применяют фильтры.
- `highlight`: marks matching words in their original spelling. / Подсвечивает совпавшие слова, сохраняя написание.
- `render_record`: formats one record as a card. / Форматирует одну запись как карточку.
- `main`: parses `--variant`, creates the app object, and starts it. / Разбирает `--variant`, создаёт объект приложения и запускает его.

## 5. Things to state accurately / Что важно объяснять точно

- The program searches only the `title` field; `show` displays all fields. / Поиск выполняется только по `title`; `show` показывает все поля.
- Relevance counts occurrences; it is not a normalized similarity between 0 and 1. / Релевантность считает вхождения; это не нормализованная метрика сходства от 0 до 1.
- The rating changes ordering, but does not make a non-match eligible. / Оценка меняет порядок, но не добавляет неподходящую запись.
- Ratings are temporary and reset on load. / Оценки временные и очищаются при загрузке.
- `show_fields` infers column types from sample values for display. / `show_fields` определяет типы столбцов по значениям для отображения.
- If asked about testing, describe only commands you actually ran. Do not claim an automated test suite passed unless you ran it. / Если спросят о тестировании, рассказывайте только о командах, которые действительно запускали. Не утверждайте, что автоматические тесты прошли, если вы их не запускали.

## 6. Final 20-second answer / Итоговый ответ на 20 секунд

**EN:** “I built an OOP command-line search app for the airport CSV. It normalizes query words and titles, applies all-word matching and filters, ranks by title relevance plus an optional rating boost, and displays up to ten highlighted results. The class owns state across commands, while helper functions handle text and record transformations.”

**RU:** «Я реализовал объектно-ориентированное консольное приложение для поиска по CSV аэропортов. Оно нормализует запрос и названия, ищет по всем словам и применяет фильтры, сортирует по релевантности названия с возможной прибавкой рейтинга и показывает до десяти подсвеченных результатов. Класс хранит состояние между командами, а вспомогательные функции обрабатывают текст и записи».
