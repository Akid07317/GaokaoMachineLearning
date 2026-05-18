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

COMPLETENESS_RANK = {
    "plan_and_score": 3,
    "score_only": 2,
    "plan_only": 1,
}


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


def parse_int(value: str) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def row_score(row: dict[str, str]) -> tuple[int, int, int, int, int]:
    completeness = COMPLETENESS_RANK.get(normalize_text(row.get("data_completeness", "")), 0)
    total_plan = parse_int(row.get("total_plan_count", "")) or 0
    has_min_score = 1 if normalize_text(row.get("minimum_score", "")) else 0
    has_min_rank = 1 if normalize_text(row.get("minimum_rank", "")) else 0
    max_score = parse_int(row.get("maximum_score", "")) or 0
    return (completeness, total_plan, has_min_score, has_min_rank, max_score)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build canonical primary Guangxi physics snapshots by selecting the best row per school-year-subject."
    )
    parser.add_argument(
        "--primary-source",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_physics_snapshot_merged.csv",
        help="Primary Guangxi physics snapshot CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_physics_canonical_snapshot_merged.csv",
        help="Canonical primary Guangxi physics snapshot CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_canonical_snapshot_school_summary.csv",
        help="Canonical primary snapshot school summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_canonical_snapshot_coverage_rollup.csv",
        help="Canonical primary snapshot coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_primary_canonical_snapshot_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.primary_source)

    best_by_key: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (
            normalize_text(row.get("school_key", "")),
            normalize_text(row.get("year", "")),
            normalize_text(row.get("subject_type", "")),
        )
        current = best_by_key.get(key)
        if current is None or row_score(row) > row_score(current):
            best_by_key[key] = row

    canonical_rows = []
    school_counter: Counter[str] = Counter()
    for key, row in sorted(best_by_key.items()):
        out = dict(row)
        out["remarks"] = ";".join(
            part
            for part in [
                "学校-年份-主口径快照按完整度与信息量筛选最佳记录",
                f"原始类型={normalize_text(row.get('source_type', ''))}",
                normalize_text(row.get("remarks", "")),
            ]
            if part
        )
        out["record_id"] = f"{normalize_text(row.get('school_key', ''))}-primary-canonical-{normalize_text(row.get('year', ''))}-{normalize_text(row.get('subject_type', ''))}"
        out["source_slug"] = "official_primary_physics_canonical_snapshot"
        canonical_rows.append(out)
        school_counter[normalize_text(row.get("school_key", ""))] += 1

    write_rows(args.output, canonical_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in canonical_rows if normalize_text(row["school_key"]) == school_key),
                "",
            ),
            "primary_canonical_snapshot_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_canonical_snapshot_rows"],
    )

    plan_and_score_schools = sum(
        1
        for school_key in school_counter
        if any(
            normalize_text(row.get("school_key", "")) == school_key
            and normalize_text(row.get("data_completeness", "")) == "plan_and_score"
            for row in canonical_rows
        )
    )
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_canonical_snapshot_schools", "value": str(len(school_counter))},
        {
            "metric": "primary_canonical_snapshot_coverage_ratio",
            "value": f"{len(school_counter) / TARGET_TOTAL:.4f}",
        },
        {"metric": "primary_canonical_snapshot_plan_and_score_schools", "value": str(plan_and_score_schools)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in canonical_rows if normalize_text(row["school_key"]) == school_key),
                "",
            ),
            "primary_canonical_snapshot_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "primary_canonical_snapshot_rows"],
    )


if __name__ == "__main__":
    main()
