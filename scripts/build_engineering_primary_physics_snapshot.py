from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "year",
    "province",
    "normalized_type",
    "subject_type",
    "data_completeness",
    "source_type",
    "plan_specialty_count_total",
    "plan_selection_group_count_total",
    "plan_campus_count_total",
    "total_plan_count",
    "score_campus",
    "minimum_score",
    "minimum_rank",
    "average_score",
    "maximum_score",
    "remarks",
    "record_id",
    "plan_source_url",
    "score_source_url",
    "source_slug",
]

TARGET_TOTAL = 32

PRIMARY_TYPE_MAP = {
    "普通类": "普通批主口径",
    "普通考生": "普通批主口径",
    "本科普通批": "普通批主口径",
    "普通批": "普通批主口径",
    "本科一批": "普通批主口径",
    "本科第一批": "普通批主口径",
}

EXCLUDED_TYPE_KEYWORDS = (
    "国家专项",
    "高校专项",
    "民族",
    "中外",
    "威海中外",
    "飞行技术",
    "单列",
    "预科",
    "南疆",
)


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


def is_primary_type(row_type: str) -> bool:
    text = normalize_text(row_type)
    if text in PRIMARY_TYPE_MAP:
        return True
    if any(keyword in text for keyword in EXCLUDED_TYPE_KEYWORDS):
        return False
    return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build normalized primary Guangxi physics snapshots from integrated type summaries."
    )
    parser.add_argument(
        "--integrated-type-source",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_school_year_type_integrated_summary_merged.csv",
        help="School-year-type integrated Guangxi summary CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_physics_snapshot_merged.csv",
        help="Primary Guangxi physics snapshot CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_snapshot_school_summary.csv",
        help="Primary snapshot school summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_snapshot_coverage_rollup.csv",
        help="Primary snapshot coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_primary_snapshot_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.integrated_type_source)

    primary_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()

    for row in rows:
        row_type = normalize_text(row.get("type", ""))
        if not is_primary_type(row_type):
            continue
        subject_type = normalize_text(row.get("subject_type", ""))
        if "物理" not in subject_type and "理工" not in subject_type and "物化" not in subject_type:
            continue

        school_key = normalize_text(row.get("school_key", ""))
        school_name = normalize_text(row.get("school_name", ""))
        year = normalize_text(row.get("year", ""))
        province = normalize_text(row.get("province", ""))
        normalized_type = PRIMARY_TYPE_MAP[row_type]
        completeness = normalize_text(row.get("data_completeness", ""))
        record_id = f"{school_key}-primary-snapshot-{year}-{subject_type}"

        primary_rows.append(
            {
                "school_name": school_name,
                "school_key": school_key,
                "year": year,
                "province": province,
                "normalized_type": normalized_type,
                "subject_type": subject_type,
                "data_completeness": completeness,
                "source_type": row_type,
                "plan_specialty_count_total": normalize_text(row.get("plan_specialty_count_total", "")),
                "plan_selection_group_count_total": normalize_text(row.get("plan_selection_group_count_total", "")),
                "plan_campus_count_total": normalize_text(row.get("plan_campus_count_total", "")),
                "total_plan_count": normalize_text(row.get("total_plan_count", "")),
                "score_campus": normalize_text(row.get("score_campus", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": normalize_text(row.get("minimum_rank", "")),
                "average_score": normalize_text(row.get("average_score", "")),
                "maximum_score": normalize_text(row.get("maximum_score", "")),
                "remarks": ";".join(
                    part
                    for part in [
                        "学校-年份-类型级摘要进一步归一化为广西物理类普通批主口径快照",
                        f"原始类型={row_type}",
                        normalize_text(row.get("remarks", "")),
                    ]
                    if part
                ),
                "record_id": record_id,
                "plan_source_url": normalize_text(row.get("plan_source_url", "")),
                "score_source_url": normalize_text(row.get("score_source_url", "")),
                "source_slug": "official_primary_physics_snapshot",
            }
        )
        school_counter[school_key] += 1

    primary_rows.sort(key=lambda item: (item["school_key"], item["year"], item["subject_type"]))
    write_rows(args.output, primary_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in primary_rows if row["school_key"] == school_key),
                "",
            ),
            "primary_snapshot_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_snapshot_rows"],
    )

    plan_and_score_schools = sum(
        1
        for school_key in school_counter
        if any(
            row["school_key"] == school_key and row["data_completeness"] == "plan_and_score"
            for row in primary_rows
        )
    )
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_snapshot_schools", "value": str(len(school_counter))},
        {"metric": "primary_snapshot_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "primary_snapshot_plan_and_score_schools", "value": str(plan_and_score_schools)},
        {
            "metric": "primary_snapshot_plan_only_or_score_only_schools",
            "value": str(len(school_counter) - plan_and_score_schools),
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in primary_rows if row["school_key"] == school_key),
                "",
            ),
            "primary_snapshot_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "primary_snapshot_rows"],
    )


if __name__ == "__main__":
    main()
