from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "queue_source",
    "engineering_tier",
    "pipeline_status",
    "reference_year",
    "latest_year_available",
    "subject_type",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_from_year",
    "trend_to_year",
    "trend_signal",
    "evidence_quality",
    "review_priority",
    "queue_bucket",
    "actionability_band",
    "actionability_score",
    "blocker_class",
    "recommended_next_action",
    "queue_notes",
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


PRIORITY_SCORE = {
    "ready_for_pre_ml_review": 4,
    "ready_comparable_with_note": 3,
    "good_but_check_details": 2,
    "needs_manual_completion": 1,
    "backfill_when_convenient": 0,
}


def choose_row(
    strict_row: dict[str, str] | None,
    comparable_row: dict[str, str] | None,
) -> tuple[dict[str, str] | None, str]:
    if strict_row and normalize_text(strict_row.get("review_priority")) == "ready_for_pre_ml_review":
        return strict_row, "strict_queue"
    if comparable_row and normalize_text(comparable_row.get("review_priority")) == "ready_comparable_with_note":
        return comparable_row, "best_comparable_queue"
    if strict_row:
        return strict_row, "strict_queue"
    if comparable_row:
        return comparable_row, "best_comparable_queue"
    return None, ""


def derive_actionability_band(review_priority: str) -> str:
    priority = normalize_text(review_priority)
    mapping = {
        "ready_for_pre_ml_review": "A1_action_now",
        "ready_comparable_with_note": "A2_action_with_note",
        "good_but_check_details": "B_review_then_use",
        "needs_manual_completion": "C_backfill_fields",
        "backfill_when_convenient": "D_backfill_later",
    }
    return mapping.get(priority, "Z_uncategorized")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a unified operating review queue from strict and best-comparable queues."
    )
    parser.add_argument(
        "--strict-queue",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_queue_merged.csv",
        help="Strict latest-year pre-ML review queue.",
    )
    parser.add_argument(
        "--best-comparable-queue",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_best_comparable_review_queue_merged.csv",
        help="Best comparable review queue.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_unified_review_operating_queue_merged.csv",
        help="Unified review operating queue output.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_unified_review_operating_queue_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_unified_review_operating_queue_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    strict_rows = read_rows(args.strict_queue)
    comparable_rows = read_rows(args.best_comparable_queue)

    strict_by_key = {normalize_text(row.get("school_key", "")): row for row in strict_rows}
    comparable_by_key = {normalize_text(row.get("school_key", "")): row for row in comparable_rows}
    all_keys = sorted(set(strict_by_key) | set(comparable_by_key))

    queue_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    actionable_now = 0
    actionable_with_note = 0

    for school_key in all_keys:
        row, queue_source = choose_row(strict_by_key.get(school_key), comparable_by_key.get(school_key))
        if row is None:
            continue

        review_priority = normalize_text(row.get("review_priority", ""))
        if review_priority == "ready_for_pre_ml_review":
            actionable_now += 1
        if review_priority == "ready_comparable_with_note":
            actionable_with_note += 1

        reference_year = normalize_text(row.get("reference_year", "")) or normalize_text(row.get("latest_year", ""))
        latest_year_available = normalize_text(row.get("latest_year_available", "")) or normalize_text(row.get("latest_year", ""))
        data_completeness = normalize_text(row.get("reference_data_completeness", "")) or normalize_text(
            row.get("latest_data_completeness", "")
        )
        total_plan_count = normalize_text(row.get("reference_total_plan_count", "")) or normalize_text(
            row.get("latest_total_plan_count", "")
        )
        minimum_score = normalize_text(row.get("reference_minimum_score", "")) or normalize_text(
            row.get("latest_minimum_score", "")
        )
        minimum_rank = normalize_text(row.get("reference_minimum_rank", "")) or normalize_text(
            row.get("latest_minimum_rank", "")
        )

        out = {
            "school_name": normalize_text(row.get("school_name", "")),
            "school_key": school_key,
            "queue_source": queue_source,
            "engineering_tier": normalize_text(row.get("engineering_tier", "")),
            "pipeline_status": normalize_text(row.get("pipeline_status", "")),
            "reference_year": reference_year,
            "latest_year_available": latest_year_available,
            "subject_type": normalize_text(row.get("subject_type", "")),
            "data_completeness": data_completeness,
            "total_plan_count": total_plan_count,
            "minimum_score": minimum_score,
            "minimum_rank": minimum_rank,
            "trend_available": normalize_text(row.get("trend_available", "")),
            "trend_from_year": normalize_text(row.get("trend_from_year", "")),
            "trend_to_year": normalize_text(row.get("trend_to_year", "")),
            "trend_signal": normalize_text(row.get("trend_signal", "")),
            "evidence_quality": normalize_text(row.get("evidence_quality", "")),
            "review_priority": review_priority,
            "queue_bucket": normalize_text(row.get("queue_bucket", "")),
            "actionability_band": derive_actionability_band(review_priority),
            "actionability_score": str(PRIORITY_SCORE.get(review_priority, -1)),
            "blocker_class": normalize_text(row.get("blocker_class", "")),
            "recommended_next_action": normalize_text(row.get("recommended_next_action", "")),
            "queue_notes": "统一操作队列优先采用严格最新年队列，其次吸收最佳可比队列中的 A2 学校，用于持续补数和预审排程",
            "record_id": f"{school_key}-unified-review-operating-queue-{reference_year or latest_year_available}",
            "source_record_id": normalize_text(row.get("record_id", "")),
            "source_slug": "official_unified_review_operating_queue",
        }
        queue_rows.append(out)
        school_counter[school_key] += 1

    queue_rows.sort(
        key=lambda item: (
            -parse_int(item["actionability_score"]) if parse_int(item["actionability_score"]) is not None else 999,
            item["engineering_tier"],
            item["school_key"],
        )
    )
    write_rows(args.output, queue_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in queue_rows if row["school_key"] == school_key), ""),
            "unified_review_operating_queue_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "unified_review_operating_queue_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "unified_review_operating_queue_schools", "value": str(len(school_counter))},
        {
            "metric": "unified_review_operating_queue_coverage_ratio",
            "value": f"{len(school_counter) / TARGET_TOTAL:.4f}",
        },
        {"metric": "unified_review_operating_queue_action_now_schools", "value": str(actionable_now)},
        {
            "metric": "unified_review_operating_queue_action_with_note_schools",
            "value": str(actionable_with_note),
        },
        {
            "metric": "unified_review_operating_queue_total_actionable_schools",
            "value": str(actionable_now + actionable_with_note),
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])
    print(
        "Wrote unified operating review queue rows for "
        f"{len(school_counter)} schools ({actionable_now} action now, {actionable_with_note} action with note)."
    )


if __name__ == "__main__":
    main()
