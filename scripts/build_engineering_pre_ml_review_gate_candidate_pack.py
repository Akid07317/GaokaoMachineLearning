from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


TARGET_TOTAL = 32
FIELDS = [
    "school_key",
    "school_name",
    "candidate_pack_lane",
    "candidate_pack_priority",
    "manual_acceptance_required",
    "source_layer",
    "gate_status",
    "readiness_band",
    "review_lane",
    "review_risk_score",
    "review_focus_flags",
    "data_completeness",
    "latest_year",
    "reference_year",
    "total_plan_count",
    "minimum_score",
    "minimum_rank",
    "trend_available",
    "trend_signal",
    "gap_signature",
    "resolution_status",
    "plan_source_url",
    "score_source_url",
    "review_gate_action",
    "review_gate_notes",
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


def current_pack_lane(gate_status: str) -> tuple[str, str]:
    status = normalize_text(gate_status)
    if status == "G1_ready_for_human_gpt_review_gate":
        return "C1_current_clean_review_gate", "1"
    if status == "G2_ready_with_caution_for_review_gate":
        return "C2_current_caution_review_gate", "2"
    return "C9_out_of_scope", "9"


def preview_pack_lane(preview_gate_status: str) -> tuple[str, str]:
    status = normalize_text(preview_gate_status)
    if status == "G1_ready_for_human_gpt_review_gate_candidate":
        return "C3_candidate_clean_after_gap_fill_acceptance", "3"
    if status == "G2_ready_with_caution_for_review_gate_candidate":
        return "C4_candidate_caution_after_gap_fill_acceptance", "4"
    return "C9_out_of_scope", "9"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the human/GPT review-gate candidate pack without entering ML."
    )
    parser.add_argument(
        "--gate-status",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_pre_ml_gate_status_merged.csv",
        help="Current pre-ML gate status CSV.",
    )
    parser.add_argument(
        "--gap-fill-impact-preview",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_gap_fill_impact_preview_merged.csv",
        help="Gap-fill impact preview CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data")
        / "engineering_guangxi_seed"
        / "guangxi_pre_ml_review_gate_candidate_pack_merged.csv",
        help="Output review-gate candidate pack CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_candidate_pack_school_summary.csv",
        help="School summary output CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_pre_ml_review_gate_candidate_pack_coverage_rollup.csv",
        help="Coverage rollup output CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    gate_rows = read_rows(args.gate_status)
    preview_rows = read_rows(args.gap_fill_impact_preview)

    output_rows: list[dict[str, str]] = []
    lane_counts: Counter[str] = Counter()
    manual_acceptance_count = 0

    for row in gate_rows:
        if normalize_text(row.get("gate_status", "")) not in {
            "G1_ready_for_human_gpt_review_gate",
            "G2_ready_with_caution_for_review_gate",
        }:
            continue
        lane, priority = current_pack_lane(row.get("gate_status", ""))
        lane_counts[lane] += 1
        school_key = normalize_text(row.get("school_key", ""))
        output_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", school_key)),
                "candidate_pack_lane": lane,
                "candidate_pack_priority": priority,
                "manual_acceptance_required": "false",
                "source_layer": "current_gate_status",
                "gate_status": normalize_text(row.get("gate_status", "")),
                "readiness_band": normalize_text(row.get("readiness_band", "")),
                "review_lane": normalize_text(row.get("review_lane", "")),
                "review_risk_score": normalize_text(row.get("review_risk_score", "")),
                "review_focus_flags": normalize_text(row.get("review_focus_flags", "")),
                "data_completeness": normalize_text(row.get("data_completeness", "")),
                "latest_year": normalize_text(row.get("latest_year", "")),
                "reference_year": normalize_text(row.get("reference_year", "")),
                "total_plan_count": normalize_text(row.get("total_plan_count", "")),
                "minimum_score": normalize_text(row.get("minimum_score", "")),
                "minimum_rank": normalize_text(row.get("minimum_rank", "")),
                "trend_available": normalize_text(row.get("trend_available", "")),
                "trend_signal": normalize_text(row.get("trend_signal", "")),
                "gap_signature": normalize_text(row.get("gap_signature", "")),
                "resolution_status": normalize_text(row.get("resolution_status", "")),
                "plan_source_url": normalize_text(row.get("plan_source_url", "")),
                "score_source_url": normalize_text(row.get("score_source_url", "")),
                "review_gate_action": "进入人工/GPT复核闸门；复核通过前不启动机器学习",
                "review_gate_notes": normalize_text(row.get("remaining_local_action", "")),
                "record_id": f"{school_key}-pre-ml-review-gate-candidate-pack",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "pre_ml_review_gate_candidate_pack",
            }
        )

    for row in preview_rows:
        lane, priority = preview_pack_lane(row.get("preview_gate_status", ""))
        if lane == "C9_out_of_scope":
            continue
        manual_acceptance_count += 1
        lane_counts[lane] += 1
        school_key = normalize_text(row.get("school_key", ""))
        output_rows.append(
            {
                "school_key": school_key,
                "school_name": normalize_text(row.get("school_name", school_key)),
                "candidate_pack_lane": lane,
                "candidate_pack_priority": priority,
                "manual_acceptance_required": "true",
                "source_layer": "gap_fill_impact_preview",
                "gate_status": normalize_text(row.get("preview_gate_status", "")),
                "readiness_band": normalize_text(row.get("preview_readiness_band", "")),
                "review_lane": "",
                "review_risk_score": "",
                "review_focus_flags": normalize_text(row.get("preview_gap_signature", "")),
                "data_completeness": normalize_text(row.get("preview_data_completeness", "")),
                "latest_year": normalize_text(row.get("preview_latest_year", "")),
                "reference_year": normalize_text(row.get("candidate_year", "")),
                "total_plan_count": "",
                "minimum_score": normalize_text(row.get("preview_minimum_score", "")),
                "minimum_rank": normalize_text(row.get("preview_minimum_rank", "")),
                "trend_available": "",
                "trend_signal": "",
                "gap_signature": normalize_text(row.get("preview_gap_signature", "")),
                "resolution_status": "",
                "plan_source_url": "",
                "score_source_url": "",
                "review_gate_action": "先人工接受本地补洞候选，再进入人工/GPT复核闸门；复核通过前不启动机器学习",
                "review_gate_notes": normalize_text(row.get("impact_notes", "")),
                "record_id": f"{school_key}-pre-ml-review-gate-candidate-pack-gap-fill-preview",
                "source_record_id": normalize_text(row.get("record_id", "")),
                "source_slug": "pre_ml_review_gate_candidate_pack",
            }
        )

    output_rows.sort(
        key=lambda row: (
            parse_int(row["candidate_pack_priority"]),
            row["manual_acceptance_required"],
            row["school_key"],
        )
    )
    write_rows(args.output, output_rows, FIELDS)

    school_summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "candidate_pack_lane": row["candidate_pack_lane"],
            "manual_acceptance_required": row["manual_acceptance_required"],
            "gate_status": row["gate_status"],
            "readiness_band": row["readiness_band"],
            "minimum_score": row["minimum_score"],
            "minimum_rank": row["minimum_rank"],
        }
        for row in output_rows
    ]
    write_rows(
        args.school_summary_output,
        school_summary_rows,
        [
            "school_key",
            "school_name",
            "candidate_pack_lane",
            "manual_acceptance_required",
            "gate_status",
            "readiness_band",
            "minimum_score",
            "minimum_rank",
        ],
    )

    coverage_rows = [
        {"metric": "target_pool_schools", "value": str(TARGET_TOTAL)},
        {"metric": "review_gate_candidate_pack_schools", "value": str(len(output_rows))},
        {"metric": "review_gate_candidate_pack_ratio", "value": f"{len(output_rows) / TARGET_TOTAL:.4f}"},
        {"metric": "manual_acceptance_required_schools", "value": str(manual_acceptance_count)},
    ]
    for lane, count in sorted(lane_counts.items()):
        coverage_rows.append({"metric": f"{lane}_schools", "value": str(count)})
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])

    print(f"Wrote pre-ML review-gate candidate pack for {len(output_rows)} schools to {args.output}.")


if __name__ == "__main__":
    main()
