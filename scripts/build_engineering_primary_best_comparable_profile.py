from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "latest_year_available",
    "reference_year",
    "reference_is_latest",
    "year_gap_from_latest",
    "province",
    "normalized_type",
    "subject_type",
    "reference_data_completeness",
    "reference_source_type",
    "reference_total_plan_count",
    "reference_minimum_score",
    "reference_minimum_rank",
    "reference_average_score",
    "reference_maximum_score",
    "reference_plan_source_url",
    "reference_score_source_url",
    "trend_available",
    "trend_from_year",
    "trend_to_year",
    "trend_label",
    "comparable_profile_status",
    "comparable_profile_notes",
    "record_id",
    "reference_source_record_id",
    "trend_source_record_id",
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


def completeness_score(value: str) -> int:
    return COMPLETENESS_RANK.get(normalize_text(value), 0)


def trend_score(row: dict[str, str]) -> tuple[int, int, int, int]:
    return (
        parse_int(row.get("to_year", "")) or 0,
        parse_int(row.get("from_year", "")) or 0,
        completeness_score(row.get("to_data_completeness", "")),
        completeness_score(row.get("from_data_completeness", "")),
    )


def latest_snapshot_score(row: dict[str, str]) -> tuple[int, int, int]:
    return (
        parse_int(row.get("year", "")) or 0,
        completeness_score(row.get("data_completeness", "")),
        parse_int(row.get("total_plan_count", "")) or 0,
    )


def comparable_score(row: dict[str, str]) -> tuple[int, int, int, int]:
    has_rank = 1 if normalize_text(row.get("minimum_rank", "")) else 0
    return (
        has_rank,
        parse_int(row.get("year", "")) or 0,
        completeness_score(row.get("data_completeness", "")),
        parse_int(row.get("total_plan_count", "")) or 0,
    )


def describe_status(reference_row: dict[str, str], latest_row: dict[str, str]) -> str:
    has_rank = bool(normalize_text(reference_row.get("minimum_rank", "")))
    reference_year = normalize_text(reference_row.get("year", ""))
    latest_year = normalize_text(latest_row.get("year", ""))
    if has_rank and reference_year == latest_year:
        return "latest_comparable_with_rank"
    if has_rank:
        return "older_comparable_with_rank"
    return "latest_fallback_without_rank"


