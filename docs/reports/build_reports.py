"""Build separate English and Russian DOCX reports from verified lab results.

Uses the existing Demandlane environment. Run from any working directory.
"""

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = json.loads((ROOT / "lab2/results/summary.json").read_text(encoding="utf-8"))
METRICS = json.loads((ROOT / "lab3/results/metrics.json").read_text(encoding="utf-8"))
CHECKS = json.loads((ROOT / "docs/reports/lab1_checks.json").read_text(encoding="utf-8"))


class Report:
    def __init__(self, lab, language, topic):
        self.lab = lab
        self.language = language
        self.doc = Document()
        section = self.doc.sections[0]
        section.page_width, section.page_height = Cm(21), Cm(29.7)
        section.top_margin = section.bottom_margin = Cm(1.9)
        section.left_margin, section.right_margin = Cm(2.3), Cm(1.9)
        section.different_first_page_header_footer = True
        normal = self.doc.styles["Normal"]
        normal.font.name = "Calibri"
        normal.font.size = Pt(11)
        normal.paragraph_format.line_spacing = 1.08
        normal.paragraph_format.space_after = Pt(6)
        for name, size in [("Title", 24), ("Heading 1", 15), ("Heading 2", 12)]:
            style = self.doc.styles[name]
            style.font.name = "Calibri"
            style.font.size = Pt(size)
            style.font.color.rgb = RGBColor(0, 0, 0)
            style.font.bold = name != "Title"
            style.paragraph_format.space_before = Pt(10)
            style.paragraph_format.space_after = Pt(7)
            style.paragraph_format.keep_with_next = True
        self.doc.core_properties.title = topic
        self.doc.core_properties.subject = self.t(f"Laboratory work {lab}", f"Лабораторная работа {lab}")
        self.doc.core_properties.author = "Септанугрохо Мухаммад Арис"
        self.doc.core_properties.keywords = self.t("ITMO Python laboratory report", "ИТМО Python отчёт лабораторная работа")
        self.doc.core_properties.language = "en-US" if language == "EN" else "ru-RU"
        lang = OxmlElement("w:lang")
        lang.set(qn("w:val"), self.doc.core_properties.language)
        normal.element.get_or_add_rPr().append(lang)
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        field = OxmlElement("w:fldSimple")
        field.set(qn("w:instr"), "PAGE")
        footer._p.append(field)
        self.cover(topic)

    def t(self, en, ru):
        return en if self.language == "EN" else ru

    def p(self, en, ru=None, *, style=None):
        return self.doc.add_paragraph(en if ru is None else self.t(en, ru), style)

    def h(self, en, ru, level=1):
        self.doc.add_heading(self.t(en, ru), level)

    def page(self):
        self.doc.add_page_break()

    def cover(self, topic):
        p = self.p("ITMO University", "Университет ИТМО")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].bold = True
        p = self.p("Python Programming Course", "Курс программирования на Python")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Cm(3.3)
        p = self.p(self.t(f"Laboratory Work {self.lab}", f"Лабораторная работа {self.lab}"), style="Title")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p = self.p(topic)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.size = Pt(17)
        p = self.p("Report", "Отчёт")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Cm(3.7)
        for en, ru in [
            ("Student  Септанугрохо Мухаммад Арис", "Выполнил  Септанугрохо Мухаммад Арис"),
            ("ISU number  512260", "Номер ИСУ  512260"),
            ("Group  P3121", "Группа  P3121"),
        ]:
            p = self.p(en, ru)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p = self.p("2026")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Cm(2.8)
        self.page()

    def table(self, headers, rows, widths=None):
        table = self.doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        table.autofit = False
        for cell, value in zip(table.rows[0].cells, headers):
            cell.text = str(value)
            for run in cell.paragraphs[0].runs:
                run.bold = True
            shade = OxmlElement("w:shd")
            shade.set(qn("w:fill"), "EAEFF4")
            cell._tc.get_or_add_tcPr().append(shade)
        header = OxmlElement("w:tblHeader")
        table.rows[0]._tr.get_or_add_trPr().append(header)
        for values in rows:
            for cell, value in zip(table.add_row().cells, values):
                cell.text = str(value)
        for row in table.rows:
            keep = OxmlElement("w:cantSplit")
            row._tr.get_or_add_trPr().append(keep)
            for index, cell in enumerate(row.cells):
                if widths:
                    cell.width = Cm(widths[index])
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.line_spacing = 1.0
                    for run in p.runs:
                        run.font.size = Pt(9.5)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(0)
        return table

    def code(self, text):
        p = self.p(text)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(8)
        for run in p.runs:
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        return p

    def figure(self, relative_path, caption_en, caption_ru, width=16):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(ROOT / relative_path), width=Cm(width))
        p = self.p(caption_en, caption_ru)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.italic = True
            run.font.size = Pt(9)

    def save(self, basename):
        # Word's default Title style may carry a theme-colored paragraph rule.
        # Remove paragraph borders from the title and inherited styles.
        for root in (self.doc.element, self.doc.styles.element):
            for border in list(root.iter(qn("w:pBdr"))):
                border.getparent().remove(border)
        path = ROOT / f"lab{self.lab}" / f"{basename}_{self.language}.docx"
        self.doc.save(path)
        print(path.relative_to(ROOT))
        return path


