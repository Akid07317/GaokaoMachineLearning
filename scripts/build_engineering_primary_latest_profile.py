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
    "latest_data_completeness",
    "latest_source_type",
    "latest_total_plan_count",
    "latest_minimum_score",
    "latest_minimum_rank",
    "latest_average_score",
    "latest_maximum_score",
    "latest_plan_source_url",
    "latest_score_source_url",
    "trend_from_year",
    "trend_to_year",
    "trend_available",
    "trend_from_data_completeness",
    "trend_to_data_completeness",
    "trend_plan_count_delta",
    "trend_minimum_score_delta",
    "trend_minimum_rank_delta",
    "trend_label",
    "profile_status",
    "profile_notes",
    "record_id",
    "latest_source_record_id",
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


def latest_trend_score(row: dict[str, str]) -> tuple[int, int, int, int]:
    to_year = parse_int(row.get("to_year", "")) or 0
    from_year = parse_int(row.get("from_year", "")) or 0
    to_completeness = COMPLETENESS_RANK.get(normalize_text(row.get("to_data_completeness", "")), 0)
    from_completeness = COMPLETENESS_RANK.get(normalize_text(row.get("from_data_completeness", "")), 0)
    return (to_year, from_year, to_completeness, from_completeness)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build per-school latest Guangxi physics profiles from latest snapshots and canonical trends."
    )
    parser.add_argument(
        "--latest-snapshot",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_latest_snapshot_merged.csv",
        help="Latest primary Guangxi physics snapshot CSV.",
    )
    parser.add_argument(
        "--canonical-trend",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_canonical_trend_merged.csv",
        help="Canonical primary Guangxi physics trend CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_latest_profile_merged.csv",
        help="Output latest profile CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_latest_profile_school_summary.csv",
        help="Output school summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_latest_profile_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_primary_latest_profile_round.csv",
        help="Round summary CSV.",
    )
    return parser


def describe_profile_status(latest_row: dict[str, str], trend_row: dict[str, str] | None) -> str:
    latest_completeness = normalize_text(latest_row.get("data_completeness", ""))
    has_trend = trend_row is not None
    if latest_completeness == "plan_and_score" and has_trend:
        return "latest_plan_and_score_with_trend"
    if latest_completeness == "plan_and_score":
        return "latest_plan_and_score_no_trend"
    if latest_completeness == "score_only" and has_trend:
        return "latest_score_only_with_trend"
    if latest_completeness == "score_only":
        return "latest_score_only_no_trend"
    if latest_completeness == "plan_only" and has_trend:
        return "latest_plan_only_with_trend"
    if latest_completeness == "plan_only":
        return "latest_plan_only_no_trend"
    return "latest_profile_unclassified"


def describe_profile_notes(latest_row: dict[str, str], trend_row: dict[str, str] | None) -> str:
    pieces = [
        "逐校最新画像由最新主口径快照层与最佳主口径趋势层合并得到",
        "优先保留每校最新可用的广西物理类普通批主口径记录",
    ]
    if trend_row is None:
        pieces.append("当前学校暂无可用的主口径年际趋势记录")
    else:
        pieces.append(
            f"最近趋势采用{normalize_text(trend_row.get('from_year', ''))}->{normalize_text(trend_row.get('to_year', ''))}记录"
        )
    return ";".join(pieces)


def main() -> None:
    args = build_parser().parse_args()
    latest_rows = read_rows(args.latest_snapshot)
    trend_rows = read_rows(args.canonical_trend)

    trend_by_key: dict[str, dict[str, str]] = {}
    for row in trend_rows:
        key = normalize_text(row.get("school_key", ""))
        if not key:
            continue
        current = trend_by_key.get(key)
        if current is None or latest_trend_score(row) > latest_trend_score(current):
            trend_by_key[key] = row

    profile_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    schools_with_trend = 0
    plan_and_score_schools = 0

    for latest_row in latest_rows:
        school_key = normalize_text(latest_row.get("school_key", ""))
        if not school_key:
            continue
        trend_row = trend_by_key.get(school_key)
        if trend_row is not None:
            schools_with_trend += 1
        if normalize_text(latest_row.get("data_completeness", "")) == "plan_and_score":
            plan_and_score_schools += 1

        out = {
            "school_name": normalize_text(latest_row.get("school_name", "")),
            "school_key": school_key,
            "latest_year": normalize_text(latest_row.get("latest_year", "")),
            "province": normalize_text(latest_row.get("province", "")),
            "normalized_type": normalize_text(latest_row.get("normalized_type", "")),
            "subject_type": normalize_text(latest_row.get("subject_type", "")),
            "latest_data_completeness": normalize_text(latest_row.get("data_completeness", "")),
            "latest_source_type": normalize_text(latest_row.get("source_type", "")),
            "latest_total_plan_count": normalize_text(latest_row.get("total_plan_count", "")),
            "latest_minimum_score": normalize_text(latest_row.get("minimum_score", "")),
            "latest_minimum_rank": normalize_text(latest_row.get("minimum_rank", "")),
            "latest_average_score": normalize_text(latest_row.get("average_score", "")),
            "latest_maximum_score": normalize_text(latest_row.get("maximum_score", "")),
            "latest_plan_source_url": normalize_text(latest_row.get("plan_source_url", "")),
            "latest_score_source_url": normalize_text(latest_row.get("score_source_url", "")),
            "trend_from_year": normalize_text(trend_row.get("from_year", "")) if trend_row else "",
            "trend_to_year": normalize_text(trend_row.get("to_year", "")) if trend_row else "",
            "trend_available": "true" if trend_row else "false",
            "trend_from_data_completeness": normalize_text(trend_row.get("from_data_completeness", "")) if trend_row else "",
            "trend_to_data_completeness": normalize_text(trend_row.get("to_data_completeness", "")) if trend_row else "",
            "trend_plan_count_delta": normalize_text(trend_row.get("plan_count_delta", "")) if trend_row else "",
            "trend_minimum_score_delta": normalize_text(trend_row.get("minimum_score_delta", "")) if trend_row else "",
            "trend_minimum_rank_delta": normalize_text(trend_row.get("minimum_rank_delta", "")) if trend_row else "",
            "trend_label": normalize_text(trend_row.get("trend_label", "")) if trend_row else "",
            "profile_status": describe_profile_status(latest_row, trend_row),
            "profile_notes": describe_profile_notes(latest_row, trend_row),
            "record_id": f"{school_key}-primary-latest-profile-{normalize_text(latest_row.get('latest_year', ''))}",
            "latest_source_record_id": normalize_text(latest_row.get("record_id", "")),
            "trend_source_record_id": normalize_text(trend_row.get("record_id", "")) if trend_row else "",
            "source_slug": "official_primary_latest_profile",
        }
        profile_rows.append(out)
        school_counter[school_key] += 1

    write_rows(args.output, profile_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in profile_rows if row["school_key"] == school_key),
                "",
            ),
            "primary_latest_profile_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_latest_profile_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_latest_profile_schools", "value": str(len(school_counter))},
        {"metric": "primary_latest_profile_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "primary_latest_profile_with_trend_schools", "value": str(schools_with_trend)},
        {"metric": "primary_latest_profile_plan_and_score_schools", "value": str(plan_and_score_schools)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next(
                (row["school_name"] for row in profile_rows if row["school_key"] == school_key),
                "",
            ),
            "primary_latest_profile_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "primary_latest_profile_rows"],
    )


if __name__ == "__main__":
    main()
