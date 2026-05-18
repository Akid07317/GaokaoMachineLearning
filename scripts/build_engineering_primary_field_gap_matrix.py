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
    "latest_data_completeness",
    "latest_total_plan_count",
    "latest_minimum_score",
    "latest_minimum_rank",
    "trend_available",
    "review_priority",
    "has_latest_plan_count",
    "has_latest_minimum_score",
    "has_latest_minimum_rank",
    "has_trend",
    "is_fresh_2025",
    "gap_count",
    "gap_signature",
    "blocker_class",
    "backfill_route",
    "matrix_notes",
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


def derive_blocker_class(pipeline_status: str) -> str:
    status = normalize_text(pipeline_status)
    if status in {"ajax_blocked_403", "form_replay_blocked"}:
        return status
    if status == "ajax_family_page_only":
        return "cached_page_needs_extract"
    if status == "page_only":
        return "page_extract_needed"
    if status == "needs_discovery":
        return "source_gap"
    return "none"


def derive_backfill_route(pipeline_status: str, gap_signature: str, review_priority: str) -> str:
    status = normalize_text(pipeline_status)
    priority = normalize_text(review_priority)
    if status == "ajax_blocked_403":
        return "冷队列:等待更便宜的官方缓存或PDF"
    if status == "form_replay_blocked":
        return "冷队列:优先找缓存页或PDF，不回放表单"
    if status == "ajax_family_page_only":
        return "优先从已缓存静态页/脚本里抽表"
    if status == "page_only":
        return "优先从页面或附件提取官方摘要"
    if status == "needs_discovery":
        return "补官方入口或广西分省页"
    if priority == "ready_for_pre_ml_review":
        return "暂不补数，保留待预审"
    if "missing_rank" in gap_signature:
        return "优先补最低位次"
    if "missing_plan" in gap_signature:
        return "优先补计划数或计划摘要"
    if "missing_score" in gap_signature:
        return "优先补最低分或学校级分数摘要"
    return "常规低成本回填"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a primary-field gap matrix for the 32-school engineering target pool."
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix_520_master.csv",
        help="School matrix CSV.",
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
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_field_gap_matrix_merged.csv",
        help="Output field gap matrix CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_primary_field_gap_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_primary_field_gap_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    parser.add_argument(
        "--round-summary-output",
        type=Path,
        default=Path("reports") / "derived_primary_field_gap_round.csv",
        help="Round summary output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    matrix_rows = read_rows(args.matrix)
    signal_rows = read_rows(args.signal_sheet)
    pipeline_rows = read_rows(args.pipeline_status)

    signal_by_key = {normalize_text(row.get("school_key", "")): row for row in signal_rows}
    pipeline_by_key = {normalize_text(row.get("school_key", "")): row for row in pipeline_rows}

    gap_rows: list[dict[str, str]] = []
    school_counter: Counter[str] = Counter()
    ready_count = 0
    blocked_count = 0

    for row in matrix_rows:
        school_key = normalize_text(row.get("seed_id", ""))
        signal = signal_by_key.get(school_key, {})
        pipeline = pipeline_by_key.get(school_key, {})

        school_name = normalize_text(signal.get("school_name", "") or row.get("source_name", ""))
        latest_year = normalize_text(signal.get("latest_year", ""))
        latest_data_completeness = normalize_text(signal.get("latest_data_completeness", ""))
        latest_total_plan_count = normalize_text(signal.get("latest_total_plan_count", ""))
        latest_minimum_score = normalize_text(signal.get("latest_minimum_score", ""))
        latest_minimum_rank = normalize_text(signal.get("latest_minimum_rank", ""))
        trend_available = normalize_text(signal.get("trend_available", ""))
        review_priority = normalize_text(signal.get("review_priority", ""))
        pipeline_status = normalize_text(pipeline.get("pipeline_status", ""))

        has_latest_plan_count = "true" if (parse_int(latest_total_plan_count) or 0) > 0 else "false"
        has_latest_minimum_score = "true" if latest_minimum_score else "false"
        has_latest_minimum_rank = "true" if latest_minimum_rank else "false"
        has_trend = "true" if trend_available == "true" else "false"
        is_fresh_2025 = "true" if latest_year == "2025" else "false"

        gaps: list[str] = []
        if has_latest_plan_count == "false":
            gaps.append("missing_plan")
        if has_latest_minimum_score == "false":
            gaps.append("missing_score")
        if has_latest_minimum_rank == "false":
            gaps.append("missing_rank")
        if has_trend == "false":
            gaps.append("missing_trend")
        if is_fresh_2025 == "false":
            gaps.append("not_fresh_2025")
        if not latest_year:
            gaps.append("missing_latest_snapshot")

        gap_signature = "|".join(gaps) if gaps else "complete_enough"
        blocker = derive_blocker_class(pipeline_status)
        if blocker != "none":
            blocked_count += 1
        if review_priority == "ready_for_pre_ml_review":
            ready_count += 1

        gap_row = {
            "school_name": school_name,
            "school_key": school_key,
            "engineering_tier": normalize_text(row.get("engineering_tier", "")),
            "pipeline_status": pipeline_status,
            "latest_year": latest_year,
            "latest_data_completeness": latest_data_completeness,
            "latest_total_plan_count": latest_total_plan_count,
            "latest_minimum_score": latest_minimum_score,
            "latest_minimum_rank": latest_minimum_rank,
            "trend_available": has_trend,
            "review_priority": review_priority,
            "has_latest_plan_count": has_latest_plan_count,
            "has_latest_minimum_score": has_latest_minimum_score,
            "has_latest_minimum_rank": has_latest_minimum_rank,
            "has_trend": has_trend,
            "is_fresh_2025": is_fresh_2025,
            "gap_count": str(len(gaps)),
            "gap_signature": gap_signature,
            "blocker_class": blocker,
            "backfill_route": derive_backfill_route(pipeline_status, gap_signature, review_priority),
            "matrix_notes": "字段缺口矩阵由逐校信号表与主状态表合并得到，用于继续补数时保持质量与效率，不进入机器学习",
            "record_id": f"{school_key}-primary-field-gap",
            "source_record_id": normalize_text(signal.get("record_id", "")),
            "source_slug": "official_primary_field_gap_matrix",
        }
        gap_rows.append(gap_row)
        school_counter[school_key] += 1

    gap_rows.sort(key=lambda item: (item["engineering_tier"], item["gap_count"], item["school_key"]))
    write_rows(args.output, gap_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in gap_rows if row["school_key"] == school_key), ""),
            "primary_field_gap_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "primary_field_gap_rows"],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "primary_field_gap_schools", "value": str(len(school_counter))},
        {"metric": "primary_field_gap_coverage_ratio", "value": f"{len(school_counter) / TARGET_TOTAL:.4f}"},
        {"metric": "primary_field_gap_ready_schools", "value": str(ready_count)},
        {"metric": "primary_field_gap_blocked_schools", "value": str(blocked_count)},
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    round_rows = [
        {
            "school_key": school_key,
            "school_name": next((row["school_name"] for row in gap_rows if row["school_key"] == school_key), ""),
            "primary_field_gap_rows": str(count),
        }
        for school_key, count in sorted(school_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_rows(
        args.round_summary_output,
        round_rows,
        ["school_key", "school_name", "primary_field_gap_rows"],
    )


if __name__ == "__main__":
    main()
