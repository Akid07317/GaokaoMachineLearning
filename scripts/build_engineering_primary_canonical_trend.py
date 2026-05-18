from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "from_year",
    "to_year",
    "normalized_type",
    "subject_type",
    "from_data_completeness",
    "to_data_completeness",
    "from_total_plan_count",
    "to_total_plan_count",
    "plan_count_delta",
    "from_minimum_score",
    "to_minimum_score",
    "minimum_score_delta",
    "from_minimum_rank",
    "to_minimum_rank",
    "minimum_rank_delta",
    "trend_label",
    "remarks",
    "record_id",
    "from_record_id",
    "to_record_id",
    "source_slug",
]

TARGET_TOTAL = 32


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


def trend_label(plan_delta: int | None, score_delta: int | None, rank_delta: int | None) -> str:
    labels: list[str] = []
    if plan_delta is not None:
        labels.append("计划增加" if plan_delta > 0 else "计划减少" if plan_delta < 0 else "计划持平")
    if score_delta is not None:
        labels.append("最低分上升" if score_delta > 0 else "最低分下降" if score_delta < 0 else "最低分持平")
    if rank_delta is not None:
        labels.append("最低位次后移" if rank_delta > 0 else "最低位次前移" if rank_delta < 0 else "最低位次持平")
    return "|".join(labels) if labels else "信息不足"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build canonical primary Guangxi physics trends from canonical snapshots."
    )
    parser.add_argument(
        "--canonical-source",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_physics_canonical_snapshot_merged.csv",
        help="Canonical primary Guangxi physics snapshot CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_canonical_trend_merged.csv",
        help="Canonical primary trend CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_canonical_trend_school_summary.csv",
        help="Canonical primary trend school summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_canonical_trend_coverage_rollup.csv",
        help="Canonical primary trend coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_primary_canonical_trend_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.canonical_source)

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(normalize_text(row.get("school_key", "")), normalize_text(row.get("subject_type", "")))].append(row)

    trend_rows = []
    school_counter: Counter[str] = Counter()
    for (school_key, subject_type), subset in sorted(grouped.items()):
        ordered = sorted(subset, key=lambda item: parse_int(item.get("year", "")) or 0)
        if len(ordered) < 2:
            continue
        for prev, curr in zip(ordered, ordered[1:]):
            prev_year = normalize_text(prev.get("year", ""))
            curr_year = normalize_text(curr.get("year", ""))
            if prev_year == curr_year:
                continue
            prev_plan = parse_int(prev.get("total_plan_count", ""))
            curr_plan = parse_int(curr.get("total_plan_count", ""))
            prev_score = parse_int(prev.get("minimum_score", ""))
            curr_score = parse_int(curr.get("minimum_score", ""))
            prev_rank = parse_int(prev.get("minimum_rank", ""))
            curr_rank = parse_int(curr.get("minimum_rank", ""))
            plan_delta = None if prev_plan is None or curr_plan is None else curr_plan - prev_plan
            score_delta = None if prev_score is None or curr_score is None else curr_score - prev_score
            rank_delta = None if prev_rank is None or curr_rank is None else curr_rank - prev_rank
            school_name = normalize_text(curr.get("school_name") or prev.get("school_name"))
            normalized_type = normalize_text(curr.get("normalized_type") or prev.get("normalized_type"))

            trend_rows.append(
                {
                    "school_name": school_name,
                    "school_key": school_key,
                    "from_year": prev_year,
                    "to_year": curr_year,
                    "normalized_type": normalized_type,
                    "subject_type": subject_type,
                    "from_data_completeness": normalize_text(prev.get("data_completeness", "")),
                    "to_data_completeness": normalize_text(curr.get("data_completeness", "")),
                    "from_total_plan_count": normalize_text(prev.get("total_plan_count", "")),
                    "to_total_plan_count": normalize_text(curr.get("total_plan_count", "")),
                    "plan_count_delta": "" if plan_delta is None else str(plan_delta),
                    "from_minimum_score": normalize_text(prev.get("minimum_score", "")),
                    "to_minimum_score": normalize_text(curr.get("minimum_score", "")),
                    "minimum_score_delta": "" if score_delta is None else str(score_delta),
                    "from_minimum_rank": normalize_text(prev.get("minimum_rank", "")),
                    "to_minimum_rank": normalize_text(curr.get("minimum_rank", "")),
                    "minimum_rank_delta": "" if rank_delta is None else str(rank_delta),
                    "trend_label": trend_label(plan_delta, score_delta, rank_delta),
                    "remarks": ";".join(
                        part
                        for part in [
                            "由广西物理类普通批主口径最佳快照派生的逐校逐年趋势摘要",
                            f"原始年份={prev_year}->{curr_year}",
                            normalize_text(curr.get("remarks", "")),
                        ]
                        if part
                    ),
                    "record_id": f"{school_key}-primary-canonical-trend-{prev_year}-{curr_year}-{subject_type}",
                    "from_record_id": normalize_text(prev.get("record_id", "")),
                    "to_record_id": normalize_text(curr.get("record_id", "")),
                    "source_slug": "official_primary_physics_canonical_trend",
                }
            )
            school_counter[school_key] += 1

    write_rows(args.output, trend_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in trend_rows if row["school_key"] == school_key),
                "",
            ),
            "primary_canonical_trend_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_canonical_trend_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_canonical_trend_schools", "value": str(len(school_counter))},
        {"metric": "primary_canonical_trend_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "primary_canonical_trend_total_rows", "value": str(len(trend_rows))},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in trend_rows if row["school_key"] == school_key),
                "",
            ),
            "primary_canonical_trend_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "primary_canonical_trend_rows"],
    )


if __name__ == "__main__":
    main()
