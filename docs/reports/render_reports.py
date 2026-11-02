"""Render reports with installed Microsoft Word and rasterize PDFs for visual QA.

Run on Windows in the existing Demandlane environment. QA files stay in TEMP.
"""

import json
import tempfile
from pathlib import Path

import pymupdf as fitz
import win32com.client

ROOT = Path(__file__).resolve().parents[2]
QA = Path(tempfile.gettempdir()) / "itmo-lab-reports-20261102"


def main():
    QA.mkdir(parents=True, exist_ok=True)
    paths = json.loads((ROOT / "docs/reports/outputs.json").read_text())
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    summary = []
    try:
        for relative in paths:
            source = ROOT / relative
            out = QA / source.parent.name / source.stem
            out.mkdir(parents=True, exist_ok=True)
            pdf = out / (source.stem + ".pdf")
            document = word.Documents.Open(
                str(source), ConfirmConversions=False, ReadOnly=True,
                AddToRecentFiles=False, Visible=False,
            )
            try:
                document.Repaginate()
                document.ExportAsFixedFormat(str(pdf), 17)
            finally:
                document.Close(0)
            pages = []
            with fitz.open(pdf) as rendered:
                for i, page in enumerate(rendered):
                    image = out / f"page-{i + 1}.png"
                    page.get_pixmap(dpi=100).save(image)
                    text = page.get_text()
                    (out / f"page-{i + 1}.txt").write_text(text, encoding="utf-8")
                    pages.append({"page": i + 1, "characters": len(text), "head": text[:90]})
            summary.append({"file": relative, "pages": pages, "qa_directory": str(out)})
            print(f"{relative}: {len(pages)} pages", flush=True)
    finally:
        word.Quit(0)
    (QA / "render_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"QA directory: {QA}", flush=True)


if __name__ == "__main__":
    main()
