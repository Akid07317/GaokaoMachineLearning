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
    "readiness_band",
    "gate_status",
    "gate_priority",
    "review_lane",
    "review_risk_score",
    "review_focus_flags",
    "pipeline_status",
    "operating_lane",
    "latest_year",
    "reference_year",
    "data_completeness",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "gap_count",
    "gap_signature",
    "blocker_class",
    "backfill_route",
    "plan_source_resolution",
    "score_source_resolution",
    "resolution_status",
    "structured_plan_rows",
    "structured_score_major_rows",
    "structured_score_summary_rows",
    "plan_source_url",
    "score_source_url",
    "remaining_local_action",
    "ml_gate_instruction",
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


def derive_gate_status(readiness_band: str, review_lane: str) -> tuple[str, str]:
    readiness = normalize_text(readiness_band)
    lane = normalize_text(review_lane)
    if readiness == "M1_ready_for_pre_ml_review" and lane == "R1_clean_ready":
        return "G1_ready_for_human_gpt_review_gate", "1"
    if readiness == "M2_comparable_ready_with_note":
        return "G2_ready_with_caution_for_review_gate", "2"
    if readiness == "M3_fill_gaps_then_review":
        return "G3_local_gap_fill_needed", "3"
    if readiness == "M4_blocked_or_manual_route":
        return "G4_blocked_or_manual_route", "4"
    return "G9_uncategorized", "9"


