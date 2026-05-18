from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


SOURCE_FILES = [
    Path("raw_data") / "official_api" / "hehai_211" / "hehai_guangxi_score_2024.json",
    Path("raw_data") / "official_api" / "hehai_211" / "hehai_guangxi_score_2025.json",
]
SOURCE_URL = "https://zsw.hhu.edu.cn/api/lsfs/fsList"
OUTPUT_FIELDS = [
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
SCHOOL_NAME = "河海大学"
SCHOOL_KEY = "hehai_211"


def load_payload_rows(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload.get("data", [])
    return payload


def normalize_text(value: object) -> str:
    return (
        str(value or "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def normalize_subject_type(discipline: str) -> str:
    text = normalize_text(discipline)
    if "物理" in text and "化学" in text:
        return "物理+化学"
    if "物理" in text:
        return "物理"
    if "历史" in text and "思想政治" in text:
        return "历史+思想政治"
    if "历史" in text:
        return "历史+不限"
    return text


def build_rows(payload_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in payload_rows:
        major = normalize_text(row.get("major"))
        if "投档线" not in major:
            continue
        province = normalize_text(row.get("province") or row.get("province_text"))
        if province != "广西":
            continue
        discipline = normalize_text(row.get("discipline"))
        remarks = ";".join(
            part
            for part in [
                f"专业组={normalize_text(row.get('group'))}" if normalize_text(row.get("group")) else "",
                f"投档线类型={major}",
                "来源=河海大学官方历史录取API",
            ]
            if part
        )
        output.append(
            {
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": normalize_text(row.get("year")),
                "province": province,
                "type": normalize_text(row.get("type") or row.get("type_text")),
                "subject_type": normalize_subject_type(discipline),
                "campus": normalize_text(row.get("group")),
                "minimum_score": normalize_text(row.get("filescore")),
                "minimum_rank": "",
                "average_score": "",
                "maximum_score": normalize_text(row.get("highestscore")),
                "remarks": remarks,
                "record_id": f"hehai-summary-{normalize_text(row.get('year'))}-{normalize_text(row.get('id'))}",
                "source_url": SOURCE_URL,
            }
        )
    return output


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Hehai official Guangxi school-level score summary rows from cached public API payloads."
    )
    parser.add_argument(
        "--sources",
        type=Path,
        nargs="+",
        default=SOURCE_FILES,
        help="Cached Hehai Guangxi score JSON files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "hehai_guangxi_score_summary_rows.csv",
        help="Structured Hehai Guangxi school-level score summary CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "hehai_official_guangxi_score_summary.csv",
        help="School-level extraction summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows: list[dict[str, str]] = []
    for source in args.sources:
        rows.extend(build_rows(load_payload_rows(source)))
    rows.sort(key=lambda row: (row["year"], row["type"], row["subject_type"], row["record_id"]))
    write_rows(args.output, rows)

    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "score_summary_rows": str(len(rows)),
            "years": "|".join(sorted({row["year"] for row in rows if row["year"]})),
            "source_url": SOURCE_URL,
        }
    ]
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["school_key", "school_name", "score_summary_rows", "years", "source_url"],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Wrote {len(rows)} Hehai Guangxi school-level score summary rows.")


if __name__ == "__main__":
    main()
