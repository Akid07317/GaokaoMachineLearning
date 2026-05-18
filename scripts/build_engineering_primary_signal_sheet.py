from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "latest_year",
    "subject_type",
    "latest_data_completeness",
    "latest_total_plan_count",
    "latest_minimum_score",
    "latest_minimum_rank",
    "trend_available",
    "trend_from_year",
    "trend_to_year",
    "trend_label",
    "trend_signal",
    "evidence_quality",
    "freshness_flag",
    "review_priority",
    "signal_notes",
    "record_id",
    "source_record_id",
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


def derive_trend_signal(label: str, trend_available: bool) -> str:
    text = normalize_text(label)
    if not trend_available:
        return "no_trend"
    has_forward = "最低位次前移" in text
    has_backward = "最低位次后移" in text
    if has_forward and has_backward:
        return "mixed_rank_signal"
    if has_forward:
        return "rank_hotter"
    if has_backward:
        return "rank_cooler"
    if "最低分上升" in text and "最低分下降" not in text:
        return "score_hotter_only"
    if "最低分下降" in text and "最低分上升" not in text:
        return "score_cooler_only"
    return "trend_available_unclassified"


def derive_evidence_quality(row: dict[str, str], trend_available: bool) -> str:
    completeness = normalize_text(row.get("latest_data_completeness", ""))
    has_rank = bool(normalize_text(row.get("latest_minimum_rank", "")))
    has_plan = (parse_int(row.get("latest_total_plan_count", "")) or 0) > 0
    has_score = bool(normalize_text(row.get("latest_minimum_score", "")))
    if completeness == "plan_and_score" and has_rank and trend_available:
        return "high"
    if completeness == "plan_and_score" and (has_plan or has_score):
        return "medium"
    if completeness == "score_only" and has_score and trend_available:
        return "medium"
    if completeness in {"score_only", "plan_only"} and (has_plan or has_score):
        return "foundational"
    return "thin"


def derive_freshness_flag(row: dict[str, str]) -> str:
    latest_year = parse_int(row.get("latest_year", "")) or 0
    if latest_year >= 2025:
        return "fresh_2025"
    if latest_year >= 2024:
        return "recent_2024"
    return "older_pre_2024"


def derive_review_priority(row: dict[str, str], trend_available: bool) -> str:
    completeness = normalize_text(row.get("latest_data_completeness", ""))
    freshness = derive_freshness_flag(row)
    has_rank = bool(normalize_text(row.get("latest_minimum_rank", "")))
    if completeness == "plan_and_score" and freshness == "fresh_2025" and has_rank and trend_available:
        return "ready_for_pre_ml_review"
    if completeness == "plan_and_score" and freshness in {"fresh_2025", "recent_2024"}:
        return "good_but_check_details"
    if completeness in {"score_only", "plan_only"} and freshness in {"fresh_2025", "recent_2024"}:
        return "needs_manual_completion"
    return "backfill_when_convenient"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build per-school primary signal sheet from latest Guangxi physics profiles."
    )
    parser.add_argument(
        "--latest-profile",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_latest_profile_merged.csv",
        help="Latest primary profile CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_signal_sheet_merged.csv",
        help="Primary signal sheet output CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_signal_school_summary.csv",
        help="Signal sheet school summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_signal_coverage_rollup.csv",
        help="Signal sheet coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_primary_signal_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    profile_rows = read_rows(args.latest_profile)

    signal_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    ready_count = 0
    with_trend_count = 0

    for row in profile_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        trend_available = normalize_text(row.get("trend_available", "")) == "true"
        if trend_available:
            with_trend_count += 1
        review_priority = derive_review_priority(row, trend_available)
        if review_priority == "ready_for_pre_ml_review":
            ready_count += 1

        signal_row = {
            "school_name": normalize_text(row.get("school_name", "")),
            "school_key": school_key,
            "latest_year": normalize_text(row.get("latest_year", "")),
            "subject_type": normalize_text(row.get("subject_type", "")),
            "latest_data_completeness": normalize_text(row.get("latest_data_completeness", "")),
            "latest_total_plan_count": normalize_text(row.get("latest_total_plan_count", "")),
            "latest_minimum_score": normalize_text(row.get("latest_minimum_score", "")),
            "latest_minimum_rank": normalize_text(row.get("latest_minimum_rank", "")),
            "trend_available": "true" if trend_available else "false",
            "trend_from_year": normalize_text(row.get("trend_from_year", "")),
            "trend_to_year": normalize_text(row.get("trend_to_year", "")),
            "trend_label": normalize_text(row.get("trend_label", "")),
            "trend_signal": derive_trend_signal(row.get("trend_label", ""), trend_available),
            "evidence_quality": derive_evidence_quality(row, trend_available),
            "freshness_flag": derive_freshness_flag(row),
            "review_priority": review_priority,
            "signal_notes": "逐校信号表由最新主口径画像层派生，用于快速核对学校级官方广西数据的完整度、时效性与趋势可用性",
            "record_id": f"{school_key}-primary-signal-{normalize_text(row.get('latest_year', ''))}",
            "source_record_id": normalize_text(row.get("record_id", "")),
            "source_slug": "official_primary_signal_sheet",
        }
        signal_rows.append(signal_row)
        school_counter[school_key] += 1

    signal_rows.sort(key=lambda item: (item["school_key"], item["latest_year"]))
    write_rows(args.output, signal_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in signal_rows if row["school_key"] == school_key), ""),
            "primary_signal_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_signal_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_signal_schools", "value": str(len(school_counter))},
        {"metric": "primary_signal_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "primary_signal_with_trend_schools", "value": str(with_trend_count)},
        {"metric": "primary_signal_ready_for_pre_ml_review_schools", "value": str(ready_count)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in signal_rows if row["school_key"] == school_key), ""),
            "primary_signal_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "primary_signal_rows"],
    )


if __name__ == "__main__":
    main()