def lab1(language):
    r = Report(1, language, "Catalog Search" if language == "EN" else "Поиск по каталогу")
    r.h("1 Objective and result", "1 Цель и результат работы")
    r.p(
        "An interactive command-line application was implemented for searching an airport catalog. It loads CSV records, normalizes titles and queries, applies all-word matching and filters, ranks the matches, highlights words and supports user ratings. The application is implemented in Python using only the standard library.",
        "Реализовано интерактивное консольное приложение для поиска по каталогу аэропортов. Оно загружает CSV, нормализует названия и запросы, выполняет поиск по всем словам и фильтрацию, ранжирует результаты, выделяет совпадения и поддерживает оценки пользователя. Приложение написано на Python с использованием стандартной библиотеки.",
    )
    r.h("2 Assigned variant and dataset", "2 Вариант и исходные данные")
    r.code("airports-csv | title | clean | words-all | top10 | mark | boost")
    r.p(
        "The file lab1/data/airports/records.csv contains 8,000 records and 11 fields. Each CSV row is read by csv.DictReader as a dictionary. Search uses only title; the result card displays all fields. Values remain strings until filter comparison converts numbers and Boolean values.",
        "Файл lab1/data/airports/records.csv содержит 8 000 записей и 11 полей. csv.DictReader читает каждую строку как словарь. Поиск использует только title, а карточка показывает все поля. Значения остаются строками до преобразования чисел и логических значений при сравнении фильтров.",
    )
    r.table(
        [r.t("Field group", "Группа полей"), r.t("Columns", "Столбцы")],
        [
            [r.t("Identity and title", "Идентификатор и название"), "id, title"],
            [r.t("Description", "Описание"), "city, keywords, country, kind"],
            [r.t("Numeric attributes", "Числовые характеристики"), "elevation_ft, latitude, longitude"],
            [r.t("Service information", "Служебная информация"), "scheduled, url"],
        ], [5, 11.8],
    )
    r.h("3 Program structure", "3 Структура программы")
    r.p(
        "CatalogSearchApp owns the session state: selected variant, records, active filters, ratings and last_results. run reads commands in a loop; execute dispatches them to focused methods. The same object retains state between commands. Separate helper functions transform text, read CSV, apply filters and render records.",
        "CatalogSearchApp хранит состояние сеанса: вариант, записи, активные фильтры, оценки и last_results. run читает команды в цикле, execute передаёт их соответствующим методам. Один объект сохраняет состояние между командами. Отдельные вспомогательные функции преобразуют текст, читают CSV, применяют фильтры и формируют карточки.",
    )
    r.table(
        [r.t("Component", "Компонент"), r.t("Responsibility", "Назначение")],
        [
            ["normalize", r.t("Common normalization of title and query", "Одинаковая нормализация названия и запроса")],
            ["value_for_filter, apply_filters", r.t("Conversion and AND-combined comparisons", "Преобразование и сравнения с логическим И")],
            ["highlight, render_record", r.t("Highlight matches and construct a record card", "Выделение совпадений и формирование карточки")],
            ["search, rate, save", r.t("Rank records, store ratings and export the last result", "Ранжирование, оценки и сохранение последней выдачи")],
        ], [6, 10.8],
    )
    r.page()
    r.h("4 Normalization and matching", "4 Нормализация и поиск")
    r.p(
        "The clean procedure applies casefold, Unicode NFKD decomposition and removal of combining diacritic marks. A regular expression extracts word sequences and joins them with spaces. Punctuation acts as a separator; the regular expression also treats underscores as word characters. The query and title are processed identically. For example, São-Paulo becomes sao paulo.",
        "Процедура clean выполняет casefold, Unicode-разложение NFKD и удаление комбинируемых диакритических знаков. Регулярное выражение извлекает последовательности слов и соединяет их пробелами. Пунктуация служит разделителем; подчёркивание регулярное выражение также считает символом слова. Запрос и название обрабатываются одинаково. Например, São-Paulo превращается в sao paulo.",
    )
    r.p(
        "The normalized query is converted to a set Q. A nonempty query matches when Q is a subset of the title-word set. Therefore every distinct query word is required, but order is irrelevant. Repeating a query word does not increase its weight. An empty query selects all records that pass the filters.",
        "Нормализованный запрос преобразуется в множество Q. Непустой запрос подходит, когда Q является подмножеством множества слов названия. Нужны все уникальные слова запроса, но их порядок не важен. Повтор слова в запросе не увеличивает его вес. Пустой запрос выбирает все записи, прошедшие фильтры.",
    )
    r.h("5 Relevance and rating boost", "5 Релевантность и влияние оценок")
    r.code("relevance = sum(title_words.count(word) for word in query_words)\nscore = relevance + 0.5 * rating")
    r.p(
        "Relevance counts occurrences of distinct query words in the title. This is an occurrence score, not a normalized similarity. An unrated airport contributes zero rating points; a rating of five adds 2.5. Sorting uses descending score, descending relevance, then the case-folded title alphabetically. Only after filtering and sorting are the first ten records displayed.",
        "Релевантность считает вхождения уникальных слов запроса в название. Это балл по количеству вхождений, а не нормализованное сходство. Неоценённый аэропорт не получает прибавки, оценка пять добавляет 2,5. Сортировка идёт по убыванию итогового балла, затем релевантности, затем по названию без учёта регистра. Первые десять записей выбираются только после фильтрации и сортировки.",
    )
    r.p(
        "Ratings are integers from one to five, associated with record IDs. A user may rate only an airport in the last displayed search results. A new rating replaces the previous one. Ratings reorder matching records but never introduce a record that fails the query or a filter. Loading data clears filters, ratings and last results; exiting loses the in-memory ratings.",
        "Оценки — целые числа от одного до пяти, связанные с id. Оценивать можно только аэропорт из последней показанной выдачи. Новая оценка заменяет старую. Оценки меняют порядок подходящих записей, но не добавляют запись, не прошедшую запрос или фильтр. Загрузка очищает фильтры, оценки и последнюю выдачу; при выходе оценки из памяти теряются.",
    )
    r.h("6 Filtering and presentation", "6 Фильтрация и представление")
    r.p(
        "Filters support eq, ne, lt, le, gt, ge and contains. All active conditions are combined with AND; an empty field fails a filter. Numeric comparisons require numeric operands. Matched title words are enclosed in [[double brackets]] while retaining their original spelling. Each search reports match count, displayed count, cards, relevance, rating, final score and elapsed time. show prints the entire catalog without filters or a result limit. save writes the last displayed record cards to UTF-8 text, without search highlighting or score annotations.",
        "Фильтры поддерживают eq, ne, lt, le, gt, ge и contains. Все условия объединяются через И; пустое поле не проходит фильтр. Числовое сравнение требует числовых операндов. Совпавшие слова названия заключаются в [[двойные скобки]] с сохранением написания. Поиск показывает число совпадений и выведенных записей, карточки, релевантность, оценку, итоговый балл и время. show выводит весь каталог без фильтров и лимита. save сохраняет последние карточки в UTF-8 без подсветки и приписанных баллов.",
    )
    r.page()
    r.h("7 Running and demonstration", "7 Запуск и демонстрация")
    r.p("Run python main.py from lab1. Airports is the default variant. The following command sequence demonstrates loading, search, filtering and ratings.",
        "В каталоге lab1 выполните python main.py. По умолчанию выбран вариант аэропортов. Следующая последовательность показывает загрузку, поиск, фильтрацию и оценки.")
    r.code('load\nfields\nsearch "airport"\nrate US-10787 5\nsearch "airport"\nfilter add country eq US\nfilter add scheduled eq true\nsearch "airport"\nratings\nsave results.txt\nexit')
    r.p(
        "US-10787 was in the unfiltered top ten in the verified dataset. When using another CSV or query, select an ID actually present in the latest output. Commands with spaces in arguments use quotation marks. Expected command and file errors are reported without terminating the input loop.",
        "US-10787 присутствовал в исходной первой десятке проверенного датасета. При другом CSV или запросе выбирайте id, действительно показанный последним поиском. Аргументы с пробелами заключаются в кавычки. Ожидаемые ошибки команд и файлов сообщаются без завершения цикла ввода.",
    )
    r.h("8 Verification results", "8 Результаты проверки")
    r.table(
        [r.t("Check", "Проверка"), r.t("Observed result", "Полученный результат")],
        [
            [r.t("Load bundled CSV", "Загрузка CSV"), r.t("8,000 rows and 11 fields", "8 000 строк и 11 полей")],
            [r.t('Search for "airport"', 'Поиск "airport"'), r.t("3,686 matches and 10 displayed records", "3 686 совпадений и 10 показанных записей")],
            [r.t("Rate the tenth visible record 5", "Оценка десятой видимой записи на 5"), r.t("US-10787 moves to first place", "US-10787 становится первым")],
            [r.t("Combine country and scheduled filters", "Совместная фильтрация country и scheduled"), r.t("All displayed records have US and true", "Все показанные записи имеют US и true")],
            [r.t("Normalization", "Нормализация"), "São-Paulo → sao paulo"],
            [r.t("Save and reload", "Сохранение и новая загрузка"), r.t("Nonempty export; filters, ratings and results reset", "Непустой экспорт; фильтры, оценки и выдача сброшены")],
        ], [6.4, 10.4],
    )
    r.h("9 Conclusion", "9 Вывод")
    r.p(
        "The airport variant is implemented as a stateful object-oriented console application. The result combines CSV loading, consistent Unicode processing, all-word title search, filters, rating-based ranking, top-ten presentation and highlighting. The verified demonstration confirms the rating affects order while preserving matching and filtering rules. An additional artworks configuration is available through --variant artworks, but this report covers the assigned airport variant.",
        "Вариант аэропортов реализован как объектно-ориентированное консольное приложение с состоянием сеанса. Решение объединяет загрузку CSV, согласованную обработку Unicode, поиск всех слов по названию, фильтры, ранжирование с оценками, первую десятку и подсветку. Проверка подтверждает изменение порядка оценкой при сохранении правил поиска и фильтрации. Дополнительная конфигурация картин доступна через --variant artworks, но отчёт посвящён варианту аэропортов.",
    )
    return r.save("Report_Airports")


