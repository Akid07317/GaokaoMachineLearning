from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PLAN_SOURCE = Path("raw_data") / "official_api" / "wuhan_ligong_211" / "plan_2025_guangxi_physics.json"
SCORE_SOURCES = [
    Path("raw_data") / "official_api" / "wuhan_ligong_211" / "score_2025_guangxi_physics.json",
    Path("raw_data") / "official_api" / "wuhan_ligong_211" / "score_2024_guangxi_physics.json",
]
PLAN_SOURCE_URL = "https://zs.whut.edu.cn/enroll-info/recruitScheme/selRecruitByProvinceAndYearAndSubjectType.do"
SCORE_SOURCE_URL = "https://zs.whut.edu.cn/enroll-info/recruitByMajor/selRecruitByProvinceAndYearAndSubjectType.do"
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
SCHOOL_NAME = "武汉理工大学"
SCHOOL_KEY = "wuhan_ligong_211"
INTRO_URL = "https://zs.whut.edu.cn/enroll-info/recruitScheme/list.do"


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


def normalize_text(value: object) -> str:
    return (
        str(value or "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def load_plan_rows(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ext = payload.get("ext", {})
    if isinstance(ext, dict) and isinstance(ext.get("recruitSchemeList"), list):
        return ext["recruitSchemeList"]
    return []


def load_score_rows(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ext = payload.get("ext", {})
    if isinstance(ext, dict) and isinstance(ext.get("recruitByMajorList"), list):
        return ext["recruitByMajorList"]
    return []


def normalize_requirement(value: str) -> str:
    text = normalize_text(value)
    text = text.replace("(2门科目考生均须选考方可报考)", "")
    text = text.replace("2门科目考生均须选考方可报考", "")
    text = text.replace("()", "")
    return text.strip() or "物理类"


def normalize_plan_rows(rows: list[dict[str, object]]) -> tuple[list[dict[str, str]], dict[str, str]]:
    output: list[dict[str, str]] = []
    requirement_map: dict[str, str] = {}
    for row in rows:
        province = normalize_text(row.get("province"))
        subject_type = normalize_text(row.get("subjectType"))
        row_type = normalize_text(row.get("type"))
        if province != "广西" or subject_type != "物理类" or row_type != "普通类":
            continue
        specialty = normalize_text(row.get("majorType"))
        requirement = normalize_requirement(str(row.get("electiveSubject", "")).replace("2门科目考生均须选考方可报考", "").strip())
        requirement_map[specialty] = requirement
        output.append(
            {
                "school_name": SCHOOL_NAME,
                "school_key": SCHOOL_KEY,
                "year": normalize_text(row.get("year")) or "2025",
                "province": province,
                "type": "本科普通批",
                "subject_type": "物理类",
                "college": "",
                "specialty": specialty,
                "plan_count": normalize_text(row.get("recruitNum")),
                "requirement": requirement,
                "selection_group": requirement,
                "campus": "",
                "remarks": normalize_text(row.get("remarks")),
                "weight": "",
                "record_id": f"whut-plan-{normalize_text(row.get('year'))}-{normalize_text(row.get('id'))}",
                "source_url": PLAN_SOURCE_URL,
                "introduction_link": INTRO_URL,
                "source_slug": "whut-official-api",
            }
        )
    return output, requirement_map


def normalize_score_rows(
    groups: list[list[dict[str, object]]],
    requirement_map: dict[str, str],
) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for rows in groups:
        for row in rows:
            province = normalize_text(row.get("province"))
            subject_type = normalize_text(row.get("subjectType"))
            row_type = normalize_text(row.get("type"))
            if province != "广西" or subject_type != "物理类" or row_type != "普通类":
                continue
            major = normalize_text(row.get("majorType"))
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": normalize_text(row.get("year")),
                    "province": province,
                    "type": "本科普通批",
                    "science_category": "物理类",
                    "major": major,
                    "requirement": requirement_map.get(major, normalize_requirement(row.get("electiveSubject"))),
                    "campus": "",
                    "remarks": normalize_text(row.get("remarks")),
                    "highest_score": normalize_text(row.get("zgf")),
                    "minimum_score": normalize_text(row.get("zdf")),
                    "lowest_score_ranking": normalize_text(row.get("wcz")),
                    "record_id": f"whut-score-{normalize_text(row.get('year'))}-{normalize_text(row.get('id'))}",
                    "source_url": SCORE_SOURCE_URL,
                }
            )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Wuhan Ligong Guangxi physics plan and score rows from official API payloads."
    )
    parser.add_argument("--plan-source", type=Path, default=PLAN_SOURCE, help="Cached Wuhan Ligong plan JSON.")
    parser.add_argument(
        "--score-source",
        type=Path,
        nargs="+",
        default=SCORE_SOURCES,
        help="Cached Wuhan Ligong score JSON files.",
    )
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "wuhan_ligong_guangxi_plan_rows.csv",
        help="Structured Wuhan Ligong plan output CSV.",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "wuhan_ligong_guangxi_score_rows.csv",
        help="Structured Wuhan Ligong score output CSV.",
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
        help="Merged Guangxi physics major-score seed CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "wuhan_ligong_official_guangxi_summary.csv",
        help="Summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_rows, requirement_map = normalize_plan_rows(load_plan_rows(args.plan_source))
    score_rows = normalize_score_rows([load_score_rows(path) for path in args.score_source], requirement_map)

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
    print(f"Extracted {len(plan_rows)} Wuhan Ligong Guangxi plan rows and {len(score_rows)} score rows.")


if __name__ == "__main__":
    main()
