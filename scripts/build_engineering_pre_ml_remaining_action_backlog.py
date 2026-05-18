from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "engineering_tier",
    "gate_status",
    "backlog_lane",
    "backlog_priority",
    "local_only_feasibility",
    "readiness_band",
    "review_lane",
    "review_risk_score",
    "review_focus_flags",
    "pipeline_status",
    "data_completeness",
    "latest_year",
    "reference_year",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "gap_signature",
    "missing_field_flags",
    "blocker_class",
    "resolution_status",
    "plan_source_resolution",
    "score_source_resolution",
    "remaining_local_action",
    "stop_condition",
    "why_not_ml_ready",
    "record_id",
    "source_record_id",
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
    return (
        str(value or "")
        .replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("＋", "+")
        .strip()
    )


def parse_int(value: str) -> int:
    text = normalize_text(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0


def missing_field_flags(gap_signature: str) -> str:
    flags = [
        flag
        for flag in normalize_text(gap_signature).split("|")
        if flag.startswith("missing_") or flag.startswith("not_fresh_")
    ]
    return "|".join(flags) if flags else "none"


def backlog_lane(gate_status: str) -> tuple[str, str]:
    status = normalize_text(gate_status)
    if status == "G2_ready_with_caution_for_review_gate":
        return "B1_review_with_caution", "1"
    if status == "G3_local_gap_fill_needed":
        return "B2_local_gap_fill", "2"
    if status == "G4_blocked_or_manual_route":
        return "B3_blocked_or_manual_boundary", "3"
    return "B9_uncategorized", "9"


def local_only_feasibility(gate_status: str, blocker_class: str) -> str:
    status = normalize_text(gate_status)
    blocker = normalize_text(blocker_class)
    if status in {"G2_ready_with_caution_for_review_gate", "G3_local_gap_fill_needed"}:
        return "local_only_feasible"
    if blocker in {"cached_page_needs_extract", "page_extract_needed"}:
        return "maybe_local_if_cached_page_available"
    if blocker in {"source_gap", "ajax_blocked_403", "form_replay_blocked"}:
        return "not_local_without_original_thread_or_network"
    return "manual_triage_required"


def why_not_ml_ready(row: dict[str, str]) -> str:
    status = normalize_text(row.get("gate_status", ""))
    if status == "G2_ready_with_caution_for_review_gate":
        return "可进入复核闸门，但仍需人工确认可比年份、缺字段和来源精度备注"
    if status == "G3_local_gap_fill_needed":
        return "仍有本地可补关键字段，补完并复核前不进入机器学习"
    if status == "G4_blocked_or_manual_route":
        return "仍在阻塞/人工路线，当前线程不做新增网页、接口或登录态处理"
    return "未归类，不能进入机器学习"


def stop_condition(row: dict[str, str]) -> str:
    status = normalize_text(row.get("gate_status", ""))
    if status == "G2_ready_with_caution_for_review_gate":
        return "人工/GPT复核确认备注充分后，等待明确进入ML指令"
    if status == "G3_local_gap_fill_needed":
        return "字段补齐并重新生成 readiness/workbench/gate status 后进入复核闸门"
    if status == "G4_blocked_or_manual_route":
        return "若必须新增网页、接口、登录态或403解锁，停止并切回原主线程"
    return "等待人工判断"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a prioritized pre-ML remaining action backlog from the gate-status table."
    )
    parser.add_argument(
        "--gate-status",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_gate_status_merged.csv",
        help="Pre-ML gate status CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_remaining_action_backlog_merged.csv",
        help="Output remaining-action backlog CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_remaining_action_backlog_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_remaining_action_backlog_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    gate_rows = read_rows(args.gate_status)

    backlog_rows: list[dict[str, str]] = []
    lane_counts: Counter[str] = Counter()
    feasibility_counts: Counter[str] = Counter()

    for row in gate_rows:
        gate_status = normalize_text(row.get("gate_status", ""))
        if gate_status == "G1_ready_for_human_gpt_review_gate":
            continue

        lane, priority = backlog_lane(gate_status)
        feasibility = local_only_feasibility(gate_status, row.get("blocker_class", ""))
        lane_counts[lane] += 1
        feasibility_counts[feasibility] += 1

        school_key = normalize_text(row.get("school_key", ""))
        backlog_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", school_key)),
                "engineering_tier": normalize_text(row.get("engineering_tier", "")),
                "gate_status": gate_status,
                "backlog_lane": lane,
                "backlog_priority": priority,
                "local_only_feasibility": feasibility,
                "readiness_band": normalize_text(row.get("readiness_band", "")),
                "review_lane": normalize_text(row.get("review_lane", "")),
                "review_risk_score": normalize_text(row.get("review_risk_score", "")),
                "review_focus_flags": normalize_text(row.get("review_focus_flags", "")),
                "pipeline_status": normalize_text(row.get("pipeline_status", "")),
                "data_completeness": normalize_text(row.get("data_completeness", "")),
                "latest_year": normalize_text(row.get("latest_year", "")),
                "reference_year": normalize_text(row.get("reference_year", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": normalize_text(row.get("minimum_rank", "")),
                "trend_available": normalize_text(row.get("trend_available", "")),
                "gap_signature": normalize_text(row.get("gap_signature", "")),
                "missing_field_flags": missing_field_flags(row.get("gap_signature", "")),
                "blocker_class": normalize_text(row.get("blocker_class", "")),
                "resolution_status": normalize_text(row.get("resolution_status", "")),
                "plan_source_resolution": normalize_text(row.get("plan_source_resolution", "")),
                "score_source_resolution": normalize_text(row.get("score_source_resolution", "")),
                "remaining_local_action": normalize_text(row.get("remaining_local_action", "")),
                "stop_condition": stop_condition(row),
                "why_not_ml_ready": why_not_ml_ready(row),
                "record_id": f"{school_key}-pre-ml-remaining-action",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "pre_ml_remaining_action_backlog",
            }
        )

    backlog_rows.sort(
        key=lambda item: (
            parse_int(item["backlog_priority"]),
            item["local_only_feasibility"],
            -parse_int(item["review_risk_score"]),
            item["school_key"],
        )
    )
    write_rows(args.output, backlog_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "backlog_lane": row["backlog_lane"],
            "local_only_feasibility": row["local_only_feasibility"],
            "gate_status": row["gate_status"],
            "missing_field_flags": row["missing_field_flags"],
            "remaining_local_action": row["remaining_local_action"],
        }
        for row in backlog_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "backlog_lane",
            "local_only_feasibility",
            "gate_status",
            "missing_field_flags",
            "remaining_local_action",
        ],
    )

    local_feasible_count = sum(
        1 for row in backlog_rows if row["local_only_feasibility"] == "local_only_feasible"
    )
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "remaining_action_backlog_schools", "value": str(len(backlog_rows))},
        {"metric": "remaining_action_backlog_ratio", "value": f"{len(backlog_rows) / TARGET_TOTAL:.4f}"},
        {"metric": "local_only_feasible_backlog_schools", "value": str(local_feasible_count)},
    ]
    for lane, count in sorted(lane_counts.items()):
        coverage_rows.append({"metric": f"{lane}_schools", "value": str(count)})
    for feasibility, count in sorted(feasibility_counts.items()):
        coverage_rows.append({"metric": f"{feasibility}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote pre-ML remaining action backlog for {len(backlog_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