def lab2(language):
    r = Report(2, language, "Airport Data Analysis with NumPy and pandas" if language == "EN" else "Анализ аэропортов с NumPy и pandas")
    r.h("1 Objective and data preparation", "1 Цель и подготовка данных")
    r.p(
        "The airport catalog from Lab 1 was analyzed in analysis.ipynb using NumPy, pandas and Matplotlib. The work compares missing-value imputation and duplicate removal, verifies manual statistics, investigates logical filters and operation order, and describes airport types and within-group deviations. The notebook contains executed results and four plots.",
        "Каталог аэропортов из ЛР1 исследован в analysis.ipynb с помощью NumPy, pandas и Matplotlib. Сравниваются способы заполнения пропусков и удаления повторов, проверяются ручные статистики, исследуются логические фильтры и порядок операций, описываются типы аэропортов и отклонения внутри групп. Блокнот содержит результаты выполнения и четыре графика.",
    )
    r.table([r.t("Characteristic", "Характеристика"), r.t("Value", "Значение")], [
        [r.t("Number of records", "Количество записей"), "8 000"],
        ["X", r.t("elevation_ft — elevation in feet", "elevation_ft — высота в футах")],
        ["G", r.t("kind — airport type", "kind — тип аэропорта")],
        [r.t("Observed and missing X", "Известные X и пропуски"), "6 550 / 1 450"],
        [r.t("Random seed", "Начальное состояние генератора"), "42"],
    ], [6.5, 10.3])
    r.p(
        "Heights are converted with to_numeric(errors='coerce'). Empty cells and null markers become missing rather than zero. Explicit missing markers preserve the country code NA. Missing group labels are collected under Неизвестно. Statistical calculations exclude missing X. The original DataFrame is preserved; the imputation and duplication experiments use independent copies.",
        "Высоты преобразуются через to_numeric(errors='coerce'). Пустые ячейки и маркеры null становятся пропусками, а не нулями. Явные маркеры пропусков сохраняют код страны NA. Пустые группы собираются под названием «Неизвестно». Статистика исключает пропуски X. Исходный DataFrame сохраняется; эксперименты с пропусками и повторами используют независимые копии.",
    )
    r.h("2 Missing value experiment", "2 Эксперимент с пропусками")
    r.p(
        "A seeded generator selects 655 of the 6,550 known heights without replacement. Their indices and true values are retained only for evaluation. All three methods fill the same damaged table independently. Mean, median and per-type medians are calculated after removal; a group without an observed height falls back to the global observed median. Original missing heights are not included in evaluation.",
        "Генератор с заданным seed выбирает без повторения 655 из 6 550 известных высот. Индексы и настоящие значения сохраняются только для проверки. Три способа независимо заполняют одну повреждённую таблицу. Среднее, медиана и медианы типов вычисляются после удаления; для группы без известных высот используется общая медиана оставшихся данных. Исходные пропуски в оценку не входят.",
    )
    r.code("MAE = mean(abs(restored - true))\nMSE = mean((restored - true) ** 2)")
    method_names = [r.t("Global mean", "Общее среднее"), r.t("Global median", "Общая медиана"), r.t("Group median", "Медиана группы")]
    r.table([r.t("Method", "Способ"), r.t("MAE in feet", "MAE в футах"), r.t("MSE in square feet", "MSE в квадратных футах")],
        [[name, f"{entry['MAE_ft']:.2f}", f"{entry['MSE_ft2']:.2f}"] for name, entry in zip(method_names, SUMMARY["imputation"])], [6, 4.5, 6.3])
    r.p(
        "Group median gives the lowest MAE, while global mean gives the lowest MSE. Squaring gives large errors in the upper elevation tail much greater influence. MAE and MSE have different units and cannot be compared directly by magnitude. Group information helps absolute error here, but does not reconstruct an individual airport's geography.",
        "Минимальная MAE получена у медианы группы, минимальная MSE — у общего среднего. Квадрат значительно усиливает большие ошибки в верхнем хвосте высоты. MAE и MSE имеют разные единицы, поэтому их величины нельзя сравнивать напрямую. Информация о типе здесь улучшает абсолютную ошибку, но не восстанавливает географию конкретного аэропорта.",
    )
    r.page()
    r.h("3 Duplicate removal", "3 Удаление повторов")
    r.p(
        "Exactly 400 randomly selected rows, or 5% of the original catalog, are appended as exact copies. Three independent copies of the augmented table are deduplicated by all columns, by id, and by country. The first occurrence is kept. Comparing country demonstrates why a shared descriptive attribute is not necessarily an identity key.",
        "В каталог добавлены точные копии 400 случайно выбранных строк — 5% исходного количества. На трёх независимых копиях удалены повторы по всем столбцам, по id и по country. Сохраняется первое вхождение. Сравнение по стране показывает, почему общий описательный признак не обязательно является ключом идентичности.",
    )
    stages = [r.t("Before adding copies", "До добавления копий"), r.t("After adding copies", "После добавления копий"), r.t("All-column deduplication", "Удаление по всем полям"), r.t("ID deduplication", "Удаление по id"), r.t("Country deduplication", "Удаление по стране")]
    r.table([r.t("Stage", "Этап"), r.t("Rows", "Строки"), r.t("Mean X in feet", "Среднее X в футах")],
        [[name, entry["rows"], f"{entry['mean_X_ft']:.2f}"] for name, entry in zip(stages, SUMMARY["duplicates"])], [7.8, 3, 6])
    r.p(
        "The baseline contains unique IDs and no exact duplicates. The first two methods therefore restore the original 8,000 rows and mean. Country removal leaves 193 rows and deletes real airports with distinct IDs. The notebook displays such examples. Adding copies changes the mean slightly because the copied subset does not have to share the overall mean.",
        "В исходных данных id уникальны и полных повторов нет. Поэтому первые два способа восстанавливают 8 000 строк и исходное среднее. Удаление по стране оставляет 193 строки и удаляет настоящие аэропорты с разными id; примеры показаны в блокноте. Добавление копий немного меняет среднее, поскольку среднее скопированной части не обязано совпадать с общим.",
    )
    r.h("4 Manual descriptive statistics", "4 Ручные описательные статистики")
    r.p(
        "After excluding missing values, loops, sorting and arithmetic calculate the range, mean, median, variance and standard deviation. For even N, the median averages the two central sorted values. Variance divides the sum of squared deviations by N. NumPy and pandas comparisons use ddof=0, and all results agree within floating-point tolerance.",
        "После исключения пропусков циклы, сортировка и арифметика вычисляют размах, среднее, медиану, дисперсию и стандартное отклонение. При чётном N медиана усредняет два центральных элемента. Дисперсия делит сумму квадратов отклонений на N. Сравнения NumPy и pandas используют ddof=0; результаты совпадают в пределах вычислительной точности.",
    )
    names = [("range", "Range", "Размах"), ("mean", "Mean", "Среднее"), ("median", "Median", "Медиана"), ("variance_ddof0", "Population variance", "Дисперсия с делением на N"), ("std_ddof0", "Standard deviation", "Стандартное отклонение")]
    r.table([r.t("Statistic", "Характеристика"), r.t("Value", "Значение")], [[r.t(en, ru), f"{SUMMARY['statistics'][key]:.2f}"] for key, en, ru in names], [9, 7.8])
    r.p(
        "The mean of 1,302.38 feet exceeds the median of 730 feet, consistent with the long high-elevation tail. pandas normally uses N−1 for variance, so its default would not match the assignment formula. Variance is in square feet; the other statistics above are in feet.",
        "Среднее 1 302,38 фута превышает медиану 730 футов, что соответствует длинному хвосту больших высот. По умолчанию pandas делит дисперсию на N−1, поэтому без явного параметра результат не соответствовал бы формуле задания. Дисперсия измеряется в квадратных футах, остальные характеристики таблицы — в футах.",
    )
    r.page()
    r.h("5 Logical filters and operation order", "5 Логические фильтры и порядок операций")
    r.p(
        "The selected types are small_airport and medium_airport; the elevation threshold is 500 feet. AND requires both type membership and elevation above the threshold. OR requires either condition. AND selects 2,456 rows; OR selects 5,814; 3,358 occur only in OR. Missing X never satisfies the height condition, but the row may enter OR through its type.",
        "Выбраны типы small_airport и medium_airport, граница высоты — 500 футов. И требует подходящего типа и превышения границы, ИЛИ — хотя бы одного условия. И выбирает 2 456 строк, ИЛИ — 5 814; только в ИЛИ находятся 3 358 строк. Пропуск X не проходит условие высоты, но строка может попасть в ИЛИ по типу.",
    )
    r.p(
        "Filtering before nlargest(5) selects the five highest eligible airports. Applying nlargest(5) to the complete table first can discard eligible airports before filtering. The two orders give different results in this dataset and are not interchangeable in general.",
        "Фильтрация перед nlargest(5) выбирает пять самых высоких подходящих аэропортов. Общий nlargest(5) до фильтра может заранее отбросить подходящие объекты. На этих данных результаты различаются; в общем случае операции не перестановочны.",
    )
    r.h("6 Group summaries", "6 Групповые сводки")
    r.table([r.t("Type", "Тип"), r.t("Rows", "Строки"), r.t("Share", "Доля"), r.t("Missing X", "Пропуски X"), r.t("Mean X", "Среднее X")],
        [[g["kind"], g["group_count"], f"{100*g['share']:.3f}%", g["missing_X"], f"{g['group_mean']:.2f}"] for g in SUMMARY["groups"]], [5.3, 2.1, 2.8, 2.9, 3.7])
    r.p(
        "Group size counts all rows, including missing heights. Means and medians omit missing X; shares use all 8,000 rows. Small airports dominate with 3,949 objects, while balloonports contain only six. Groups are sorted by descending size and the largest horizontal bar is placed at the top.",
        "Размер группы учитывает все строки, включая пропуски высоты. Средние и медианы пропускают неизвестные X, доли считаются от 8 000 строк. Малые аэропорты преобладают — 3 949 объектов, площадок аэростатов всего шесть. Группы отсортированы по убыванию размера, крупнейшая полоса расположена сверху.",
    )
    r.figure("lab2/results/group_counts.png", "Figure 1 Number of airports by type", "Рисунок 1 Количество аэропортов по типам", 15.5)
    r.page()
    r.h("7 Comparing an object with its group", "7 Сравнение объекта со своей группой")
    r.p(
        "A many-to-one join attaches group_count and group_mean to each original row. Validation and assertions preserve the count of 8,000 and the source index. delta = elevation_ft − group_mean compares an airport with its own type; a missing height produces a missing delta. Both figures use the same first 100 rows with known X.",
        "Соединение many-to-one добавляет group_count и group_mean к каждой исходной строке. Проверки сохраняют 8 000 строк и исходный индекс. delta = elevation_ft − group_mean сравнивает аэропорт со средним его типа; пропуск высоты даёт пропуск delta. Оба рисунка используют те же первые 100 строк с известным X.",
    )
    r.figure("lab2/results/group_delta_scatter.png", "Figure 2 Deviations in the original object order", "Рисунок 2 Отклонения в исходном порядке объектов", 15.2)
    r.p(
        "Points above zero have greater elevation than their type's mean; points below zero have smaller elevation. The second plot sorts these same objects by delta and assigns new evenly spaced positions from 1 to 100, so the line cannot decrease.",
        "Точки выше нуля имеют высоту больше среднего своего типа, ниже нуля — меньше. Второй график сортирует те же объекты по delta и задаёт новые равноотстоящие позиции от 1 до 100, поэтому линия не убывает.",
    )
    r.figure("lab2/results/group_delta_sorted.png", "Figure 3 The same deviations in increasing order", "Рисунок 3 Те же отклонения по возрастанию", 15.2)
    r.page()
    r.h("8 Quantiles and boxplots", "8 Квантили и диаграммы размаха")
    r.p(
        "The elevation quartiles are Q1 = 207.25, Q2 = 730.00 and Q3 = 1,630.00 feet. Q2 equals the median; Q1–Q3 contains the central half of the distribution. Boxplots are constructed for the five groups with the largest row counts, excluding missing heights inside each group.",
        "Квартили высоты: Q1 = 207,25, Q2 = 730,00, Q3 = 1 630,00 фута. Q2 совпадает с медианой, интервал Q1–Q3 описывает центральную половину распределения. Диаграммы построены для пяти групп с наибольшим числом строк; пропуски высоты исключены внутри групп.",
    )
    r.figure("lab2/results/group_boxplots.png", "Figure 4 Elevation distributions for the five largest types", "Рисунок 4 Распределения высоты пяти крупнейших типов", 16)
    r.p(
        "Among these groups, small_airport has the highest median (830 feet), largest IQR (1,442 feet) and largest range (14,330 feet). large_airport has the lowest median (140 feet) and smallest IQR (716 feet). Points beyond the whiskers are statistical outliers, not automatically invalid observations. Negative elevations can also be valid.",
        "Среди выбранных групп small_airport имеет наибольшую медиану — 830 футов, IQR — 1 442 фута и размах — 14 330 футов. У large_airport минимальные медиана — 140 футов и IQR — 716 футов. Точки за усами являются статистическими выбросами, но не обязательно ошибками. Отрицательная высота также может быть настоящей.",
    )
    r.h("9 Verification and conclusion", "9 Проверка и вывод")
    r.p(
        "The notebook was executed from a fresh kernel. Assertions check numeric data, unchanged observed values after filling, duplicate counts, manual statistics, AND being a subset of OR, group totals, preserved rows after the join, identical membership of the delta samples, increasing sorted deltas and the unchanged original table. Detailed results are saved in results/summary.json and the two CSV summary tables.",
        "Блокнот выполнен из нового ядра. Проверяются числовые данные, неизменность известных значений после заполнения, число повторов, ручные статистики, включение И в ИЛИ, суммы групп, сохранение строк при соединении, одинаковый состав выборок delta, возрастание отсортированных отклонений и неизменность исходной таблицы. Результаты сохранены в results/summary.json и двух сводных CSV.",
    )
    r.p(
        "The experiments show that the preferred imputation depends on the error metric, while duplicate removal depends on a meaningful identity key. Logical operators and operation order change the selected population. Group summaries and robust distribution measures give context that an overall mean alone cannot provide.",
        "Эксперименты показывают зависимость лучшего заполнения от метрики ошибки, а удаления повторов — от содержательного ключа идентичности. Логические операции и их порядок меняют состав выборки. Групповые сводки и устойчивые характеристики распределения дают контекст, которого недостаточно получить только из общего среднего.",
    )
    return r.save("Report_Airports")


