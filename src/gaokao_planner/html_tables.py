from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import csv
import re


def detect_html_encoding(raw: bytes) -> str:
    head = raw[:4096]
    for pattern in [
        rb"charset=['\"]?([A-Za-z0-9._-]+)",
        rb"encoding=['\"]?([A-Za-z0-9._-]+)",
    ]:
        match = re.search(pattern, head, flags=re.I)
        if match:
            return match.group(1).decode("ascii", errors="ignore")
    return "utf-8"


def decode_html(raw: bytes) -> str:
    encodings = []
    primary = detect_html_encoding(raw)
    if primary:
        encodings.append(primary)
    encodings.extend(["utf-8", "gb18030", "gbk", "gb2312"])

    seen: set[str] = set()
    for encoding in encodings:
        if encoding.lower() in seen:
            continue
        seen.add(encoding.lower())
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def normalize_cell_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class TableExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table_depth = 0
        self._current_table: list[list[str]] | None = None
        self._in_row = False
        self._current_row: list[str] = []
        self._in_cell = False
        self._cell_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "table":
            if self._table_depth == 0:
                self._current_table = []
            self._table_depth += 1
            return
        if self._table_depth == 0:
            return
        if tag == "tr":
            self._in_row = True
            self._current_row = []
        elif tag in {"td", "th"} and self._in_row:
            self._in_cell = True
            self._cell_parts = []
        elif tag == "br" and self._in_cell:
            self._cell_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "table":
            if self._table_depth > 0:
                self._table_depth -= 1
            if self._table_depth == 0 and self._current_table is not None:
                if any(any(cell for cell in row) for row in self._current_table):
                    self.tables.append(self._current_table)
                self._current_table = None
            return
        if self._table_depth == 0:
            return
        if tag in {"td", "th"} and self._in_cell:
            cell_text = normalize_cell_text("".join(self._cell_parts))
            self._current_row.append(cell_text)
            self._in_cell = False
            self._cell_parts = []
        elif tag == "tr" and self._in_row:
            if self._current_table is not None and any(cell for cell in self._current_row):
                self._current_table.append(self._current_row)
            self._in_row = False
            self._current_row = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)


@dataclass
class TableSummary:
    table_index: int
    row_count: int
    max_col_count: int
    first_row: list[str]


def extract_tables_from_file(path: str | Path) -> list[list[list[str]]]:
    raw = Path(path).read_bytes()
    html = decode_html(raw)
    parser = TableExtractor()
    parser.feed(html)
    return parser.tables


def summarize_tables(tables: list[list[list[str]]]) -> list[TableSummary]:
    summaries: list[TableSummary] = []
    for index, table in enumerate(tables, start=1):
        row_count = len(table)
        max_col_count = max((len(row) for row in table), default=0)
        first_row = table[0] if table else []
        summaries.append(
            TableSummary(
                table_index=index,
                row_count=row_count,
                max_col_count=max_col_count,
                first_row=first_row,
            )
        )
    return summaries


def write_table_csv(table: list[list[str]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(table)


def write_summary_csv(summaries: list[TableSummary], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["table_index", "row_count", "max_col_count", "first_row"])
        for summary in summaries:
            writer.writerow(
                [
                    summary.table_index,
                    summary.row_count,
                    summary.max_col_count,
                    " | ".join(summary.first_row),
                ]
            )
