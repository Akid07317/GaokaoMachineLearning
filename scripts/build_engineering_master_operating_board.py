from __future__ import annotations

import argparse
import csv
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "engineering_tier",
    "pipeline_status",
    "operating_lane",
    "operating_priority",
    "action_source",
    "latest_year",
    "reference_year",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "blocker_class",
    "next_action",
    "plan_source_url",
    "score_source_url",
    "board_notes",
    "record_id",
    "source_slug",
]


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
    return str(value or "").strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a 32-school master operating board for Guangxi engineering targets."
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("reports") / "engineering_focus_school_matrix_520_master.csv",
        help="Engineering target matrix CSV.",
    )
    parser.add_argument(
        "--pipeline-status",
        type=Path,
        default=Path("reports") / "engineering_pipeline_status.csv",
        help="Current pipeline status CSV.",
    )
    parser.add_argument(
        "--unified-queue",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_unified_review_operating_queue_merged.csv",
        help="Unified review operating queue CSV.",
    )
    parser.add_argument(
        "--field-gap-matrix",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_field_gap_matrix_merged.csv",
        help="Primary field gap matrix CSV.",
    )
    parser.add_argument(
        "--cold-queue-unlock",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_cold_queue_unlock_queue_merged.csv",
        help="Cold queue unlock queue CSV.",
    )
    parser.add_argument(
        "--official-source-pack",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_official_source_pack_merged.csv",
        help="Official source pack CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_master_operating_board_merged.csv",
        help="Output merged operating board CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_master_operating_board_school_summary.csv",
        help="School summary CSV output.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_master_operating_board_coverage_rollup.csv",
        help="Coverage rollup CSV output.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    matrix_rows = read_rows(args.matrix)
    pipeline_rows = read_rows(args.pipeline_status)
    queue_rows = read_rows(args.unified_queue)
    gap_rows = read_rows(args.field_gap_matrix)
    cold_rows = read_rows(args.cold_queue_unlock)
    source_rows = read_rows(args.official_source_pack)

    pipeline_by_key = {normalize_text(row.get("school_key", "")): row for row in pipeline_rows}
    queue_by_key = {normalize_text(row.get("school_key", "")): row for row in queue_rows}
    gap_by_key = {normalize_text(row.get("school_key", "")): row for row in gap_rows}
    cold_by_key = {normalize_text(row.get("school_key", "")): row for row in cold_rows}
    source_by_key = {normalize_text(row.get("school_key", "")): row for row in source_rows}

    merged_rows: list[dict[str, str]] = []
    school_summary_rows: list[dict[str, str]] = []
    lane_counts: dict[str, int] = {}

    for row in matrix_rows:
        school_key = normalize_text(row.get("seed_id", ""))
        school_name = normalize_text(row.get("source_name", school_key))
        pipeline = pipeline_by_key.get(school_key, {})
        queue = queue_by_key.get(school_key, {})
        gap = gap_by_key.get(school_key, {})
        cold = cold_by_key.get(school_key, {})
        source = source_by_key.get(school_key, {})

        if queue:
            band = normalize_text(queue.get("actionability_band", ""))
            if band == "A1_action_now":
                lane = "A1_action_now"
                priority = "1"
            else:
                lane = "A2_action_with_note"
                priority = "2"
            action_source = "unified_review_operating_queue"
            latest_year = normalize_text(queue.get("latest_year_available", ""))
            reference_year = normalize_text(queue.get("reference_year", ""))
            data_completeness = normalize_text(queue.get("data_completeness", ""))
            total_plan_count = normalize_text(queue.get("total_plan_count", ""))
            minimum_score = normalize_text(queue.get("minimum_score", ""))
            minimum_rank = normalize_text(queue.get("minimum_rank", ""))
            trend_available = normalize_text(queue.get("trend_available", ""))
            trend_signal = normalize_text(queue.get("trend_signal", ""))
            blocker_class = normalize_text(queue.get("blocker_class", ""))
            next_action = normalize_text(queue.get("recommended_next_action", ""))
        elif cold:
            lane = normalize_text(cold.get("unlock_priority", "P3_manual_review"))
            priority = "3" if lane.startswith("P1") else "4" if lane.startswith("P2") else "5"
            action_source = "cold_queue_unlock_queue"
            latest_year = normalize_text(gap.get("latest_year", ""))
            reference_year = ""
            data_completeness = normalize_text(gap.get("latest_data_completeness", ""))
            total_plan_count = normalize_text(gap.get("latest_total_plan_count", ""))
            minimum_score = normalize_text(gap.get("latest_minimum_score", ""))
            minimum_rank = normalize_text(gap.get("latest_minimum_rank", ""))
            trend_available = normalize_text(gap.get("trend_available", ""))
            trend_signal = ""
            blocker_class = normalize_text(cold.get("block_type", ""))
            next_action = normalize_text(cold.get("recommended_next_action", ""))
        else:
            lane = "B_fill_fields"
            priority = "3"
            action_source = "primary_field_gap_matrix"
            latest_year = normalize_text(gap.get("latest_year", ""))
            reference_year = ""
            data_completeness = normalize_text(gap.get("latest_data_completeness", ""))
            total_plan_count = normalize_text(gap.get("latest_total_plan_count", ""))
            minimum_score = normalize_text(gap.get("latest_minimum_score", ""))
            minimum_rank = normalize_text(gap.get("latest_minimum_rank", ""))
            trend_available = normalize_text(gap.get("trend_available", ""))
            trend_signal = ""
            blocker_class = normalize_text(gap.get("blocker_class", ""))
            next_action = normalize_text(gap.get("backfill_route", ""))

        lane_counts[lane] = lane_counts.get(lane, 0) + 1

        merged_rows.append(
            {
                "school_key": school_key,
                "school_name": school_name,
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "pipeline_status": normalize_text(pipeline.get("pipeline_status", "")),
                "operating_lane": lane,
                "operating_priority": priority,
                "action_source": action_source,
                "latest_year": latest_year,
                "reference_year": reference_year,
                "data_completeness": data_completeness,
                "total_plan_count": total_plan_count,
                "minimum_score": minimum_score,
                "minimum_rank": minimum_rank,
                "trend_available": trend_available,
                "trend_signal": trend_signal,
                "blocker_class": blocker_class,
                "next_action": next_action,
                "plan_source_url": normalize_text(source.get("plan_source_url", "")),
                "score_source_url": normalize_text(source.get("score_source_url", "")),
                "board_notes": "32校统一操作板：优先串起可行动学校、字段回填学校和冷队列解锁学校，避免在多张队列表之间来回跳",
                "record_id": f"{school_key}-master-operating-board",
                "source_slug": "master_operating_board",
            }
        )
        school_summary_rows.append(
            {
                "school_key": school_key,
                "school_name": school_name,
                "master_operating_board_rows": "1",
            }
        )

    merged_rows.sort(key=lambda item: (item["operating_priority"], item["engineering_tier"], item["school_key"]))
    school_summary_rows.sort(key=lambda item: item["school_key"])

    write_rows(args.output, merged_rows, FIELDS)
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        ["school_key", "school_name", "master_operating_board_rows"],
    )
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "master_operating_board_schools", "value": str(len(merged_rows))},
        {"metric": "master_operating_board_coverage_ratio", "value": f"{len(merged_rows) / TARGET_TOTAL:.4f}"},
    ]
    for lane, count in sorted(lane_counts.items()):
        coverage_rows.append({"metric": f"{lane}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote master operating board for {len(merged_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
