from __future__ import annotations

import argparse
import csv
from pathlib import Path


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

SCHOOL_SOURCES = [
    {
        "school_key": "beijing_jiaotong_211",
        "school_name": "北京交通大学招生与就业工作处",
        "plan_input": Path("clean_data/engineering_guangxi_seed/beijing_jiaotong_guangxi_plan_physics.csv"),
        "score_input": Path("clean_data/engineering_guangxi_seed/beijing_jiaotong_guangxi_score_major_physics.csv"),
        "summary_output": Path("reports/beijing_jiaotong_cached_guangxi_summary.csv"),
    },
    {
        "school_key": "zhongguo_dizhi_beijing_211",
        "school_name": "中国地质大学北京",
        "plan_input": Path("clean_data/engineering_guangxi_seed/zhongguo_dizhi_beijing_guangxi_plan_physics.csv"),
        "score_input": Path("clean_data/engineering_guangxi_seed/zhongguo_dizhi_beijing_guangxi_score_major_physics.csv"),
        "summary_output": Path("reports/zhongguo_dizhi_beijing_cached_guangxi_summary.csv"),
    },
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    return (
        str(value or "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def make_plan_rows(rows: list[dict[str, str]], school_key: str, school_name: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        normalized.append(
            {
                "school_name": school_name,
                "school_key": school_key,
                "year": normalize_text(row.get("year", "")),
                "province": normalize_text(row.get("province", "")),
                "type": normalize_text(row.get("type", "")),
                "subject_type": normalize_text(row.get("subject_type", "")),
                "college": "",
                "specialty": normalize_text(row.get("specialty", "")),
                "plan_count": normalize_text(row.get("plan_count", "")),
                "requirement": normalize_text(row.get("requirement", "")),
                "selection_group": normalize_text(row.get("selection_group", "")),
                "campus": normalize_text(row.get("campus", "")),
                "remarks": normalize_text(row.get("remarks", "")),
                "weight": "",
                "record_id": f"{school_key}-plan-import-{index}",
                "source_url": "",
                "introduction_link": "",
                "source_slug": normalize_text(row.get("source_payload", "")),
            }
        )
    return normalized


def make_score_rows(rows: list[dict[str, str]], school_key: str, school_name: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        normalized.append(
            {
                "school_name": school_name,
                "school_key": school_key,
                "year": normalize_text(row.get("year", "")),
                "province": normalize_text(row.get("province", "")),
                "type": normalize_text(row.get("type", "")),
                "science_category": normalize_text(row.get("subject_type", "")),
                "major": normalize_text(row.get("major", "")),
                "requirement": normalize_text(row.get("selection_group", "")),
                "campus": normalize_text(row.get("campus", "")),
                "remarks": normalize_text(row.get("remarks", "")),
                "highest_score": normalize_text(row.get("maximum_score", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "lowest_score_ranking": normalize_text(row.get("minimum_rank", "")),
                "record_id": f"{school_key}-score-import-{index}",
                "source_url": "",
            }
        )
    return normalized


def merge_rows(
    existing_rows: list[dict[str, str]],
    replacement_rows: list[dict[str, str]],
    *,
    school_key: str,
    fieldnames: list[str],
    dedupe_fields: list[str],
) -> list[dict[str, str]]:
    retained = [row for row in existing_rows if row.get("school_key", "") != school_key]
    merged: dict[tuple[str, ...], dict[str, str]] = {}
    for row in retained + replacement_rows:
        normalized_row = {field: row.get(field, "") for field in fieldnames}
        key = tuple(normalized_row.get(field, "") for field in dedupe_fields)
        merged[key] = normalized_row
    return list(merged.values())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import cached Guangxi BJTU/CUGB rows into merged engineering seed tables."
    )
    parser.add_argument(
        "--plan-merged",
        type=Path,
        default=Path("clean_data/engineering_guangxi_seed/guangxi_physics_plan_seed_merged.csv"),
        help="Merged Guangxi physics plan seed CSV.",
    )
    parser.add_argument(
        "--score-major-merged",
        type=Path,
        default=Path("clean_data/engineering_guangxi_seed/guangxi_physics_score_major_seed_merged.csv"),
        help="Merged Guangxi physics major-score seed CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    merged_plan_rows = read_rows(args.plan_merged)
    merged_score_rows = read_rows(args.score_major_merged)

    summary_rows: list[dict[str, str]] = []
    for config in SCHOOL_SOURCES:
        plan_rows = make_plan_rows(read_rows(config["plan_input"]), config["school_key"], config["school_name"])
        score_rows = make_score_rows(read_rows(config["score_input"]), config["school_key"], config["school_name"])
        merged_plan_rows = merge_rows(
            merged_plan_rows,
            plan_rows,
            school_key=config["school_key"],
            fieldnames=PLAN_FIELDS,
            dedupe_fields=["school_key", "year", "province", "specialty", "type", "subject_type", "selection_group"],
        )
        merged_score_rows = merge_rows(
            merged_score_rows,
            score_rows,
            school_key=config["school_key"],
            fieldnames=SCORE_FIELDS,
            dedupe_fields=["school_key", "year", "province", "major", "type", "science_category", "requirement"],
        )

        report_rows = [
            {
                "school_key": config["school_key"],
                "school_name": config["school_name"],
                "plan_rows_total": str(len(plan_rows)),
                "score_rows_total": str(len(score_rows)),
                "plan_years": "|".join(sorted({row["year"] for row in plan_rows if row.get("year")})),
                "score_years": "|".join(sorted({row["year"] for row in score_rows if row.get("year")})),
                "note": "缓存的官方 Guangxi 子集文件已重新并入主种子表。",
            }
        ]
        write_rows(config["summary_output"], report_rows, list(report_rows[0].keys()))
        summary_rows.extend(report_rows)

    merged_plan_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("specialty", "")))
    merged_score_rows.sort(key=lambda row: (row.get("school_key", ""), row.get("year", ""), row.get("major", "")))
    write_rows(args.plan_merged, merged_plan_rows, PLAN_FIELDS)
    write_rows(args.score_major_merged, merged_score_rows, SCORE_FIELDS)

    write_rows(
        Path("reports/import_cached_core_guangxi_rows_summary.csv"),
        summary_rows,
        ["school_key", "school_name", "plan_rows_total", "score_rows_total", "plan_years", "score_years", "note"],
    )
    print("Imported cached Guangxi rows for BJTU and CUGB into merged seed tables.")


if __name__ == "__main__":
    main()