def remaining_local_action(
    gate_status: str,
    readiness_row: dict[str, str],
    gap_row: dict[str, str],
    resolution_row: dict[str, str],
) -> str:
    if gate_status == "G1_ready_for_human_gpt_review_gate":
        return "进入人工/GPT复核闸门，复核通过前不启动机器学习"
    if gate_status == "G2_ready_with_caution_for_review_gate":
        return "带可比年份、来源精度和缺字段备注进入人工/GPT复核，不直入机器学习"
    if gate_status == "G3_local_gap_fill_needed":
        route = normalize_text(gap_row.get("backfill_route", ""))
        if route:
            return route
        gap_signature = normalize_text(gap_row.get("gap_signature", ""))
        if "missing_rank" in gap_signature:
            return "优先用本地已有结构化分数摘要补最低位次"
        if "missing_plan" in gap_signature:
            return "优先用本地已有计划表或摘要补计划数"
        return "继续做本地字段补洞后再进人工/GPT复核"
    followup = normalize_text(resolution_row.get("recommended_followup", ""))
    if followup:
        return followup
    return normalize_text(readiness_row.get("readiness_notes", "")) or "保持在非ML数据整理队列"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a 32-school pre-ML gate status table from local artifacts."
    )
    parser.add_argument(
        "--readiness",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_model_readiness_merged.csv",
        help="Pre-ML readiness CSV.",
    )
    parser.add_argument(
        "--workbench",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_review_workbench_merged.csv",
        help="Pre-ML review workbench CSV.",
    )
    parser.add_argument(
        "--field-gap-matrix",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_primary_field_gap_matrix_merged.csv",
        help="Primary field gap matrix CSV.",
    )
    parser.add_argument(
        "--source-resolution",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_source_resolution_matrix_merged.csv",
        help="Source resolution matrix CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_gate_status_merged.csv",
        help="Output pre-ML gate status CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_gate_status_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_gate_status_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    readiness_rows = read_rows(args.readiness)
    workbench_rows = read_rows(args.workbench)
    gap_rows = read_rows(args.field_gap_matrix)
    resolution_rows = read_rows(args.source_resolution)

    workbench_by_key = {normalize_text(row.get("school_key", "")): row for row in workbench_rows}
    gap_by_key = {normalize_text(row.get("school_key", "")): row for row in gap_rows}
    resolution_by_key = {normalize_text(row.get("school_key", "")): row for row in resolution_rows}

    output_rows: list[dict[str, str]] = []
    gate_counts: Counter[str] = Counter()
    readiness_counts: Counter[str] = Counter()
    resolution_counts: Counter[str] = Counter()

    for readiness_row in readiness_rows:
        school_key = normalize_text(readiness_row.get("school_key", ""))
        if not school_key:
            continue
        workbench_row = workbench_by_key.get(school_key, {})
        gap_row = gap_by_key.get(school_key, {})
        resolution_row = resolution_by_key.get(school_key, {})

        readiness_band = normalize_text(readiness_row.get("readiness_band", ""))
        review_lane = normalize_text(workbench_row.get("review_lane", ""))
        gate_status, gate_priority = derive_gate_status(readiness_band, review_lane)

        gate_counts[gate_status] += 1
        readiness_counts[readiness_band] += 1
        resolution_counts[normalize_text(resolution_row.get("resolution_status", ""))] += 1

        output_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(readiness_row.get("school_name", school_key)),
                "engineering_tier": normalize_text(readiness_row.get("engineering_tier", "")),
                "readiness_band": readiness_band,
                "gate_status": gate_status,
                "gate_priority": gate_priority,
                "review_lane": review_lane,
                "review_risk_score": normalize_text(workbench_row.get("review_risk_score", "")),
                "review_focus_flags": normalize_text(workbench_row.get("review_focus_flags", "")),
                "pipeline_status": normalize_text(readiness_row.get("pipeline_status", "")),
                "operating_lane": normalize_text(readiness_row.get("operating_lane", "")),
                "latest_year": normalize_text(readiness_row.get("latest_year", "")),
                "reference_year": normalize_text(readiness_row.get("reference_year", "")),
                "data_completeness": normalize_text(readiness_row.get("data_completeness", "")),
                "total_plan_count": normalize_text(readiness_row.get("total_plan_count", "")),
                "minimum_score": normalize_text(readiness_row.get("minimum_score", "")),
                "minimum_rank": normalize_text(readiness_row.get("minimum_rank", "")),
                "trend_available": normalize_text(readiness_row.get("trend_available", "")),
                "trend_signal": normalize_text(readiness_row.get("trend_signal", "")),
                "gap_count": normalize_text(gap_row.get("gap_count", "")),
                "gap_signature": normalize_text(gap_row.get("gap_signature", readiness_row.get("critical_gap_signature", ""))),
                "blocker_class": normalize_text(gap_row.get("blocker_class", "")),
                "backfill_route": normalize_text(gap_row.get("backfill_route", "")),
                "plan_source_resolution": normalize_text(resolution_row.get("plan_source_resolution", "")),
                "score_source_resolution": normalize_text(resolution_row.get("score_source_resolution", "")),
                "resolution_status": normalize_text(resolution_row.get("resolution_status", "")),
                "structured_plan_rows": normalize_text(resolution_row.get("structured_plan_rows", "")),
                "structured_score_major_rows": normalize_text(resolution_row.get("structured_score_major_rows", "")),
                "structured_score_summary_rows": normalize_text(resolution_row.get("structured_score_summary_rows", "")),
                "plan_source_url": normalize_text(resolution_row.get("plan_source_url", "")),
                "score_source_url": normalize_text(resolution_row.get("score_source_url", "")),
                "remaining_local_action": remaining_local_action(
                    gate_status,
                    readiness_row,
                    gap_row,
                    resolution_row,
                ),
                "ml_gate_instruction": "只到人工/GPT复核闸门；复核通过前禁止启动机器学习",
                "record_id": f"{school_key}-pre-ml-gate-status",
                "source_record_id": normalize_text(readiness_row.get("record_id", "")),
                "source_slug": "pre_ml_gate_status",
            }
        )

    output_rows.sort(
        key=lambda item: (
            parse_int(item["gate_priority"]),
            -parse_int(item["review_risk_score"]),
            item["engineering_tier"],
            item["school_key"],
        )
    )
    write_rows(args.output, output_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "gate_status": row["gate_status"],
            "gate_priority": row["gate_priority"],
            "readiness_band": row["readiness_band"],
            "review_lane": row["review_lane"],
            "resolution_status": row["resolution_status"],
            "gap_signature": row["gap_signature"],
            "remaining_local_action": row["remaining_local_action"],
        }
        for row in output_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "gate_status",
            "gate_priority",
            "readiness_band",
            "review_lane",
            "resolution_status",
            "gap_signature",
            "remaining_local_action",
        ],
    )

    review_gate_ready = gate_counts["G1_ready_for_human_gpt_review_gate"] + gate_counts[
        "G2_ready_with_caution_for_review_gate"
    ]
    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "pre_ml_gate_status_schools", "value": str(len(output_rows))},
        {"metric": "pre_ml_gate_status_coverage_ratio", "value": f"{len(output_rows) / TARGET_TOTAL:.4f}"},
        {"metric": "human_gpt_review_gate_candidate_schools", "value": str(review_gate_ready)},
        {"metric": "human_gpt_review_gate_candidate_ratio", "value": f"{review_gate_ready / TARGET_TOTAL:.4f}"},
    ]
    for gate_status, count in sorted(gate_counts.items()):
        coverage_rows.append({"metric": f"{gate_status}_schools", "value": str(count)})
    for readiness_band, count in sorted(readiness_counts.items()):
        coverage_rows.append({"metric": f"{readiness_band}_schools", "value": str(count)})
    for resolution_status, count in sorted(resolution_counts.items()):
        coverage_rows.append({"metric": f"{resolution_status or 'unknown'}_source_resolution_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote pre-ML gate status for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
