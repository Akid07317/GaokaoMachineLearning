from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "latest_year_available",
    "reference_year",
    "reference_is_latest",
    "year_gap_from_latest",
    "subject_type",
    "reference_data_completeness",
    "reference_total_plan_count",
    "reference_minimum_score",
    "reference_minimum_rank",
    "reference_plan_source_url",
    "reference_score_source_url",
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


def derive_freshness_flag(latest_year: str, reference_year: str, year_gap: int) -> str:
    latest_year_int = parse_int(latest_year) or 0
    reference_year_int = parse_int(reference_year) or 0
    if latest_year_int >= 2025 and year_gap == 0:
        return "fresh_latest_2025"
    if latest_year_int >= 2025 and year_gap == 1 and reference_year_int >= 2024:
        return "fresh_with_recent_fallback"
    if reference_year_int >= 2024:
        return "recent_2024"
    return "older_pre_2024"


def derive_evidence_quality(row: dict[str, str], trend_available: bool, year_gap: int) -> str:
    completeness = normalize_text(row.get("reference_data_completeness", ""))
    has_rank = bool(normalize_text(row.get("reference_minimum_rank", "")))
    has_plan = (parse_int(row.get("reference_total_plan_count", "")) or 0) > 0
    has_score = bool(normalize_text(row.get("reference_minimum_score", "")))
    if completeness == "plan_and_score" and has_rank and trend_available and year_gap == 0:
        return "high"
    if has_rank and trend_available and year_gap <= 1:
        return "medium"
    if has_rank or has_plan or has_score:
        return "foundational"
    return "thin"


def derive_review_priority(row: dict[str, str], trend_available: bool, year_gap: int) -> str:
    completeness = normalize_text(row.get("reference_data_completeness", ""))
    has_rank = bool(normalize_text(row.get("reference_minimum_rank", "")))
    latest_year_int = parse_int(row.get("latest_year_available", "")) or 0
    if completeness == "plan_and_score" and has_rank and trend_available and year_gap == 0 and latest_year_int >= 2025:
        return "ready_for_pre_ml_review"
    if has_rank and trend_available and year_gap <= 1 and latest_year_int >= 2025:
        return "ready_comparable_with_note"
    if has_rank and latest_year_int >= 2024:
        return "good_but_check_details"
    return "needs_manual_completion"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build per-school best comparable signal sheet from best comparable profiles."
    )
    parser.add_argument(
        "--best-comparable-profile",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_best_comparable_profile_merged.csv",
        help="Best comparable profile CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_best_comparable_signal_merged.csv",
        help="Output signal CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_best_comparable_signal_school_summary.csv",
        help="School summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_best_comparable_signal_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    profile_rows = read_rows(args.best_comparable_profile)

    signal_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    ready_now = 0
    ready_comparable_with_note = 0
    with_plan_source = 0
    with_score_source = 0

    for row in profile_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        trend_available = normalize_text(row.get("trend_available", "")) == "true"
        year_gap = parse_int(row.get("year_gap_from_latest", "")) or 0
        review_priority = derive_review_priority(row, trend_available, year_gap)
        if review_priority == "ready_for_pre_ml_review":
            ready_now += 1
        if review_priority == "ready_comparable_with_note":
            ready_comparable_with_note += 1
        if normalize_text(row.get("reference_plan_source_url", "")):
            with_plan_source += 1
        if normalize_text(row.get("reference_score_source_url", "")):
            with_score_source += 1

        signal_rows.append(
            {
                "school_name": normalize_text(row.get("school_name", "")),
                "school_key": school_key,
                "latest_year_available": normalize_text(row.get("latest_year_available", "")),
                "reference_year": normalize_text(row.get("reference_year", "")),
                "reference_is_latest": normalize_text(row.get("reference_is_latest", "")),
                "year_gap_from_latest": normalize_text(row.get("year_gap_from_latest", "")),
                "subject_type": normalize_text(row.get("subject_type", "")),
                "reference_data_completeness": normalize_text(row.get("reference_data_completeness", "")),
                "reference_total_plan_count": normalize_text(row.get("reference_total_plan_count", "")),
                "reference_minimum_score": normalize_text(row.get("reference_minimum_score", "")),
                "reference_minimum_rank": normalize_text(row.get("reference_minimum_rank", "")),
                "reference_plan_source_url": normalize_text(row.get("reference_plan_source_url", "")),
                "reference_score_source_url": normalize_text(row.get("reference_score_source_url", "")),
                "trend_available": "true" if trend_available else "false",
                "trend_from_year": normalize_text(row.get("trend_from_year", "")),
                "trend_to_year": normalize_text(row.get("trend_to_year", "")),
                "trend_label": normalize_text(row.get("trend_label", "")),
                "trend_signal": derive_trend_signal(row.get("trend_label", ""), trend_available),
                "evidence_quality": derive_evidence_quality(row, trend_available, year_gap),
                "freshness_flag": derive_freshness_flag(
                    row.get("latest_year_available", ""),
                    row.get("reference_year", ""),
                    year_gap,
                ),
                "review_priority": review_priority,
                "signal_notes": "最佳可比信号表基于最近且带最低位次的主口径记录，用于把最新缺位次但近年可比的学校重新拉回可审状态",
                "record_id": f"{school_key}-primary-best-comparable-signal-{normalize_text(row.get('reference_year', ''))}",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "official_primary_best_comparable_signal",
            }
        )
        school_counter[school_key] += 1

    signal_rows.sort(key=lambda item: (item["school_key"], item["reference_year"]))
    write_rows(args.output, signal_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in signal_rows if row["school_key"] == school_key), ""),
            "primary_best_comparable_signal_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_best_comparable_signal_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_best_comparable_signal_schools", "value": str(len(school_counter))},
        {
            "metric": "primary_best_comparable_signal_coverage_ratio",
            "value": f"{len(school_counter) / TARGET_TOTAL:.4f}",
        },
        {"metric": "primary_best_comparable_signal_ready_now_schools", "value": str(ready_now)},
        {"metric": "primary_best_comparable_signal_with_plan_source_schools", "value": str(with_plan_source)},
        {"metric": "primary_best_comparable_signal_with_score_source_schools", "value": str(with_score_source)},
        {
            "metric": "primary_best_comparable_signal_ready_comparable_with_note_schools",
            "value": str(ready_comparable_with_note),
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])
    print(
        "Wrote best comparable signal rows for "
        f"{len(school_counter)} schools ({ready_now} ready now, {ready_comparable_with_note} ready comparable with note)."
    )


if __name__ == "__main__":
    main()
