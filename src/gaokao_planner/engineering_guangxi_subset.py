from __future__ import annotations

from pathlib import Path
import csv


def read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def filter_guangxi_physics(
    rows: list[dict[str, str]],
    *,
    province_field: str,
    category_field: str,
) -> list[dict[str, str]]:
    accepted = {"物理类", "物理"}
    return [
        row
        for row in rows
        if row.get(province_field, "") == "广西"
        and (
            row.get(category_field, "") in accepted
            or "物理" in row.get(category_field, "")
        )
    ]


def attach_school(rows: list[dict[str, str]], school_name: str, school_key: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        merged = dict(row)
        merged["school_name"] = school_name
        merged["school_key"] = school_key
        out.append(merged)
    return out
