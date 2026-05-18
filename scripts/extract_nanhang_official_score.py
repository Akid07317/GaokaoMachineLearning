from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


SCORE_SOURCES = [
    Path("raw_data") / "official_api" / "nanhang_211" / "score_2024_guangxi_physics.json",
    Path("raw_data") / "official_api" / "nanhang_211" / "score_2025_guangxi_physics.json",
]
SCORE_SOURCE_URL = "https://zsservice.nuaa.edu.cn/zsw-admin/api/getAdmissionScore"
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
SCHOOL_NAME = "南京航空航天大学"
SCHOOL_KEY = "nanhang_211"


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


def drop_school_rows(rows: list[dict[str, str]], school_key: str) -> list[dict[str, str]]:
    return [row for row in rows if row.get("school_key", "") != school_key]


def load_rows(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    data = payload.get("data", [])
    return data if isinstance(data, list) else []


def normalize_score_rows(paths: list[Path]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for path in paths:
        for row in load_rows(path):
            province = str(row.get("province", "")).strip()
            subject = str(row.get("subject", "")).strip()
            row_type = str(row.get("type", "")).strip()
            if province != "广西" or "物理" not in subject or row_type not in {"普通类", "一批次"}:
                continue
            year = str(row.get("year", "")).strip()
            average = str(row.get("averageScore", "")).strip()
            remarks = []
            if row_type:
                remarks.append(f"类型={row_type}")
            if average:
                remarks.append(f"平均分={average}")
            college = str(row.get("college", "")).strip()
            if college:
                remarks.append(f"学院={college}")
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": year,
                    "province": province,
                    "type": "本科普通批",
                    "science_category": "物理类",
                    "major": str(row.get("specialty", "")).strip(),
                    "requirement": "物理类",
                    "campus": "",
                    "remarks": ";".join(remarks),
                    "highest_score": str(row.get("highestScore", "")).strip(),
                    "minimum_score": str(row.get("lowestScore", "")).strip(),
                    "lowest_score_ranking": "",
                    "record_id": f"nuaa-score-{year}-{row.get('id', '')}",
                    "source_url": SCORE_SOURCE_URL,
                }
            )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Nanhang Guangxi physics score rows from official public JSON."
    )
    parser.add_argument(
        "--score-source",
        type=Path,
        nargs="+",
        default=SCORE_SOURCES,
        help="Cached Nanhang score JSON files.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "nanhang_guangxi_score_rows.csv",
        help="Structured Nanhang score output CSV.",
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
        default=Path("reports") / "nanhang_official_guangxi_score_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    score_rows = normalize_score_rows([path for path in args.score_source if path.exists()])
    write_rows(score_rows, args.score_output, SCORE_FIELDS)

    merged_score_rows = merge_rows(
        drop_school_rows(read_rows(args.score_major_merged), SCHOOL_KEY),
        score_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_score_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(merged_score_rows, args.score_major_merged, SCORE_FIELDS)

    years = sorted({row["year"] for row in score_rows if row.get("year")})
    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "score_rows_total": str(len(score_rows)),
            "score_years": "|".join(years),
            "score_source_url": SCORE_SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Extracted {len(score_rows)} Nanhang Guangxi score rows.")


if __name__ == "__main__":
    main()
