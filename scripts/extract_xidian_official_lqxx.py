from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PLAN_SOURCE = Path("raw_data") / "engineering_api_official" / "xidian_211" / "xidian_guangxi_plan.json"
SCORE_SOURCE = Path("raw_data") / "engineering_api_official" / "xidian_211" / "xidian_guangxi_score_all.json"
PLAN_SOURCE_URL = "https://zsxc.xidian.edu.cn/lqxx/s/api/front/lqxx/getList"
SCORE_SOURCE_URL = "https://zsxc.xidian.edu.cn/lqxx/s/api/front/lqxx/getList"
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
SCHOOL_NAME = "西安电子科技大学"
SCHOOL_KEY = "xidian_211"
INTRO_URL = "https://zsxc.xidian.edu.cn/auth/zsdata/lqxx"


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
    return payload.get("list", [])


def normalize_requirement(value: str) -> str:
    return str(value).replace("+", ",").strip() or "物理类"


def normalize_plan_rows(rows: list[dict[str, object]]) -> tuple[list[dict[str, str]], dict[str, str]]:
    output: list[dict[str, str]] = []
    requirement_map: dict[str, str] = {}
    for index, row in enumerate(rows, start=1):
        province = str(row.get("sf", "")).strip()
        subject = str(row.get("klmc", "")).strip()
        if province != "广西" or "物理" not in subject:
            continue
        specialty = str(row.get("zymc", "")).strip()
        requirement = normalize_requirement(str(row.get("xkkm", "")).strip())
        normalized_specialty = normalize_name(specialty)
        requirement_map[normalized_specialty] = requirement
        output.append(
            {
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": str(row.get("nf", "")).strip() or "2025",
                "province": province,
                "type": (str(row.get("pcmc", "")).strip() or "本科普通批"),
                "subject_type": "物理类",
                "college": "",
                "specialty": specialty,
                "plan_count": str(row.get("jhrs", "")).strip(),
                "requirement": requirement,
                "selection_group": requirement,
                "campus": str(row.get("xqlx", "")).strip(),
                "remarks": str(row.get("remarks", "")).strip(),
                "weight": "",
                "record_id": f"xidian-plan-{index}",
                "source_url": PLAN_SOURCE_URL,
                "introduction_link": INTRO_URL,
                "source_slug": "xidian-official-lqxx",
            }
        )
    return output, requirement_map


def normalize_score_rows(
    rows: list[dict[str, object]],
    requirement_map: dict[str, str],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        province = str(row.get("sf", "")).strip()
        subject = str(row.get("klmc", "")).strip()
        if province != "广西" or "物理" not in subject:
            continue
        specialty = str(row.get("zymc", "")).strip()
        normalized_specialty = normalize_name(specialty)
        output.append(
            {
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": str(row.get("nf", "")).strip() or "2025",
                "province": province,
                "type": (str(row.get("pcmc", "")).strip() or "本科普通批"),
                "science_category": "物理类",
                "major": specialty,
                "requirement": requirement_map.get(normalized_specialty, normalize_requirement(str(row.get("xkkm", "")).strip())),
                "campus": str(row.get("xqlx", "")).strip(),
                "remarks": str(row.get("remarks", "")).strip(),
                "highest_score": str(row.get("zgf", "")).strip(),
                "minimum_score": str(row.get("zdf", "")).strip(),
                "lowest_score_ranking": str(row.get("zdfwc", "")).strip(),
                "record_id": f"xidian-score-{index}",
                "source_url": SCORE_SOURCE_URL,
            }
        )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Xidian Guangxi physics plan and score rows from official LQXX payloads."
    )
    parser.add_argument("--plan-source", type=Path, default=PLAN_SOURCE, help="Cached Xidian plan JSON.")
    parser.add_argument("--score-source", type=Path, default=SCORE_SOURCE, help="Cached Xidian score JSON.")
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "xidian_guangxi_plan_rows.csv",
        help="Structured Xidian plan output CSV.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "xidian_guangxi_score_rows.csv",
        help="Structured Xidian score output CSV.",
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
        default=Path("reports") / "xidian_official_guangxi_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_source_rows = load_payload_rows(args.plan_source)
    score_source_rows = load_payload_rows(args.score_source)

    plan_rows, requirement_map = normalize_plan_rows(plan_source_rows)
    score_rows = normalize_score_rows(score_source_rows, requirement_map)

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
    print(f"Wrote {len(plan_rows)} Xidian Guangxi plan rows and {len(score_rows)} score rows.")


if __name__ == "__main__":
    main()
