from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "school_name",
    "school_key",
    "engineering_tier",
    "pipeline_status",
    "reference_year",
    "latest_year_available",
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
    "trend_signal",
    "evidence_quality",
    "review_priority",
    "queue_bucket",
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


def queue_bucket(review_priority: str) -> str:
    mapping = {
        "ready_for_pre_ml_review": "A_ready_now",
        "ready_comparable_with_note": "A2_ready_comparable_with_note",
        "good_but_check_details": "B_review_with_caution",
        "needs_manual_completion": "C_complete_missing_fields",
    }
    return mapping.get(normalize_text(review_priority), "Z_uncategorized")


def blocker_class(pipeline_status: str, review_priority: str) -> str:
    status = normalize_text(pipeline_status)
    priority = normalize_text(review_priority)
    if status in {"ajax_blocked_403", "form_replay_blocked"}:
        return status
    if "page_only" in status or "needs_discovery" in status:
        return "source_gap"
    if priority == "needs_manual_completion":
        return "needs_more_fields"
    return "none"


def recommended_next_action(review_priority: str) -> str:
    priority = normalize_text(review_priority)
    if priority == "ready_for_pre_ml_review":
        return "hold_for_pre_ml_review"
    if priority == "ready_comparable_with_note":
        return "allow_comparable_reference_with_explicit_note"
    if priority == "good_but_check_details":
        return "verify_reference_year_and_special_type_scope"
    return "补主口径缺失字段后再纳入可比画像"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a best-comparable review queue from best-comparable signal rows."
    )
    parser.add_argument(
        "--signal-sheet",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_best_comparable_signal_merged.csv",
        help="Best comparable signal sheet CSV.",
    )
    parser.add_argument(
        "--pipeline-status",
        type=Path,
        default=Path("reports") / "engineering_pipeline_status.csv",
        help="Pipeline status CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_best_comparable_review_queue_merged.csv",
        help="Output review queue CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_best_comparable_review_queue_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_best_comparable_review_queue_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    signal_rows = read_rows(args.signal_sheet)
    pipeline_rows = read_rows(args.pipeline_status)
    pipeline_by_key = {normalize_text(row.get("school_key", "")): row for row in pipeline_rows}

    queue_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    ready_now = 0
    ready_comparable_with_note = 0
    with_plan_source = 0
    with_score_source = 0

    for row in signal_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        pipeline = pipeline_by_key.get(school_key, {})
        priority = normalize_text(row.get("review_priority", ""))
        if priority == "ready_for_pre_ml_review":
            ready_now += 1
        if priority == "ready_comparable_with_note":
            ready_comparable_with_note += 1
        if normalize_text(row.get("reference_plan_source_url", "")):
            with_plan_source += 1
        if normalize_text(row.get("reference_score_source_url", "")):
            with_score_source += 1
        queue_rows.append(
            {
                "school_name": normalize_text(row.get("school_name", "")),
                "school_key": school_key,
                "engineering_tier": normalize_text(pipeline.get("engineering_tier", "")),
                "pipeline_status": normalize_text(pipeline.get("pipeline_status", "")),
                "reference_year": normalize_text(row.get("reference_year", "")),
                "latest_year_available": normalize_text(row.get("latest_year_available", "")),
                "subject_type": normalize_text(row.get("subject_type", "")),
                "reference_data_completeness": normalize_text(row.get("reference_data_completeness", "")),
                "reference_total_plan_count": normalize_text(row.get("reference_total_plan_count", "")),
                "reference_minimum_score": normalize_text(row.get("reference_minimum_score", "")),
                "reference_minimum_rank": normalize_text(row.get("reference_minimum_rank", "")),
                "reference_plan_source_url": normalize_text(row.get("reference_plan_source_url", "")),
                "reference_score_source_url": normalize_text(row.get("reference_score_source_url", "")),
                "trend_available": normalize_text(row.get("trend_available", "")),
                "trend_from_year": normalize_text(row.get("trend_from_year", "")),
                "trend_to_year": normalize_text(row.get("trend_to_year", "")),
                "trend_signal": normalize_text(row.get("trend_signal", "")),
                "evidence_quality": normalize_text(row.get("evidence_quality", "")),
                "review_priority": priority,
                "queue_bucket": queue_bucket(priority),
                "blocker_class": blocker_class(pipeline.get("pipeline_status", ""), priority),
                "recommended_next_action": recommended_next_action(priority),
                "queue_notes": "最佳可比预审队列基于最近可比年份构建，专门收容最新缺位次但近年可比的学校，不进入机器学习",
                "record_id": f"{school_key}-best-comparable-review-queue-{normalize_text(row.get('reference_year', ''))}",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "official_best_comparable_review_queue",
            }
        )
        school_counter[school_key] += 1

    queue_rows.sort(key=lambda item: (item["queue_bucket"], item["engineering_tier"], item["school_key"]))
    write_rows(args.output, queue_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in queue_rows if row["school_key"] == school_key), ""),
            "best_comparable_review_queue_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "best_comparable_review_queue_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "best_comparable_review_queue_schools", "value": str(len(school_counter))},
        {
            "metric": "best_comparable_review_queue_coverage_ratio",
            "value": f"{len(school_counter) / TARGET_TOTAL:.4f}",
        },
        {"metric": "best_comparable_review_queue_ready_now_schools", "value": str(ready_now)},
        {"metric": "best_comparable_review_queue_with_plan_source_schools", "value": str(with_plan_source)},
        {"metric": "best_comparable_review_queue_with_score_source_schools", "value": str(with_score_source)},
        {
            "metric": "best_comparable_review_queue_ready_comparable_with_note_schools",
            "value": str(ready_comparable_with_note),
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])
    print(
        "Wrote best comparable review queue rows for "
        f"{len(school_counter)} schools ({ready_now} ready now, {ready_comparable_with_note} ready comparable with note)."
    )


if __name__ == "__main__":
    main()