def describe_notes(reference_row: dict[str, str], latest_row: dict[str, str]) -> str:
    latest_year = normalize_text(latest_row.get("year", ""))
    reference_year = normalize_text(reference_row.get("year", ""))
    pieces = [
        "最佳可比画像优先选择最近且带最低位次的广西物理类普通批主口径记录",
        f"最新年份={latest_year}",
        f"参考年份={reference_year}",
    ]
    if reference_year != latest_year:
        pieces.append("最新年份缺最低位次，已回退到最近可比年份")
    if not normalize_text(reference_row.get("minimum_rank", "")):
        pieces.append("当前仍无最低位次，仅保留最新可用分数/计划信息")
    return ";".join(pieces)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build per-school best comparable Guangxi physics profiles from canonical snapshots."
    )
    parser.add_argument(
        "--canonical-snapshot",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_physics_canonical_snapshot_merged.csv",
        help="Canonical primary snapshot CSV.",
    )
    parser.add_argument(
        "--canonical-trend",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_canonical_trend_merged.csv",
        help="Canonical trend CSV.",
    )
    parser.add_argument(
        "--source-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_official_source_pack_merged.csv",
        help="Official source pack CSV for fallback plan/score URLs.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_best_comparable_profile_merged.csv",
        help="Best comparable profile output CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_best_comparable_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_best_comparable_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_primary_best_comparable_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    snapshot_rows = read_rows(args.canonical_snapshot)
    trend_rows = read_rows(args.canonical_trend)
    source_pack_rows = read_rows(args.source_pack)
    source_pack_by_key = {
        normalize_text(row.get("school_key", "")): row
        for row in source_pack_rows
        if normalize_text(row.get("school_key", ""))
    }

    trend_by_key: dict[str, dict[str, str]] = {}
    for row in trend_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        current = trend_by_key.get(school_key)
        if current is None or trend_score(row) > trend_score(current):
            trend_by_key[school_key] = row

    snapshots_by_key: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in snapshot_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if school_key:
            snapshots_by_key[school_key].append(row)

    profile_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    with_rank_count = 0
    rescued_older_count = 0
    with_trend_count = 0

    for school_key, items in sorted(snapshots_by_key.items()):
        latest_row = max(items, key=latest_snapshot_score)
        reference_row = max(items, key=comparable_score)
        trend_row = trend_by_key.get(school_key)

        latest_year = normalize_text(latest_row.get("year", ""))
        reference_year = normalize_text(reference_row.get("year", ""))
        has_rank = bool(normalize_text(reference_row.get("minimum_rank", "")))
        if has_rank:
            with_rank_count += 1
            if latest_year and reference_year and latest_year != reference_year:
                rescued_older_count += 1
        if trend_row is not None:
            with_trend_count += 1

        latest_year_int = parse_int(latest_year) or 0
        reference_year_int = parse_int(reference_year) or 0
        profile_rows.append(
            {
                "school_name": normalize_text(reference_row.get("school_name", "")),
                "school_key": school_key,
                "latest_year_available": latest_year,
                "reference_year": reference_year,
                "reference_is_latest": "true" if latest_year == reference_year else "false",
                "year_gap_from_latest": str(max(latest_year_int - reference_year_int, 0)) if latest_year_int else "",
                "province": normalize_text(reference_row.get("province", "")),
                "normalized_type": normalize_text(reference_row.get("normalized_type", "")),
                "subject_type": normalize_text(reference_row.get("subject_type", "")),
                "reference_data_completeness": normalize_text(reference_row.get("data_completeness", "")),
                "reference_source_type": normalize_text(reference_row.get("source_type", "")),
                "reference_total_plan_count": normalize_text(reference_row.get("total_plan_count", "")),
                "reference_minimum_score": normalize_text(reference_row.get("minimum_score", "")),
                "reference_minimum_rank": normalize_text(reference_row.get("minimum_rank", "")),
                "reference_average_score": normalize_text(reference_row.get("average_score", "")),
                "reference_maximum_score": normalize_text(reference_row.get("maximum_score", "")),
                "reference_plan_source_url": normalize_text(reference_row.get("plan_source_url", ""))
                or normalize_text(source_pack_by_key.get(school_key, {}).get("plan_source_url", "")),
                "reference_score_source_url": normalize_text(reference_row.get("score_source_url", ""))
                or normalize_text(source_pack_by_key.get(school_key, {}).get("score_source_url", "")),
                "trend_available": "true" if trend_row else "false",
                "trend_from_year": normalize_text(trend_row.get("from_year", "")) if trend_row else "",
                "trend_to_year": normalize_text(trend_row.get("to_year", "")) if trend_row else "",
                "trend_label": normalize_text(trend_row.get("trend_label", "")) if trend_row else "",
                "comparable_profile_status": describe_status(reference_row, latest_row),
                "comparable_profile_notes": describe_notes(reference_row, latest_row),
                "record_id": f"{school_key}-primary-best-comparable-{reference_year or latest_year}",
                "reference_source_record_id": normalize_text(reference_row.get("record_id", "")),
                "trend_source_record_id": normalize_text(trend_row.get("record_id", "")) if trend_row else "",
                "source_slug": "official_primary_best_comparable_profile",
            }
        )
        school_counter[school_key] += 1

    write_rows(args.output, profile_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in profile_rows if row["school_key"] == school_key), ""),
            "primary_best_comparable_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_best_comparable_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_best_comparable_schools", "value": str(len(school_counter))},
        {"metric": "primary_best_comparable_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "primary_best_comparable_with_rank_schools", "value": str(with_rank_count)},
        {"metric": "primary_best_comparable_rescued_older_rank_schools", "value": str(rescued_older_count)},
        {"metric": "primary_best_comparable_with_trend_schools", "value": str(with_trend_count)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in profile_rows if row["school_key"] == school_key), ""),
            "primary_best_comparable_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "primary_best_comparable_rows"],
    )
    print(
        "Wrote best comparable Guangxi physics profiles for "
        f"{len(school_counter)} schools ({with_rank_count} with rank, {rescued_older_count} rescued from older years)."
    )


if __name__ == "__main__":
    main()
