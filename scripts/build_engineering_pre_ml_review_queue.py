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
    "latest_year",
    "subject_type",
    "latest_data_completeness",
    "latest_total_plan_count",
    "latest_minimum_score",
    "latest_minimum_rank",
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
        "good_but_check_details": "B_review_with_caution",
        "needs_manual_completion": "C_complete_missing_fields",
        "backfill_when_convenient": "D_backfill_later",
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
    if priority == "backfill_when_convenient":
        return "thin_history"
    return "none"


def recommended_next_action(pipeline_status: str, review_priority: str, trend_available: str) -> str:
    status = normalize_text(pipeline_status)
    priority = normalize_text(review_priority)
    has_trend = normalize_text(trend_available) == "true"
    if priority == "ready_for_pre_ml_review":
        return "hold_for_pre_ml_review"
    if priority == "good_but_check_details":
        return "verify_latest_rank_and_plan_details"
    if priority == "needs_manual_completion":
        if has_trend:
            return "补齐缺失的计划数或最低位次字段"
        return "优先补最近两年的普通批主口径摘要"
    if status in {"ajax_blocked_403", "form_replay_blocked"}:
        return "保持在冷队列，等待更便宜的官方材料"
    return "低优先级回填"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a pre-ML review queue from primary signal rows and pipeline status."
    )
    parser.add_argument(
        "--signal-sheet",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_signal_sheet_merged.csv",
        help="Primary signal sheet CSV.",
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
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_queue_merged.csv",
        help="Output pre-ML review queue CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_queue_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_queue_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_pre_ml_review_queue_round.csv",
        help="Round summary CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    signal_rows = read_rows(args.signal_sheet)
    pipeline_rows = read_rows(args.pipeline_status)
    pipeline_by_key = {normalize_text(row.get("school_key", "")): row for row in pipeline_rows}

    queue_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    ready_count = 0

    for row in signal_rows:
        school_key = normalize_text(row.get("school_key", ""))
        if not school_key:
            continue
        pipeline = pipeline_by_key.get(school_key, {})
        priority = normalize_text(row.get("review_priority", ""))
        bucket = queue_bucket(priority)
        if priority == "ready_for_pre_ml_review":
            ready_count += 1

        out = {
            "school_name": normalize_text(row.get("school_name", "")),
            "school_key": school_key,
            "engineering_tier": normalize_text(pipeline.get("engineering_tier", "")),
            "pipeline_status": normalize_text(pipeline.get("pipeline_status", "")),
            "latest_year": normalize_text(row.get("latest_year", "")),
            "subject_type": normalize_text(row.get("subject_type", "")),
            "latest_data_completeness": normalize_text(row.get("latest_data_completeness", "")),
            "latest_total_plan_count": normalize_text(row.get("latest_total_plan_count", "")),
            "latest_minimum_score": normalize_text(row.get("latest_minimum_score", "")),
            "latest_minimum_rank": normalize_text(row.get("latest_minimum_rank", "")),
            "trend_available": normalize_text(row.get("trend_available", "")),
            "trend_from_year": normalize_text(row.get("trend_from_year", "")),
            "trend_to_year": normalize_text(row.get("trend_to_year", "")),
            "trend_signal": normalize_text(row.get("trend_signal", "")),
            "evidence_quality": normalize_text(row.get("evidence_quality", "")),
            "review_priority": priority,
            "queue_bucket": bucket,
            "blocker_class": blocker_class(pipeline.get("pipeline_status", ""), priority),
            "recommended_next_action": recommended_next_action(
                pipeline.get("pipeline_status", ""),
                priority,
                row.get("trend_available", ""),
            ),
            "queue_notes": "预审队列表由逐校信号表与主状态表合并得到，用于继续补数前的稳定排队，不进入机器学习",
            "record_id": f"{school_key}-pre-ml-review-queue-{normalize_text(row.get('latest_year', ''))}",
            "source_record_id": normalize_text(row.get("record_id", "")),
            "source_slug": "official_pre_ml_review_queue",
        }
        queue_rows.append(out)
        school_counter[school_key] += 1

    queue_rows.sort(key=lambda item: (item["queue_bucket"], item["engineering_tier"], item["school_key"]))
    write_rows(args.output, queue_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in queue_rows if row["school_key"] == school_key), ""),
            "pre_ml_review_queue_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "pre_ml_review_queue_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "pre_ml_review_queue_schools", "value": str(len(school_counter))},
        {"metric": "pre_ml_review_queue_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "pre_ml_review_queue_ready_schools", "value": str(ready_count)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in queue_rows if row["school_key"] == school_key), ""),
            "pre_ml_review_queue_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "pre_ml_review_queue_rows"],
    )


if __name__ == "__main__":
    main()
