"""Interactive catalog search for the Lab 1 airports and artworks variants."""

from __future__ import annotations

import argparse
import csv
import re
import shlex
import time
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
VARIANTS = {
    "airports": {
        "path": ROOT / "data" / "airports" / "records.csv",
        "rating": "boost",
        "limit": 10,
    },
    "artworks": {
        "path": ROOT / "data" / "artworks" / "records.csv",
        "rating": "none", 
        "limit": None,
    },
}


def normalize(value: str) -> str:
    """Case-fold text, remove diacritics, and treat punctuation as separators."""
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    plain = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"\w+", plain, flags=re.UNICODE))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def value_for_filter(raw: str) -> Any:
    text = raw.strip()
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    try:
        return float(text)
    except ValueError:
        return text


def apply_filters(record: dict[str, str], filters: list[tuple[str, str, str]]) -> bool:
    for field, operator, expected_raw in filters:
        if field not in record:
            raise ValueError(f"Unknown field: {field}")
        actual_raw = record[field]
        if actual_raw == "":
            return False
        actual = value_for_filter(actual_raw)
        expected = value_for_filter(expected_raw)
        if operator == "contains":
            passed = str(expected_raw).casefold() in actual_raw.casefold()
        elif operator in {"eq", "ne"}:
            passed = actual == expected
            if operator == "ne":
                passed = not passed
        elif operator in {"lt", "le", "gt", "ge"}:
            if not isinstance(actual, float) or not isinstance(expected, float):
                raise ValueError(f"{operator} requires numeric values")
            passed = {"lt": actual < expected, "le": actual <= expected,
                      "gt": actual > expected, "ge": actual >= expected}[operator]
        else:
            raise ValueError(f"Unknown operator: {operator}")
        if not passed:
            return False
    return True


def highlight(text: str, query_tokens: set[str]) -> str:
    pieces: list[str] = []
    cursor = 0
    for match in re.finditer(r"\w+", text, flags=re.UNICODE):
        if normalize(match.group()) in query_tokens:
            pieces.extend((text[cursor:match.start()], "[[", match.group(), "]]") )
            cursor = match.end()
    pieces.append(text[cursor:])
    return "".join(pieces)


def render_record(record: dict[str, str], query_tokens: set[str] | None = None) -> str:
    record_id = record.get("id", "?")
    title = record.get("title", "")
    if query_tokens:
        title = highlight(title, query_tokens)
    lines = [f"[{record_id}] {title}"]
    for field, value in record.items():
        if field not in {"id", "title"}:
            lines.append(f"  {field}: {value if value else '—'}")
    return "\n".join(lines)


