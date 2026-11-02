# Laboratory reports

Each lab has a separate English and Russian Word report:

| Lab | English | Russian |
| --- | --- | --- |
| 1 | [Catalog search](../../lab1/Report_Airports_EN.docx) | [Поиск по каталогу](../../lab1/Report_Airports_RU.docx) |
| 2 | [Airport data analysis](../../lab2/Report_Airports_EN.docx) | [Анализ данных аэропортов](../../lab2/Report_Airports_RU.docx) |
| 3 | [NumPy neural network library](../../lab3/Report_MiniTorch_EN.docx) | [Библиотека нейросетей NumPy](../../lab3/Report_MiniTorch_RU.docx) |

Reports use the measured notebook outputs and the Lab 1 checks in this directory. Student details are retained from the original Lab 1 reports.

Use the existing environment requested by the user; a new isolated environment is unnecessary:

```powershell
& 'C:\Users\USER\Documents\Aris Project\Demandlane\demandlane\Scripts\python.exe' docs\reports\build_reports.py
```

`build_reports.py` requires python-docx. It rewrites the six report files. `render_reports.py` requires Microsoft Word, pywin32 and PyMuPDF, and creates PDFs and page images under the system temporary directory for visual verification. QA intermediates are not report deliverables.
