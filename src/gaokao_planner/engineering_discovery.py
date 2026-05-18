from __future__ import annotations

from pathlib import Path
import csv


def read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def build_engineering_seed_rows(
    engineering_rows: list[dict[str, str]],
    discovery_rows: list[dict[str, str]],
    *,
    max_depth: int,
    max_pages: int,
) -> tuple[list[dict[str, str]], list[str]]:
    discovery_by_id = {row.get("seed_id", "").strip(): row for row in discovery_rows}
    output_rows: list[dict[str, str]] = []
    missing_seed_ids: list[str] = []

    for engineering_row in engineering_rows:
        seed_id = engineering_row.get("seed_id", "").strip()
        discovery_row = discovery_by_id.get(seed_id)
        if discovery_row is None:
            missing_seed_ids.append(seed_id)
            continue

        output_row = dict(discovery_row)
        output_row["max_depth"] = str(max_depth)
        output_row["max_pages"] = str(max_pages)
        notes = output_row.get("notes", "").strip()
        suffix = "工程池520全量抓取"
        output_row["notes"] = f"{notes} {suffix}".strip()
        output_rows.append(output_row)

    return output_rows, missing_seed_ids


def write_rows(rows: list[dict[str, str]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with output_path.open("w", encoding="utf-8", newline="") as file:
            file.write("")
        return

    fieldnames = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
