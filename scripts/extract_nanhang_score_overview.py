from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "type",
    "subject_type",
    "campus",
    "minimum_score",
    "minimum_rank",
    "average_score",
    "maximum_score",
    "remarks",
    "record_id",
    "source_url",
]

SCHOOL_NAME = "南京航空航天大学"
SCHOOL_KEY = "nanhang_211"
SOURCE_URL = "https://zsservice.nuaa.edu.cn/zsw-admin/api/getAdmissionScoreOverview"


def read_json_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    data = payload.get("data", [])
    return data if isinstance(data, list) else []


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: object) -> str:
    return str(value or "").strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Nanhang Guangxi score overview rows from cached official API JSON."
    )
    parser.add_argument(
        "--inputs",
        type=Path,
        nargs="+",
        default=[Path("raw_data/official_api/nanhang_211/score_overview_2024.json")],
        help="Cached Nanhang overview JSON files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data/official_api_structured/nanhang_guangxi_score_overview_rows.csv"),
        help="Structured overview output CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports/nanhang_official_guangxi_overview_summary.csv"),
        help="Summary CSV path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    normalized: list[dict[str, str]] = []
    for source in args.inputs:
        for item in read_json_rows(source):
            if normalize_text(item.get("province")) != "广西":
                continue
            subject_type = normalize_text(item.get("subject"))
            if "物理" not in subject_type:
                continue
            year = normalize_text(item.get("year"))
            row_type = normalize_text(item.get("type"))
            normalized.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": year,
                    "province": "广西",
                    "type": row_type or "普通类",
                    "subject_type": subject_type,
                    "campus": "",
                    "minimum_score": normalize_text(item.get("lowestScore")),
                    "minimum_rank": "",
                    "average_score": normalize_text(item.get("averageScore")),
                    "maximum_score": normalize_text(item.get("highestScore")),
                    "remarks": f"来源=官方录取概况接口;类型={row_type or '普通类'}",
                    "record_id": f"nanhang-overview-{year}-{row_type or 'normal'}",
                    "source_url": SOURCE_URL,
                }
            )

    deduped: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in normalized:
        key = (row["year"], row["province"], row["type"])
        deduped[key] = row
    output_rows = list(deduped.values())
    output_rows.sort(key=lambda row: (row["year"], row["type"]))
    write_rows(args.output, output_rows, FIELDS)

    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "rows_total": str(len(output_rows)),
            "rows_by_year": "|".join(
                f"{year}:{count}"
                for year, count in sorted(
                    {
                        row["year"]: sum(1 for item in output_rows if item["year"] == row["year"])
                        for row in output_rows
                    }.items()
                )
            ),
            "note": "官方录取概况接口中广西物理类学校级摘要行。",
        }
    ]
    write_rows(args.summary_output, summary_rows, list(summary_rows[0].keys()))
    print(f"Wrote {len(output_rows)} Nanhang Guangxi score-overview rows.")


if __name__ == "__main__":
    main()