class CatalogSearchApp:
    """Owns the interactive session state and handles its commands."""

    def __init__(self, variant_name: str) -> None:
        self.variant = VARIANTS[variant_name]
        self.records: list[dict[str, str]] = []
        self.filters: list[tuple[str, str, str]] = []
        self.ratings: dict[str, int] = {}
        self.last_results: list[dict[str, str]] = []

    def run(self) -> None:
        print("Catalog search. Commands: help. Exit: exit.")
        while True:
            try:
                parts = shlex.split(input("search> "))
            except EOFError:
                return
            except ValueError as error:
                print(f"Error: {error}")
                continue
            if not parts:
                continue
            try:
                if not self.execute(parts):
                    return
            except (OSError, ValueError, KeyError) as error:
                print(f"Error: {error}")

    def execute(self, parts: list[str]) -> bool:
        """Run one parsed command; return False when the session should exit."""
        command = parts[0]
        if command == "exit" and len(parts) == 1:
            return False
        if command == "help" and len(parts) == 1:
            self.show_help()
        elif command == "load" and len(parts) in {1, 2}:
            self.load(parts[1] if len(parts) == 2 else None)
        elif command == "show" and len(parts) == 1:
            self.show_records()
        elif command == "fields" and len(parts) == 1:
            self.show_fields()
        elif command == "filter" and len(parts) >= 2:
            self.handle_filter(parts[1:])
        elif command == "search" and len(parts) == 2:
            self.search(parts[1])
        elif command == "save" and len(parts) == 2:
            self.save(parts[1])
        elif command == "rate" and len(parts) == 3:
            self.rate(parts[1], parts[2])
        elif command == "ratings" and len(parts) == 1:
            self.show_ratings()
        else:
            self.show_help()
        return True

    @staticmethod
    def show_help() -> None:
        print("Commands: help, load <file>, show, fields, filter add <field> <op> <value>,")
        print("          filter list|remove <n>|clear, search \"<query>\", save <file>,")
        print("          rate <id> <1..5>, ratings, exit")

    def load(self, filename: str | None) -> None:
        path = Path(filename) if filename else self.variant["path"]
        if not path.is_absolute():
            path = Path.cwd() / path
        self.records = read_csv(path)
        self.filters.clear()
        self.ratings.clear()
        self.last_results.clear()
        print(f"Loaded records: {len(self.records)}")

    def show_records(self) -> None:
        if not self.records:
            print("No data loaded. Use load <file>.")
            return
        print(f"Records: {len(self.records)}")
        print("\n\n".join(render_record(record) for record in self.records))

    def show_fields(self) -> None:
        if not self.records:
            print("No data loaded. Use load <file>.")
            return
        print("Search fields: title\nField | Type | Filters")
        for field in self.records[0]:
            sample = next((row[field] for row in self.records if row.get(field, "") != ""), "")
            if sample.lower() in {"true", "false"}:
                kind, operators = "bool", "eq ne"
            else:
                try:
                    float(sample)
                    kind, operators = "number", "eq ne lt le gt ge"
                except ValueError:
                    kind = "str"
                    operators = "eq ne contains" if field != "url" else "-"
            print(f"{field} | {kind} | {operators}")

    def handle_filter(self, args: list[str]) -> None:
        action = args[0]
        if action == "add" and len(args) == 4:
            field, operator, value = args[1:]
            if not self.records:
                raise ValueError("Load data first")
            if field not in self.records[0]:
                raise ValueError(f"Unknown field: {field}")
            self.filters.append((field, operator, value))
            print(f"Added filter {len(self.filters)}: {field} {operator} {value}")
        elif action == "list" and len(args) == 1:
            if not self.filters:
                print("No filters")
            for index, (field, operator, value) in enumerate(self.filters, 1):
                print(f"{index}. {field} {operator} {value}")
        elif action == "remove" and len(args) == 2:
            index = int(args[1]) - 1
            if index < 0 or index >= len(self.filters):
                raise ValueError("Filter number out of range")
            self.filters.pop(index)
            print("Filter removed")
        elif action == "clear" and len(args) == 1:
            self.filters.clear()
            print("Filters cleared")
        else:
            raise ValueError("Invalid filter command")

    def search(self, query: str) -> None:
        if not self.records:
            raise ValueError("Load data first")
        start = time.perf_counter()
        query_tokens = set(normalize(query).split())
        matches: list[tuple[int, dict[str, str]]] = []
        for record in self.records:
            if not apply_filters(record, self.filters):
                continue
            title_tokens = normalize(record.get("title", "")).split()
            if query_tokens and not query_tokens.issubset(set(title_tokens)):
                continue
            relevance = sum(title_tokens.count(token) for token in query_tokens)
            matches.append((relevance, record))

        matches.sort(key=lambda item: (
            -(item[0] + (self.ratings.get(item[1].get("id", ""), 0) * 0.5
                         if self.variant["rating"] == "boost" else 0)),
            -item[0], item[1].get("title", "").casefold(),
        ))
        limit = self.variant["limit"]
        visible = matches if limit is None else matches[:limit]
        self.last_results = [record for _, record in visible]
        print(f"Found: {len(matches)}; displayed: {len(visible)}")
        for relevance, record in visible:
            print(render_record(record, query_tokens))
            if self.variant["rating"] == "boost":
                rating = self.ratings.get(record.get("id", ""))
                print(f"  Relevance: {relevance:.2f}")
                print(f"  Rating: {rating}/5" if rating else "  Rating: none")
                print(f"  Score: {relevance + (rating or 0) * 0.5:.2f}")
            print()
        print(f"Search time: {(time.perf_counter() - start) * 1000:.2f} ms")

    def save(self, filename: str) -> None:
        Path(filename).write_text(
            "\n\n".join(render_record(record) for record in self.last_results),
            encoding="utf-8",
        )
        print(f"Saved: {filename}")

    def rate(self, record_id: str, raw_rating: str) -> None:
        if self.variant["rating"] not in {"stars", "boost"}:
            raise ValueError("Ratings are disabled for this variant")
        rating = int(raw_rating)
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be an integer from 1 to 5")
        if record_id not in {record.get("id") for record in self.last_results}:
            raise ValueError("Rate a record from the last displayed results")
        self.ratings[record_id] = rating
        print(f"Rating: {record_id} — {rating}/5")

    def show_ratings(self) -> None:
        if self.variant["rating"] not in {"stars", "boost"}:
            raise ValueError("Ratings are disabled for this variant")
        if not self.ratings:
            print("No ratings")
        for record_id, rating in sorted(self.ratings.items()):
            print(f"{record_id}: {rating}/5")


def main() -> None:
    parser = argparse.ArgumentParser(description="Lab 1 catalog search")
    parser.add_argument("--variant", choices=VARIANTS, default="airports")
    args = parser.parse_args()
    CatalogSearchApp(args.variant).run()


if __name__ == "__main__":
    main()
