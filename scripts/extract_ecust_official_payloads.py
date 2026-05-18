from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PLAN_SOURCES = [
    Path("raw_data") / "engineering_api_official" / "huadong_ligong_211" / "ecust_zsjh_2024_guangxi.json",
    Path("raw_data") / "engineering_api_official" / "huadong_ligong_211" / "ecust_zsjh_2025_guangxi.json",
]
SCORE_SOURCES = [
    Path("raw_data") / "engineering_api_official" / "huadong_ligong_211" / "ecust_lnfs_2024_guangxi.json",
    Path("raw_data") / "engineering_api_official" / "huadong_ligong_211" / "ecust_lnfs_2025_guangxi.json",
]
PLAN_SOURCE_URL = "https://bkzsdata.ecust.edu.cn/lqxx/s/api/front/lqxx2/getList?type=zsjh"
SCORE_SOURCE_URL = "https://bkzsdata.ecust.edu.cn/lqxx/s/api/front/lqxx2/getList?type=lnfs"
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
SCHOOL_NAME = "华东理工大学"
SCHOOL_KEY = "huadong_ligong_211"
INTRO_URL = "https://bkzsdata.ecust.edu.cn/zsdata/lqxx/"


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
    rows = payload.get("list", [])
    return rows if isinstance(rows, list) else []


def normalize_requirement(value: object) -> str:
    text = str(value or "").replace("+", ",").strip()
    return text or "物理类"


def normalize_plan_rows(paths: list[Path]) -> tuple[list[dict[str, str]], dict[str, str]]:
    output: list[dict[str, str]] = []
    requirement_map: dict[str, str] = {}
    for path in paths:
        for row in load_rows(path):
            province = str(row.get("sf", "")).strip()
            subject = str(row.get("klmc", "")).strip()
            row_type = str(row.get("zslb", "")).strip()
            if province != "广西" or "物理" not in subject or row_type != "普通类":
                continue
            year = str(row.get("nf", "")).strip()
            specialty = str(row.get("zymc", "")).strip()
            requirement = normalize_requirement(row.get("xkyq"))
            requirement_map[specialty] = requirement
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": year,
                    "province": province,
                    "type": str(row.get("pcmc", "")).strip() or "本科普通批",
                    "subject_type": "物理类",
                    "college": "",
                    "specialty": specialty,
                    "plan_count": str(row.get("jhrs", "")).strip(),
                    "requirement": requirement,
                    "selection_group": requirement,
                    "campus": str(row.get("xqlx", "")).strip(),
                    "remarks": str(row.get("zybz", "")).strip(),
                    "weight": "",
                    "record_id": f"ecust-plan-{year}-{specialty}",
                    "source_url": PLAN_SOURCE_URL,
                    "introduction_link": INTRO_URL,
                    "source_slug": "ecust-official-lqxx2",
                }
            )
    return output, requirement_map


def normalize_score_rows(paths: list[Path], requirement_map: dict[str, str]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for path in paths:
        for row in load_rows(path):
            province = str(row.get("sf", "")).strip()
            subject = str(row.get("klmc", "")).strip()
            row_type = str(row.get("zslb", "")).strip()
            if province != "广西" or "物理" not in subject or row_type != "普通类":
                continue
            year = str(row.get("nf", "")).strip()
            major = str(row.get("zymc", "")).strip()
            output.append(
                {
                    "school_name": SCHOOL_NAME,
                    "school_key": SCHOOL_KEY,
                    "year": year,
                    "province": province,
                    "type": str(row.get("pcmc", "")).strip() or "本科普通批",
                    "science_category": "物理类",
                    "major": major,
                    "requirement": requirement_map.get(major, normalize_requirement(row.get("xkyq"))),
                    "campus": str(row.get("xqlx", "")).strip(),
                    "remarks": str(row.get("remarks", "")).strip(),
                    "highest_score": str(row.get("zgf", "")).strip(),
                    "minimum_score": str(row.get("zdf", "")).strip(),
                    "lowest_score_ranking": str(row.get("zdfwc", "")).strip(),
                    "record_id": f"ecust-score-{year}-{major}",
                    "source_url": SCORE_SOURCE_URL,
                }
            )
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract ECUST Guangxi physics rows from cached official JSON payloads.")
    parser.add_argument("--plan-source", type=Path, nargs="+", default=PLAN_SOURCES)
    parser.add_argument("--score-source", type=Path, nargs="+", default=SCORE_SOURCES)
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "huadong_ligong_guangxi_plan_rows.csv",
    )
    parser.add_argument(
        "--score-output",
        type=Path,
        default=Path("clean_data") / "official_api_structured" / "huadong_ligong_guangxi_score_rows.csv",
    )
    parser.add_argument(
        "--plan-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_plan_seed_merged.csv",
    )
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_physics_score_major_seed_merged.csv",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("reports") / "huadong_ligong_official_guangxi_summary.csv",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    plan_rows, requirement_map = normalize_plan_rows([path for path in args.plan_source if path.exists()])
    score_rows = normalize_score_rows([path for path in args.score_source if path.exists()], requirement_map)

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
            "years": "|".join(sorted({row["year"] for row in plan_rows + score_rows if row.get("year")})),
            "plan_source_url": PLAN_SOURCE_URL,
            "score_source_url": SCORE_SOURCE_URL,
        }
    ]
    write_rows(summary_rows, args.summary_output, list(summary_rows[0].keys()))
    print(f"Extracted {len(plan_rows)} ECUST Guangxi plan rows and {len(score_rows)} score rows.")


if __name__ == "__main__":
    main()
