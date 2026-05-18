from __future__ import annotations

from pathlib import Path
import csv


def load_extracted_table(path: str | Path) -> list[list[str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.reader(file))


def _find_header_index(rows: list[list[str]], header_starts_with: str) -> int:
    for index, row in enumerate(rows):
        if row and row[0].strip() == header_starts_with:
            return index
    raise ValueError(f"Could not find header row starting with {header_starts_with!r}")


def build_score_rank_rows(
    table_path: str | Path,
    *,
    year: int,
    score_type: str,
    source_id: str,
) -> list[dict[str, str | int]]:
    rows = load_extracted_table(table_path)
    header_index = _find_header_index(rows, "总分")
    data_rows = rows[header_index + 1 :]

    result: list[dict[str, str | int]] = []
    for row in data_rows:
        if len(row) < 4 or not row[0].strip().isdigit():
            continue
        score = int(row[0].strip())
        count_at_score = int(row[1].strip())
        cum_count = int(row[2].strip())
        rank_start = int(row[3].strip())
        rank_end = cum_count
        result.append(
            {
                "year": year,
                "province": "广西",
                "subject_type": "物理类",
                "score_type": score_type,
                "score": score,
                "count_at_score": count_at_score,
                "cum_count": cum_count,
                "rank_start": rank_start,
                "rank_end": rank_end,
                "rank_method": "official_start_plus_conservative_end",
                "source_id": source_id,
                "data_quality": "official",
            }
        )
    return result


def build_rank_lookup(score_rank_rows: list[dict[str, str | int]]) -> dict[int, tuple[int, int]]:
    lookup: dict[int, tuple[int, int]] = {}
    for row in score_rank_rows:
        score = int(row["score"])
        lookup[score] = (int(row["rank_start"]), int(row["rank_end"]))
    return lookup


def build_admission_rows(
    table_path: str | Path,
    *,
    year: int,
    source_id: str,
    rank_lookup: dict[int, tuple[int, int]] | None = None,
) -> list[dict[str, str | int]]:
    rows = load_extracted_table(table_path)
    header_index = _find_header_index(rows, "院校代码")
    data_rows = rows[header_index + 1 :]

    result: list[dict[str, str | int]] = []
    for row in data_rows:
        if len(row) < 4 or not row[0].strip():
            continue
        if not row[0].strip().isdigit():
            continue
        min_score = int(row[3].strip()) if row[3].strip().isdigit() else ""
        min_rank_low = ""
        min_rank_high = ""
        min_rank_est = ""
        if isinstance(min_score, int) and rank_lookup and min_score in rank_lookup:
            min_rank_low, min_rank_high = rank_lookup[min_score]
            min_rank_est = min_rank_high
        result.append(
            {
                "year": year,
                "batch": "本科普通批",
                "subject_type": "物理类",
                "university_code": row[0].strip(),
                "university_name": row[1].strip(),
                "group_code": row[2].strip(),
                "min_score": min_score,
                "min_rank_est": min_rank_est,
                "min_rank_low": min_rank_low,
                "min_rank_high": min_rank_high,
                "remark": row[4].strip() if len(row) > 4 else "",
                "is_first_round": "true",
                "source_id": source_id,
                "data_quality": "official",
            }
        )
    return result


def write_dict_rows(rows: list[dict[str, str | int]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {output_path}")
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
