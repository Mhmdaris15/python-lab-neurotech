# Lab 1: Catalog Search

Write a command-line program for searching a catalog. Run it with `python main.py`; it accepts commands and exits when given the `exit` command.

## Variant

The program parameters are specified by your assigned variant:

```text
dataset | fields | processing | search | results | highlighting | ratings
```


| Parameter | Values                                                                                                                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dataset   | `books-json` — books; `artworks-csv` — art; `airports-csv` — airports; `earthquakes-jsonl` — earthquakes; `chess-json` — chess openings; `exoplanets-csv` — exoplanets; `papers-jsonl` — papers |
| Fields    | `title` — title; `all` — all available text fields                                                                                                                                               |
| Processing| `raw` — unchanged; `fold` — case-insensitive; `clean` — custom normalization                                                                                                                      |
| Search    | `substr` — substring; `words-all` — all words; `words-any` — any word; `fuzzy-words` — all words with typos; `fuzzy-text` — typo-tolerant similarity against the whole field text                 |
| Results   | `ranked` — all matches by relevance; `top10` — up to the ten best; `best` — the single best match                                                                                                |
| Highlight | `plain` — no highlighting; `mark` — highlight matches in any visible way                                                                                                                         |
| Rating    | `none` — no ratings; `stars` — rate records from 1 to 5; `boost` — ratings also affect result order                                                                                               |


For `clean`, choose your own normalization rules. Process the query and record text the same way.

## Output

`show` displays every loaded record with all fields, without filters or a result limit. Choose any output format, such as a table or cards.

`search` displays records in the same format as `show`, but only those matching the query and filters. Also show relevance, the user's rating in `stars` and `boost` modes, and the final score in `boost` mode. Report the number of matching and displayed records and the search time. In `mark` mode, highlight matches in the relevant card fields.

## Relevance and ratings

Calculate relevance from the query and record text. In `none` and `stars` modes, sort records by descending relevance. Choose a formula and describe it in your report.

For approximate search, choose a string similarity measure from 0 to 1, where 1 means an exact match. `threshold` sets the minimum acceptable similarity. Relevance and similarity may use different formulas.

The user assigns a rating from 1 to 5 with the `rate` command. In `stars` mode, store and display it. In `boost` mode, it adds to relevance for sorting; describe the boost formula in your report. Display relevance, rating, and final score separately. A rating must not add a record that does not match the query or filters.

## Commands


| Command                                   | Action                                                                  |
| ----------------------------------------- | ----------------------------------------------------------------------- |
| `help`                                    | List commands                                                           |
| `load <file>`                             | Load data; reset filters, threshold, last results, and ratings          |
| `show`                                    | Display all records as cards                                            |
| `fields`                                  | Show fields, types, and allowed filters                                 |
| `filter add <field> <operator> <value>`   | Add a condition                                                         |
| `filter list`                             | List conditions, numbered starting at 1                                 |
| `filter remove <number>`                  | Remove a condition and renumber the rest                                |
| `filter clear`                            | Remove all conditions                                                   |
| `threshold <number>`                      | Set threshold in (0, 1]; approximate search only                        |
| `search "<query>"`                        | Display search results; an empty query applies only filters              |
| `save <file>`                             | Save the last displayed results to a text file                          |
| `rate <id> <1..5>`                        | Rate a record in the last results; `stars` and `boost` only              |
| `ratings`                                 | Show ratings; `stars` and `boost` only                                   |
| `exit`                                    | Exit the program                                                        |




## Filters


| Operator   | Meaning        |
| ---------- | -------------- |
| `eq`       | Equal          |
| `ne`       | Not equal      |
| `lt`       | Less than      |
| `le`       | Less than or equal |
| `gt`       | Greater than   |
| `ge`       | Greater than or equal |
| `contains` | Contains text  |


- Numeric fields support `eq`, `ne`, `lt`, `le`, `gt`, `ge`.
- String fields support `eq`, `ne`, `contains`.
- Boolean fields support `eq`, `ne`; values are `true` and `false`.
- All filters are applied together, before limiting the number of results. Empty fields do not pass a filter.
- Setting changes take effect on the next `search`.



## General requirements

- Before data is loaded, only `help`, `load`, and `exit` are available.
- Put arguments containing spaces in quotes.
- A command error should display a clear message and must not terminate the program.
- Keep ratings in memory until exit or the next load. Associate them with IDs and retain them when the query changes. A new rating replaces the previous one.



