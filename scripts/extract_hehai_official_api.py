from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PLAN_SOURCE = Path("raw_data") / "official_api" / "hehai_211" / "hehai_guangxi_plan_2025.json"
SCORE_SOURCES = [
    Path("raw_data") / "official_api" / "hehai_211" / "hehai_guangxi_score_2025.json",
    Path("raw_data") / "official_api" / "hehai_211" / "hehai_guangxi_score_2024.json",
]
PLAN_SOURCE_URL = "https://zsw.hhu.edu.cn/api/zsjh/jhList"
SCORE_SOURCE_URL = "https://zsw.hhu.edu.cn/api/lsfs/fsList"
PLAN_FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "type",
    "subject_type",
    "college",
    "specialty",
    "plan_count",
    "requirement",
    "selection_group",
    "campus",
    "remarks",
    "weight",
    "record_id",
    "source_url",
    "introduction_link",
    "source_slug",
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
SCHOOL_NAME = "河海大学"
SCHOOL_KEY = "hehai_211"
INTRO_URL = "https://zsw.hhu.edu.cn/zhaoshengjihua.html"


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


def normalize_name(text: str) -> str:
    return (
        str(text)
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def load_payload_rows(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("data", [])


def normalize_requirement(value: str) -> str:
    requirement = str(value).replace("+", ",").strip()
    return requirement or "物理类"


def normalize_plan_rows(rows: list[dict[str, object]]) -> tuple[list[dict[str, str]], dict[str, str]]:
    output: list[dict[str, str]] = []
    requirement_map: dict[str, str] = {}
    for row in rows:
        province = str(row.get("province", "")).strip()
        row_type = str(row.get("type", "")).strip()
        requirement = normalize_requirement(str(row.get("requirement", "")).strip())
        if province != "广西" or row_type != "普通类" or "物理" not in requirement:
            continue
        specialty = str(row.get("major", "")).strip()
        normalized_specialty = normalize_name(specialty)
        requirement_map[normalized_specialty] = requirement
        record_id = f"hehai-plan-{row.get('year', '')}-{row.get('id', '')}"
        output.append(
            {
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": str(row.get("year", "")).strip() or "2025",
                "province": province,
                "type": "本科普通批",
                "subject_type": "物理类",
                "college": "",
                "specialty": specialty,
                "plan_count": str(row.get("plannnumber", "")).strip(),
                "requirement": requirement,
                "selection_group": str(row.get("serialnumber", "")).strip() or requirement,
                "campus": str(row.get("campus", "")).strip(),
                "remarks": str(row.get("remark", "")).strip(),
                "weight": "",
                "record_id": record_id,
                "source_url": PLAN_SOURCE_URL,
                "introduction_link": INTRO_URL,
                "source_slug": "hehai-official-api",
            }
        )
    return output, requirement_map


def normalize_score_rows(
    payload_groups: list[list[dict[str, object]]],
    requirement_map: dict[str, str],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for rows in payload_groups:
        for row in rows:
            province = str(row.get("province", "")).strip()
            row_type = str(row.get("type", "")).strip()
            discipline = str(row.get("discipline", "")).strip()
            if province != "广西" or row_type != "普通类" or "物理" not in discipline:
                continue
            major = str(row.get("major", "")).strip()
            normalized_major = normalize_name(major)
            record_id = f"hehai-score-{row.get('year', '')}-{row.get('id', '')}"
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": str(row.get("year", "")).strip(),
                    "province": province,
                    "type": "本科普通批",
                    "science_category": "物理类",
                    "major": major,
                    "requirement": requirement_map.get(normalized_major, normalize_requirement(discipline)),
                    "campus": "",
                    "remarks": str(row.get("group", "")).strip(),
                    "highest_score": str(row.get("highestscore", "")).strip(),
                    "minimum_score": str(row.get("filescore", "")).strip(),
                    "lowest_score_ranking": "",
                    "record_id": record_id,
                    "source_url": SCORE_SOURCE_URL,
                }
            )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Hehai Guangxi physics plan and score rows from official public API payloads."
    )
    parser.add_argument("--plan-source", type=Path, default=PLAN_SOURCE, help="Cached Hehai plan JSON.")
    parser.add_argument(
        "--score-source",
        type=Path,
        nargs="+",
        default=SCORE_SOURCES,
        help="Cached Hehai score JSON files.",
    )
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "hehai_guangxi_plan_rows.csv",
        help="Structured Hehai plan output CSV.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "hehai_guangxi_score_rows.csv",
        help="Structured Hehai score output CSV.",
    )
    parser.add_argument(
        "--plan-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_seed_merged.csv",
        help="Merged Guangxi physics plan seed CSV.",
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
        default=Path("reports") / "hehai_official_guangxi_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_rows, requirement_map = normalize_plan_rows(load_payload_rows(args.plan_source))
    score_payload_groups = [load_payload_rows(path) for path in args.score_source]
    score_rows = normalize_score_rows(score_payload_groups, requirement_map)

    write_rows(plan_rows, args.plan_output, PLAN_FIELDS)
    write_rows(score_rows, args.score_output, SCORE_FIELDS)

    merged_plan_rows = merge_rows(
        drop_school_rows(read_rows(args.plan_merged), SCHOOL_KEY),
        plan_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_plan_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("specialty", "")))
    write_rows(merged_plan_rows, args.plan_merged, PLAN_FIELDS)

    merged_score_rows = merge_rows(
        drop_school_rows(read_rows(args.score_major_merged), SCHOOL_KEY),
        score_rows,
        ["school_key", "year", "province", "record_id", "source_url"],
    )
    merged_score_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(merged_score_rows, args.score_major_merged, SCORE_FIELDS)

    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "plan_rows": str(len(plan_rows)),
            "score_rows_total": str(len(score_rows)),
            "plan_source_url": PLAN_SOURCE_URL,
            "score_source_url": SCORE_SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))


if __name__ == "__main__":
    main()
