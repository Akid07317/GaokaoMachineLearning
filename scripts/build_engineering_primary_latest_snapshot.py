from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "latest_year",
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
    "selection_reason",
    "remarks",
    "record_id",
    "source_record_id",
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


def read_registry(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return {
        normalize_text(row.get("school_key", "")): row
        for row in rows
        if normalize_text(row.get("school_key", ""))
    }


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
    year = parse_int(row.get("year", "")) or 0
    completeness = COMPLETENESS_RANK.get(normalize_text(row.get("data_completeness", "")), 0)
    total_plan = parse_int(row.get("total_plan_count", "")) or 0
    has_score = 1 if normalize_text(row.get("minimum_score", "")) else 0
    min_rank = parse_int(row.get("minimum_rank", "")) or -1
    return (year, completeness, total_plan, has_score, -min_rank)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build per-school latest canonical Guangxi physics snapshots."
    )
    parser.add_argument(
        "--canonical-source",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_physics_canonical_snapshot_merged.csv",
        help="Canonical primary Guangxi physics snapshot CSV.",
    )
    parser.add_argument(
        "--source-registry",
        type=Path,
        default=Path("configs") / "actionable_source_fallback_registry.csv",
        help="Fallback registry for plan/score source URLs when canonical snapshot lacks them.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_latest_snapshot_merged.csv",
        help="Latest primary Guangxi physics snapshot CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_latest_snapshot_school_summary.csv",
        help="Latest primary snapshot school summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_latest_snapshot_coverage_rollup.csv",
        help="Latest primary snapshot coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_primary_latest_snapshot_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.canonical_source)
    source_registry = read_registry(args.source_registry)

    best_by_school: dict[str, dict[str, str]] = {}
    for row in rows:
        school_key = normalize_text(row.get("school_key", ""))
        current = best_by_school.get(school_key)
        if current is None or row_score(row) > row_score(current):
            best_by_school[school_key] = row

    latest_rows = []
    school_counter: Counter[str] = Counter()
    for school_key, row in sorted(best_by_school.items()):
        registry_row = source_registry.get(school_key, {})
        plan_source_url = normalize_text(row.get("plan_source_url", "")) or normalize_text(
            registry_row.get("plan_source_url", "")
        )
        score_source_url = normalize_text(row.get("score_source_url", "")) or normalize_text(
            registry_row.get("score_source_url", "")
        )
        out = {
            "school_name": normalize_text(row.get("school_name", "")),
            "school_key": school_key,
            "latest_year": normalize_text(row.get("year", "")),
            "province": normalize_text(row.get("province", "")),
            "normalized_type": normalize_text(row.get("normalized_type", "")),
            "subject_type": normalize_text(row.get("subject_type", "")),
            "data_completeness": normalize_text(row.get("data_completeness", "")),
            "source_type": normalize_text(row.get("source_type", "")),
            "plan_specialty_count_total": normalize_text(row.get("plan_specialty_count_total", "")),
            "plan_selection_group_count_total": normalize_text(row.get("plan_selection_group_count_total", "")),
            "plan_campus_count_total": normalize_text(row.get("plan_campus_count_total", "")),
            "total_plan_count": normalize_text(row.get("total_plan_count", "")),
            "score_campus": normalize_text(row.get("score_campus", "")),
            "minimum_score": normalize_text(row.get("minimum_score", "")),
            "minimum_rank": normalize_text(row.get("minimum_rank", "")),
            "average_score": normalize_text(row.get("average_score", "")),
            "maximum_score": normalize_text(row.get("maximum_score", "")),
            "selection_reason": "按年份优先、完整度优先、计划数优先、分数信息优先选取每校最新可用主口径记录",
            "remarks": ";".join(
                part
                for part in [
                    "每校最新主口径快照由最佳主口径快照层筛选得到",
                    normalize_text(row.get("remarks", "")),
                ]
                if part
            ),
            "record_id": f"{school_key}-primary-latest-{normalize_text(row.get('year', ''))}",
            "source_record_id": normalize_text(row.get("record_id", "")),
            "plan_source_url": plan_source_url,
            "score_source_url": score_source_url,
            "source_slug": "official_primary_latest_snapshot",
        }
        latest_rows.append(out)
        school_counter[school_key] += 1

    write_rows(args.output, latest_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in latest_rows if row["school_key"] == school_key),
                "",
            ),
            "primary_latest_snapshot_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_latest_snapshot_rows"],
    )

    plan_and_score_schools = sum(
        1
        for school_key in school_counter
        if any(
            row["school_key"] == school_key and normalize_text(row.get("data_completeness", "")) == "plan_and_score"
            for row in latest_rows
        )
    )
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_latest_snapshot_schools", "value": str(len(school_counter))},
        {"metric": "primary_latest_snapshot_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "primary_latest_snapshot_plan_and_score_schools", "value": str(plan_and_score_schools)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in latest_rows if row["school_key"] == school_key),
                "",
            ),
            "primary_latest_snapshot_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "primary_latest_snapshot_rows"],
    )


if __name__ == "__main__":
    main()