def lab3(language):
    r = Report(3, language, "A Small Neural Network Library with NumPy" if language == "EN" else "Небольшая библиотека нейронных сетей на NumPy")
    r.h("1 Objective and implementation", "1 Цель и реализация")
    r.p(
        "A modular neural-network library was implemented using NumPy and manual backpropagation. tutorial.ipynb contains the complete code, explanations, examples and executed MNIST experiment. Its writefile cells save the implementation into separate minitorch modules. The resulting 784–32–10 network reaches 89.51% accuracy on the independent 10,000-image test set.",
        "Реализована модульная библиотека нейронных сетей на NumPy с ручным обратным распространением. tutorial.ipynb содержит полный код, объяснения, примеры и выполненный эксперимент MNIST. Ячейки writefile сохраняют реализацию в отдельные модули minitorch. Полученная сеть 784–32–10 достигает точности 89,51% на отдельной тестовой выборке из 10 000 изображений.",
    )
    r.h("2 Class design", "2 Проектирование классов")
    r.figure("lab3/results/uml.png", "Figure 1 Final class diagram", "Рисунок 1 Итоговая диаграмма классов", 16)
    r.table([r.t("Class", "Класс"), r.t("Responsibility", "Ответственность")], [
        ["Parameter", r.t("Owns a value array and an equally shaped gradient", "Хранит массив значений и градиент той же формы")],
        ["Layer", r.t("Abstract forward, backward and common calling interface", "Абстрактные проходы и единый интерфейс вызова")],
        ["Linear, ReLU", r.t("Affine transformation and nonlinearity", "Аффинное преобразование и нелинейность")],
        ["Sequential", r.t("Nested layer composition and model persistence", "Вложенная композиция слоёв и сохранение модели")],
        ["MSELoss, SGD", r.t("Measure error and update existing parameters", "Измеряют ошибку и обновляют существующие параметры")],
    ], [5, 11.8])
    r.p(
        "Inheritance gives layers the same interface; composition builds models, including nested Sequential containers. parameters() returns the original Parameter objects in layer order, so SGD updates the same arrays used by forward. The initial diagram in notebook section 1 retains these responsibilities in the final design.",
        "Наследование задаёт слоям одинаковый интерфейс; композиция строит модели, включая вложенные Sequential. parameters() возвращает исходные Parameter в порядке слоёв, поэтому SGD обновляет массивы, используемые forward. Первоначальная схема в разделе 1 блокнота сохраняет эти обязанности в итоговой реализации.",
    )
    r.page()
    r.h("3 Forward and backward computation", "3 Прямые и обратные вычисления")
    r.p(
        "Inputs are nonempty two-dimensional arrays: rows represent objects and columns represent features. A Linear layer stores W with shape (input_features, output_features) and b with shape (output_features,). Bias broadcasts across rows. Both arrays start with small random values around zero; one seeded generator makes initialization reproducible.",
        "Входы — непустые двумерные массивы: строки соответствуют объектам, столбцы — признакам. Linear хранит W формы (input_features, output_features) и b формы (output_features,). Смещение распространяется по строкам. Оба массива получают малые случайные значения около нуля, один генератор с seed обеспечивает воспроизводимость.",
    )
    r.table([r.t("Operation", "Операция"), r.t("Formula", "Формула")], [
        ["Linear forward", "Y = XW + b"],
        [r.t("Linear input gradient", "Градиент входа Linear"), "G_X = G Wᵀ"],
        [r.t("Linear weight gradient", "Градиент весов Linear"), "G_W = Xᵀ G"],
        [r.t("Linear bias gradient", "Градиент смещения Linear"), "G_b = sum(G, axis=0)"],
        ["ReLU forward / backward", "Y = max(0, X);  G_X = G · [X > 0]"],
        ["MSELoss", "L = sum((prediction − target)²) / (n k)"],
        [r.t("MSE prediction gradient", "Градиент MSE по прогнозу"), "G_prediction = 2 (prediction − target) / (n k)"],
    ], [6.6, 10.2])
    r.p(
        "G is the gradient received from the next layer in reverse order. Linear caches its input to compute parameter derivatives. ReLU caches a positive-input mask, has no trainable parameters and chooses derivative zero at zero. Sequential traverses layers forward for prediction and in reverse for backpropagation, implementing the chain rule.",
        "G — градиент, полученный от следующего слоя в обратном порядке. Linear сохраняет вход для производных параметров. ReLU сохраняет маску положительного входа, не имеет обучаемых параметров и выбирает нулевую производную в нуле. Sequential проходит слои вперёд при прогнозе и в обратном порядке при распространении градиента, реализуя цепное правило.",
    )
    r.p(
        "MSE averages over n objects and k outputs, and returns one number. Exact target/prediction shape equality prevents unintended broadcasting. The factor 1/(n k) is already included in the loss derivative and must not be applied again in Linear. Numerical central differences verify analytical derivatives for every weight, bias and input coordinate in the test model.",
        "MSE усредняет по n объектам и k выходам и возвращает одно число. Точное равенство форм ответов и прогнозов исключает случайный broadcasting. Множитель 1/(n k) уже включён в производную ошибки и не должен повторяться в Linear. Центральные численные разности проверяют аналитические производные всех весов, смещений и входных координат тестовой модели.",
    )
    r.h("4 Optimization and training loop", "4 Оптимизация и цикл обучения")
    r.code("zero_grad()\nprediction = model(x_batch)\nloss = criterion(prediction, target_batch)\nmodel.backward(criterion.backward())\noptimizer.step()\n\nparameter.value -= learning_rate * parameter.grad")
    r.p(
        "Gradients accumulate through +=, so zero_grad clears them before each batch. SGD uses a positive finite learning rate and works independently of layer types. One index permutation shuffles inputs and targets together each epoch. The final incomplete batch is included. Epoch loss is sum(batch_loss × actual_batch_size) / N, preventing a short batch from receiving excess weight.",
        "Градиенты накапливаются через +=, поэтому zero_grad обнуляет их перед каждой порцией. SGD использует положительную конечную скорость и не зависит от типов слоёв. Одна перестановка индексов одновременно перемешивает входы и ответы каждой эпохи. Последняя неполная порция включается. Ошибка эпохи равна sum(batch_loss × actual_batch_size) / N, поэтому короткая порция не получает лишнего веса.",
    )
    r.page()
    r.h("5 MNIST experiment", "5 Эксперимент MNIST")
    r.p(
        "fetch_openml obtains mnist_784 version 1. scikit-learn is used only for data loading; NumPy performs all network computation. The liac-arff parser avoids a numeric-category compatibility issue in the default pandas parser without changing the dataset. The first 60,000 images train the model; the last 10,000 are used only for evaluation. Test data never updates parameters or selects hyperparameters.",
        "fetch_openml получает mnist_784 версии 1. scikit-learn используется только для загрузки, все вычисления сети выполняет NumPy. Парсер liac-arff обходит проблему числовых категорий стандартного парсера pandas без изменения датасета. Первые 60 000 изображений обучают модель, последние 10 000 используются только для оценки. Тест не обновляет параметры и не используется для выбора гиперпараметров.",
    )
    r.table([r.t("Setting", "Настройка"), r.t("Value", "Значение")], [
        [r.t("Input and target", "Вход и ответ"), r.t("784 float32 pixels / 255; 10 one-hot outputs", "784 пикселя float32 / 255; 10 выходов one-hot")],
        [r.t("Architecture", "Архитектура"), "Linear(784, 32) → ReLU → Linear(32, 10)"],
        [r.t("Trainable values", "Обучаемые числа"), "784 × 32 + 32 + 32 × 10 + 10 = 25 450"],
        [r.t("Loss and optimizer", "Ошибка и оптимизатор"), "MSELoss; SGD; lr = 0.05"],
        [r.t("Epochs and batch size", "Эпохи и размер порции"), r.t("10 epochs; batch 128; final batch 96", "10 эпох; порция 128; последняя порция 96")],
        [r.t("Initialization and shuffle seed", "Seed инициализации и перемешивания"), "42"],
    ], [6, 10.8])
    r.p(
        "Every 28 × 28 image is flattened into 784 values. Pixel scaling gives values in [0, 1], and one-hot encoding places one at the correct digit's output. Predictions are argmax over ten scores; these scores are not probabilities and need not sum to one.",
        "Каждое изображение 28 × 28 развёрнуто в 784 значения. Масштабирование переводит пиксели в [0, 1], one-hot ставит единицу на выходе правильной цифры. Прогноз — argmax десяти оценок; они не являются вероятностями и не обязаны давать сумму один.",
    )
    r.figure("lab3/results/training_loss.png", "Figure 2 Sample-weighted training MSE by epoch", "Рисунок 2 MSE обучения по эпохам с учётом размера порций", 15.2)
    r.p(
        "The training-history loss decreases from 0.071865 to 0.025767. It averages batch losses measured at changing weights during an epoch. It therefore differs from a separate full-dataset loss evaluated at the final epoch weights.",
        "Ошибка истории обучения снижается с 0,071865 до 0,025767. Она усредняет ошибки порций при меняющихся весах в течение эпохи, поэтому отличается от отдельной ошибки всей выборки при конечных весах эпохи.",
    )
    r.page()
    r.h("6 Test metrics and predictions", "6 Тестовые метрики и предсказания")
    r.table([r.t("Metric", "Метрика"), r.t("Measured value", "Измеренное значение")], [
        [r.t("Test accuracy before training", "Тестовая точность до обучения"), "5.71%"],
        [r.t("Test accuracy after training", "Тестовая точность после обучения"), "89.51%"],
        [r.t("Correct test predictions", "Правильные тестовые прогнозы"), "8 951 / 10 000"],
        [r.t("Final test MSE", "Итоговая тестовая MSE"), f"{METRICS['test_mse']:.6f}"],
        [r.t("Maximum score difference after reload", "Максимальная разность после загрузки"), "0.0"],
    ], [10, 6.8])
    r.p(
        "Accuracy counts correct argmax decisions, while MSE measures numerical error against the one-hot vectors. These metrics need not change in the same way. A random initial model need not have exactly 10% accuracy because its decisions are not uniformly random labels.",
        "Accuracy считает правильные решения argmax, MSE измеряет числовую ошибку относительно one-hot. Метрики не обязаны меняться одинаково. Случайная начальная модель не обязана давать ровно 10% точности, поскольку её решения не равнозначны равномерным случайным цифрам.",
    )
    r.figure("lab3/results/predictions.png", "Figure 3 Predictions for the first twelve test images", "Рисунок 3 Прогнозы первых двенадцати тестовых изображений", 13.5)
    r.p(
        "The examples are the first twelve test images, without selecting only successful cases. Correct and incorrect predictions are included: for example, a 5 is predicted as 6 and a 6 as 8. Raw metrics, the full confusion matrix and per-digit accuracy are stored in results/metrics.json.",
        "Показаны первые двенадцать тестовых изображений без отбора только удачных случаев. Есть верные и неверные прогнозы: например, 5 предсказана как 6, а 6 — как 8. Числа, полная матрица ошибок и точность по цифрам сохранены в results/metrics.json.",
    )
    r.page()
    r.h("7 Error analysis and model persistence", "7 Анализ ошибок и сохранение модели")
    r.figure("lab3/results/confusion_matrix.png", "Figure 4 Confusion matrix on the independent test set", "Рисунок 4 Матрица ошибок на отдельной тестовой выборке", 12.3)
    r.p(
        "Rows represent true digits and columns represent predictions. The diagonal contains correct decisions; an off-diagonal cell counts a particular confusion. The saved per-digit results show approximately 97.00% accuracy for digit 1 and 80.83% for digit 5, so recognition quality is not uniform across classes.",
        "Строки соответствуют настоящим цифрам, столбцы — прогнозам. Диагональ содержит правильные решения, ячейка вне диагонали — число конкретных смешений. Сохранённые результаты дают около 97,00% для цифры 1 и 80,83% для цифры 5, поэтому качество распознавания классов неодинаково.",
    )
    r.p(
        "Sequential.save stores a versioned JSON architecture and numeric parameter arrays in model.npz. Loading uses allow_pickle=False, reconstructs nested layers and restores values; gradients and caches reset. Exact equality of all 10,000 test output vectors is verified using the same evaluation batch size. The maximum absolute difference is zero.",
        "Sequential.save записывает структуру JSON с версией и числовые массивы в model.npz. Загрузка использует allow_pickle=False, восстанавливает вложенные слои и значения, обнуляет градиенты и кэши. Проверено точное равенство всех 10 000 тестовых выходных векторов при одинаковом размере порции оценки. Максимальное абсолютное отличие равно нулю.",
    )
    r.h("8 Verification and conclusion", "8 Проверка и вывод")
    r.p(
        "Six automated tests check known forward values, nested parameter identity, central-difference gradients, accumulation and SGD, ReLU and MSE, invalid shapes and call order, nested persistence, successful regression learning and weighted short batches. The notebook was executed from a fresh kernel. Each layer caches one forward pass, so distinct layer instances must be used at different model positions; shared-layer graphs and general automatic differentiation are outside the implementation.",
        "Шесть автоматических тестов проверяют известные выходы, идентичность вложенных параметров, центральные разности, накопление и SGD, ReLU и MSE, неверные формы и порядок вызовов, сохранение вложенности, обучение регрессии и вес коротких порций. Блокнот выполнен из нового ядра. Слой хранит один прямой проход, поэтому на разных позициях нужны разные экземпляры; графы с разделяемыми слоями и общее автодифференцирование не реализованы.",
    )
    r.p(
        "The library demonstrates separation of responsibilities, polymorphic layer interfaces, nested composition and manual application of the chain rule. Its measured MNIST improvement from 5.71% to 89.51% and exact reload equality confirm that training and persistence work together.",
        "Библиотека демонстрирует разделение обязанностей, полиморфный интерфейс слоёв, вложенную композицию и ручное применение цепного правила. Измеренное улучшение MNIST с 5,71% до 89,51% и точное совпадение после загрузки подтверждают совместную работу обучения и сохранения.",
    )
    return r.save("Report_MiniTorch")


def main():
    paths = [builder(language) for builder in (lab1, lab2, lab3) for language in ("EN", "RU")]
    (ROOT / "docs/reports/outputs.json").write_text(
        json.dumps([str(path.relative_to(ROOT)) for path in paths], indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
