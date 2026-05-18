from __future__ import annotations

import argparse
import csv
from pathlib import Path


SCHOOL_NAME = "北京工业大学"
SCHOOL_KEY = "beijing_gongye_211"
SOURCE_ROWS = [
    {
        "year": "2022",
        "minimum_score": "575",
        "lowest_score_ranking": "8400",
        "source_url": "https://admissions.bjut.edu.cn/info/1015/1442.htm",
    },
    {
        "year": "2023",
        "minimum_score": "592",
        "lowest_score_ranking": "6500",
        "source_url": "https://admissions.bjut.edu.cn/info/1015/1572.htm",
    },
    {
        "year": "2024",
        "minimum_score": "595",
        "lowest_score_ranking": "8700",
        "source_url": "https://admissions.bjut.edu.cn/info/1015/1775.htm",
    },
]
SCORE_FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "type",
    "science_category",
    "major",
    "requirement",
    "campus",
    "remarks",
    "highest_score",
    "minimum_score",
    "lowest_score_ranking",
    "record_id",
    "source_url",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def merge_rows(
    existing_rows: list[dict[str, str]],
    new_rows: list[dict[str, str]],
    key_fields: list[str],
) -> list[dict[str, str]]:
    merged: dict[tuple[str, ...], dict[str, str]] = {}
    for row in existing_rows + new_rows:
        key = tuple(row.get(field, "") for field in key_fields)
        merged[key] = row
    return list(merged.values())


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in SOURCE_ROWS:
        rows.append(
            {
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": row["year"],
                "province": "广西",
                "type": "本科普通批",
                "science_category": "物理类",
                "major": "普通专业(京外省份)",
                "requirement": "",
                "campus": "",
                "remarks": "统计口径=京外省份普通类录取分数统计;来源=官方图片页提档线与全省排位",
                "highest_score": "",
                "minimum_score": row["minimum_score"],
                "lowest_score_ranking": row["lowest_score_ranking"],
                "record_id": f"bjut-summary-{row['year']}-guangxi",
                "source_url": row["source_url"],
            }
        )
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize BJUT official Guangxi score summary rows from historical image pages."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "official_html_structured" / "beijing_gongye_guangxi_score_summary_rows.csv",
        help="Structured BJUT historical score summary output CSV.",
    )
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_major_seed_merged.csv",
        help="Merged Guangxi physics score seed CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "beijing_gongye_historical_score_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = build_rows()
    write_rows(rows, args.output, SCORE_FIELDS)

    existing_rows = [
        row
        for row in read_rows(args.score_major_merged)
        if not (row.get("school_key") == SCHOOL_KEY and row.get("record_id", "").startswith("bjut-summary-"))
    ]
    merged_rows = merge_rows(
        existing_rows,
        rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(merged_rows, args.score_major_merged, SCORE_FIELDS)

    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "score_rows_total": str(len(rows)),
            "score_rows_by_year": "|".join(f"{row['year']}:1" for row in rows),
            "note": "2022-2024 官方图片页广西普通专业提档线与位次摘要",
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Extracted {len(rows)} BJUT historical Guangxi score summary rows.")


if __name__ == "__main__":
    main()