## Example session

Variant: `airports-csv | all | fold | words-all | top10 | mark | boost`. The file `airports.csv` contains four records; `show` displays them in full.

```text
$ python main.py
Catalog search. Commands: help. Exit: exit.


# Load: each record is displayed as a card with all fields.

search> load airports.csv
Loaded records: 4

search> fields
Search fields: title, city, keywords

Field         Type   Filters
------------  -----  -----------------
id            str    -
title         str    -
city          str    -
keywords      str    -
country       str    eq ne contains
kind          str    eq ne contains
elevation_ft  float  eq ne lt le gt ge
latitude      float  eq ne lt le gt ge
longitude     float  eq ne lt le gt ge
scheduled     bool   eq ne
url           str    -

eq = equal; ne = not equal; contains = contains text.
lt <; le <=; gt >; ge >=. true = yes; false = no.

search> show
Records: 4

[KBOS] Boston Logan International Airport
  city: Boston
  keywords: General Edward Lawrence Logan International Airport
  country: US
  kind: large_airport
  elevation_ft: 20.0
  latitude: 42.36197
  longitude: -71.0079
  scheduled: true
  url: https://ourairports.com/airports/KBOS/

[NH60] Huff Memorial Airport
  city: New Boston
  keywords: —
  country: US
  kind: small_airport
  elevation_ft: 840.0
  latitude: 42.958877
  longitude: -71.653126
  scheduled: false
  url: https://ourairports.com/airports/NH60/

[US-0960] Tufts Medical Center Heliport
  city: Boston
  keywords: —
  country: US
  kind: heliport
  elevation_ft: 230.0
  latitude: 42.349037
  longitude: -71.063223
  scheduled: false
  url: https://ourairports.com/airports/US-0960/

[EGTE] Exeter International Airport
  city: Exeter, Devon
  keywords: —
  country: GB
  kind: medium_airport
  elevation_ft: 102.0
  latitude: 50.734261
  longitude: -3.413984
  scheduled: true
  url: https://ourairports.com/airports/EGTE/


# Case-insensitive search; matches are highlighted [[like this]].

search> search "bOsToN"
Found: 3; displayed: 3

[KBOS] [[Boston]] Logan International Airport
  city: [[Boston]]
  keywords: General Edward Lawrence Logan International Airport
  country: US
  kind: large_airport
  elevation_ft: 20.0
  latitude: 42.36197
  longitude: -71.0079
  scheduled: true
  url: https://ourairports.com/airports/KBOS/
  Релевантность: 4.00
  Оценка: нет
  Баллы: 4.00

[NH60] Huff Memorial Airport
  city: New [[Boston]]
  keywords: —
  country: US
  kind: small_airport
  elevation_ft: 840.0
  latitude: 42.958877
  longitude: -71.653126
  scheduled: false
  url: https://ourairports.com/airports/NH60/
  Релевантность: 1.00
  Оценка: нет
  Баллы: 1.00

[US-0960] Tufts Medical Center Heliport
  city: [[Boston]]
  keywords: —
  country: US
  kind: heliport
  elevation_ft: 230.0
  latitude: 42.349037
  longitude: -71.063223
  scheduled: false
  url: https://ourairports.com/airports/US-0960/
  Релевантность: 1.00
  Оценка: нет
  Баллы: 1.00

Время поиска: 0.04 мс


# Оставим аэропорты США без регулярных рейсов.

search> filter add country eq US
Добавлен фильтр 1: country = US

search> filter add scheduled eq false
Добавлен фильтр 2: scheduled = false

search> filter list
1. country = US
2. scheduled = false

search> search "Boston"
Найдено: 2; показано: 2

[NH60] Huff Memorial Airport
  city: New [[Boston]]
  keywords: —
  country: US
  kind: small_airport
  elevation_ft: 840.0
  latitude: 42.958877
  longitude: -71.653126
  scheduled: false
  url: https://ourairports.com/airports/NH60/
  Релевантность: 1.00
  Оценка: нет
  Баллы: 1.00

[US-0960] Tufts Medical Center Heliport
  city: [[Boston]]
  keywords: —
  country: US
  kind: heliport
  elevation_ft: 230.0
  latitude: 42.349037
  longitude: -71.063223
  scheduled: false
  url: https://ourairports.com/airports/US-0960/
  Релевантность: 1.00
  Оценка: нет
  Баллы: 1.00

Время поиска: 0.02 мс


# Ошибка не завершает программу. Оценка меняет порядок, но не релевантность.

search> rate US-0960 6
Ошибка: Оценка должна быть целым числом от 1 до 5

search> rate US-0960 5
Оценка: US-0960 — 5/5

search> ratings
US-0960: 5/5

search> search "Boston"
Найдено: 2; показано: 2

[US-0960] Tufts Medical Center Heliport
  city: [[Boston]]
  keywords: —
  country: US
  kind: heliport
  elevation_ft: 230.0
  latitude: 42.349037
  longitude: -71.063223
  scheduled: false
  url: https://ourairports.com/airports/US-0960/
  Релевантность: 1.00
  Оценка: 5/5
  Баллы: 3.50

[NH60] Huff Memorial Airport
  city: New [[Boston]]
  keywords: —
  country: US
  kind: small_airport
  elevation_ft: 840.0
  latitude: 42.958877
  longitude: -71.653126
  scheduled: false
  url: https://ourairports.com/airports/NH60/
  Релевантность: 1.00
  Оценка: нет
  Баллы: 1.00

Время поиска: 0.01 мс

search> save result.txt
Сохранено: result.txt


# show по-прежнему выводит весь файл, даже при активных фильтрах.

search> show
Записей: 4

[KBOS] Boston Logan International Airport
  city: Boston
  keywords: General Edward Lawrence Logan International Airport
  country: US
  kind: large_airport
  elevation_ft: 20.0
  latitude: 42.36197
  longitude: -71.0079
  scheduled: true
  url: https://ourairports.com/airports/KBOS/

[NH60] Huff Memorial Airport
  city: New Boston
  keywords: —
  country: US
  kind: small_airport
  elevation_ft: 840.0
  latitude: 42.958877
  longitude: -71.653126
  scheduled: false
  url: https://ourairports.com/airports/NH60/

[US-0960] Tufts Medical Center Heliport
  city: Boston
  keywords: —
  country: US
  kind: heliport
  elevation_ft: 230.0
  latitude: 42.349037
  longitude: -71.063223
  scheduled: false
  url: https://ourairports.com/airports/US-0960/

[EGTE] Exeter International Airport
  city: Exeter, Devon
  keywords: —
  country: GB
  kind: medium_airport
  elevation_ft: 102.0
  latitude: 50.734261
  longitude: -3.413984
  scheduled: true
  url: https://ourairports.com/airports/EGTE/


# Удалим второй фильтр. Пустой запрос оставляет только фильтрацию.

search> filter remove 2
Фильтр удалён

search> filter list
1. country = US

search> search ""
Найдено: 3; показано: 3

[US-0960] Tufts Medical Center Heliport
  city: Boston
  keywords: —
  country: US
  kind: heliport
  elevation_ft: 230.0
  latitude: 42.349037
  longitude: -71.063223
  scheduled: false
  url: https://ourairports.com/airports/US-0960/
  Релевантность: 0.00
  Оценка: 5/5
  Баллы: 2.50

[KBOS] Boston Logan International Airport
  city: Boston
  keywords: General Edward Lawrence Logan International Airport
  country: US
  kind: large_airport
  elevation_ft: 20.0
  latitude: 42.36197
  longitude: -71.0079
  scheduled: true
  url: https://ourairports.com/airports/KBOS/
  Релевантность: 0.00
  Оценка: нет
  Баллы: 0.00

[NH60] Huff Memorial Airport
  city: New Boston
  keywords: —
  country: US
  kind: small_airport
  elevation_ft: 840.0
  latitude: 42.958877
  longitude: -71.653126
  scheduled: false
  url: https://ourairports.com/airports/NH60/
  Релевантность: 0.00
  Оценка: нет
  Баллы: 0.00

Время поиска: 0.01 мс


# Очистим фильтры и выполним запрос без совпадений.

search> filter clear
Фильтры удалены

search> search "Atlantis"
Найдено: 0; показано: 0

Время поиска: 0.01 мс


# Новая загрузка сбрасывает оценки и настройки.

search> load airports.csv
Загружено записей: 4

search> ratings
Оценок нет

search> filter list
Фильтров нет

search> exit
```



## Report

Submit the lab report (`README.md` and project files) **in the `lab1` directory of your own homework repository**, alongside `01_Basic`, `02_Data_Structures`, and so on (`student-xxx`).
